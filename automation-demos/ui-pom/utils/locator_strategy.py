"""定位器自愈策略：id → name → css → 相对 xpath，过滤动态属性。"""
import re

# 优先级数值越小越优先
PRIORITY_ID = 1
PRIORITY_NAME = 2
PRIORITY_CSS = 3
PRIORITY_REL_XPATH = 4

# 禁止使用的动态/不稳定特征
DYNAMIC_ATTR_PATTERNS = (
    r'data-v-[a-f0-9]+',
    r'data-__\w+',
    r'aria-controls="[a-f0-9-]{20,}"',
)
DYNAMIC_ID_PATTERNS = (
    r'^[a-f0-9]{8}-[a-f0-9-]{27,}$',  # UUID
    r'^[a-f0-9]{32,}$',
    r'^rcDialogTitle\d+$',
    r'^react-',
)
BLACKLIST_IDS = frozenset({'app', 'root', 'nprogress', 'webpack'})

# 稳定容器（相对 xpath 锚点）
STABLE_CONTAINERS = (
    ('form', 'personModal'),
    ('form', 'depotModal'),
    ('div', 'ant-modal-footer'),
    ('div', 'ant-popover-buttons'),
    ('div', 'table-operator'),
    ('div', 'table-page-search-wrapper'),
)


def is_dynamic_value(value):
    """判断定位值是否包含动态/不稳定特征。"""
    if not value:
        return True
    for pat in DYNAMIC_ATTR_PATTERNS:
        if re.search(pat, value):
            return True
    if 'data-v-' in value:
        return True
    return False


def is_stable_id(el_id):
    """判断 id 是否稳定可用。"""
    if not el_id or el_id in BLACKLIST_IDS:
        return False
    for pat in DYNAMIC_ID_PATTERNS:
        if re.match(pat, el_id, re.I):
            return False
    return bool(re.match(r'^[a-zA-Z][\w-]*$', el_id))


def is_stable_name(name):
    """判断 name 是否稳定可用。"""
    if not name or is_dynamic_value(name):
        return False
    return bool(re.match(r'^[a-zA-Z][\w-]*$', name))


def _rel_xpath(container_tag, container_hint, inner_xpath):
    """生成基于稳定容器的相对 xpath。"""
    if container_tag == 'form':
        anchor = f'//form[@id="{container_hint}"]'
    else:
        anchor = f'//div[contains(@class,"{container_hint}")]'
    return f'{anchor}{inner_xpath}'


def _candidates_from_clue(text, tag='input'):
    """从 placeholder/label 文本线索生成相对 xpath 候选。"""
    if not text or is_dynamic_value(text):
        return []
    escaped = text.replace('"', '\\"')
    items = []
    for ctag, chint in STABLE_CONTAINERS:
        if ctag == 'form':
            inner = f'//{tag}[@placeholder="{escaped}"]'
        else:
            inner = f'//{tag}[@placeholder="{escaped}"]'
        items.append((
            PRIORITY_REL_XPATH,
            'xpath',
            _rel_xpath(ctag, chint, inner),
        ))
    items.append((
        PRIORITY_REL_XPATH,
        'xpath',
        f'//label[contains(.,"{escaped}")]/following-sibling::div//{tag}',
    ))
    items.append((
        PRIORITY_REL_XPATH,
        'xpath',
        f'//{tag}[@placeholder="{escaped}"]',
    ))
    return items


def suggest_locators(page_source, original_by='', original_value=''):
    """
    从 DOM 源码推断候选定位器，按 id → name → css → 相对 xpath 排序。
    返回 [(by, value), ...] 已去重且排除动态方案。
    """
    ranked = []

    # --- 1) id（最高优先级）---
    for el_id in re.findall(r'\bid="([^"]+)"', page_source):
        if is_stable_id(el_id):
            ranked.append((PRIORITY_ID, 'id', el_id))
            for ctag, chint in STABLE_CONTAINERS:
                if ctag == 'form':
                    ranked.append((
                        PRIORITY_ID,
                        'xpath',
                        _rel_xpath('form', chint, f'//*[@id="{el_id}"]'),
                    ))

    # --- 2) name ---
    for name in re.findall(r'\bname="([^"]+)"', page_source):
        if is_stable_name(name):
            ranked.append((PRIORITY_NAME, 'name', name))

    # --- 3) css selector（稳定 class，禁止 data-v）---
    stable_css = [
        ('css selector', '#type .ant-select-selection'),
        ('css selector', '#principal .ant-select-selection'),
        ('css selector', '#name'),
        ('css selector', '#sort'),
        ('css selector', '.table-page-search-wrapper .ant-select-selection'),
        ('css selector', '.table-operator button.ant-btn-primary'),
    ]
    for by, val in stable_css:
        if is_dynamic_value(val):
            continue
        anchor = val.split()[0].lstrip('#.')
        if anchor in page_source or val.split()[0] in page_source:
            ranked.append((PRIORITY_CSS, by, val))

    # --- 4) 相对 xpath（锚定稳定容器 + 语义属性）---
    rel_xpaths = [
        ('//div[contains(@class,"ant-popover-buttons")]//button[contains(@class,"ant-btn-primary")]'),
        ('//div[contains(@class,"ant-modal-footer")]//button[contains(@class,"ant-btn-primary")]'),
        ('//div[@class="ant-modal-confirm-btns"]/button[2]'),
        ('//div[@class="table-operator"]/button[1]'),
        ('//span[contains(text(),"查询")]/..'),
        ('//span[contains(text(),"重置")]/..'),
    ]
    for xp in rel_xpaths:
        if not is_dynamic_value(xp):
            ranked.append((PRIORITY_REL_XPATH, 'xpath', xp))

    # placeholder / label 线索（来自原始定位或 DOM）
    clues = set(re.findall(r'placeholder="([^"]+)"', page_source))
    for pat in (
        r'placeholder="([^"]+)"',
        r'contains\(text\(\),\s*"([^"]+)"\)',
        r'contains\(\.\,"([^"]+)"\)',
    ):
        m = re.search(pat, original_value or '')
        if m:
            clues.add(m.group(1))

    for clue in clues:
        for item in _candidates_from_clue(clue, 'input'):
            ranked.append(item)
        for item in _candidates_from_clue(clue, 'textarea'):
            ranked.append(item)

    # label[@for] → id 关联相对 xpath
    for label_for in re.findall(
        r'<label[^>]+for="([^"]+)"[^>]*title="([^"]+)"', page_source,
    ):
        fid, title = label_for
        if is_stable_id(fid):
            ranked.append((
                PRIORITY_REL_XPATH,
                'xpath',
                f'//label[@for="{fid}"]/following-sibling::div//input',
            ))
            ranked.append((
                PRIORITY_REL_XPATH,
                'xpath',
                f'//label[contains(.,"{title}")]/following-sibling::div//input',
            ))

    # 排序、去重、过滤动态 & 原始重复
    ranked.sort(key=lambda x: x[0])
    seen = set()
    result = []
    original = (original_by, original_value)
    for _prio, by, val in ranked:
        if is_dynamic_value(val):
            continue
        sig = (by, val)
        if sig in seen or sig == original:
            continue
        seen.add(sig)
        result.append(sig)
    return result
