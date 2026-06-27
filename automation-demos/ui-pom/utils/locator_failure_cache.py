"""元素定位失败缓存：记录已失败的定位方案，避免重复尝试。"""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
CACHE_FILE = ROOT / 'log' / 'locator_failure_cache.json'


def _load():
    """读取失败缓存文件。"""
    if not CACHE_FILE.exists():
        return {'failures': []}
    with open(CACHE_FILE, encoding='utf-8') as f:
        return json.load(f)


def _save(data):
    """写入失败缓存文件。"""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _entry_key(page_class, locator_key, by, value):
    """生成缓存条目唯一键。"""
    return f'{page_class}::{locator_key}::{by}::{value}'


def _global_pattern_match(item, by, value):
    """全局失败条目：精确匹配或花括号占位模板匹配。"""
    if item.get('page') != '__global__' or item.get('by') != by:
        return False
    gv = item.get('value', '')
    if gv == value:
        return True
    if '{' not in gv:
        return False
    prefix, rest = gv.split('{', 1)
    suffix = rest.split('}', 1)[-1] if '}' in rest else ''
    return value.startswith(prefix) and value.endswith(suffix)


def is_failed(page_class, locator_key, by, value):
    """判断该定位方案是否已在失败缓存中（含全局已知失败方案）。"""
    key = _entry_key(page_class, locator_key, by, value)
    data = _load()
    for item in data['failures']:
        if item.get('cache_key') == key:
            return True
        if _global_pattern_match(item, by, value):
            return True
    return False


def record_failure(page_class, locator_key, by, value, error_msg, snapshot=''):
    """将失败的定位方案写入缓存。"""
    data = _load()
    cache_key = _entry_key(page_class, locator_key, by, value)
    if any(item.get('cache_key') == cache_key for item in data['failures']):
        return
    data['failures'].append({
        'cache_key': cache_key,
        'page': page_class,
        'locator_key': locator_key,
        'by': by,
        'value': value,
        'error': error_msg[:500],
        'snapshot': snapshot,
        'at': datetime.now().isoformat(timespec='seconds'),
    })
    _save(data)


def list_failures(page_class=''):
    """列出失败缓存，可按页面对象类名过滤。"""
    data = _load()
    items = data.get('failures', [])
    if page_class:
        items = [i for i in items if i.get('page') == page_class]
    return items
