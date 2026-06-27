"""元素定位失败修复：保存 DOM 源码、按策略推断候选定位器、最多尝试 3 次。"""
import re
import traceback
from datetime import datetime
from pathlib import Path

from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

from utils.locator_failure_cache import is_failed, record_failure
from utils.locator_strategy import is_dynamic_value, suggest_locators

ROOT = Path(__file__).parent.parent.resolve()
SNAPSHOT_DIR = ROOT / 'log' / 'dom_snapshots'
MAX_REPAIR_ATTEMPTS = 3
IMPLICIT_WAIT = 10


def is_element_error(exc):
    """判断异常是否由元素定位失败引起。"""
    if isinstance(exc, (NoSuchElementException, TimeoutException)):
        return True
    if isinstance(exc, WebDriverException):
        msg = str(exc).lower()
        return any(k in msg for k in ('no such element', 'unable to locate element', 'timeout'))
    return False


def save_dom_snapshot(driver, page_class, locator_key):
    """保存当前页面 DOM 源码，供定位推断使用。"""
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_key = re.sub(r'[^\w\-]', '_', locator_key or 'unknown')
    path = SNAPSHOT_DIR / f'{page_class}_{safe_key}_{stamp}.html'
    path.write_text(driver.page_source, encoding='utf-8')
    return str(path)


def _reject_dynamic_locator(by, value):
    """原始定位器含动态特征时不尝试，直接进入策略推断。"""
    return is_dynamic_value(value) or 'data-v-' in value


def find_element_with_repair(driver, page_class, locator_key, by, value):
    """
    定位元素；失败时保存 DOM、查缓存、按 id→name→css→相对xpath 推断备选，最多 3 次。
    非元素类异常直接抛出，不进行修复。
    """
    locator_key = locator_key or f'{by}:{value[:60]}'
    snapshot_path = ''
    last_errors = []
    tried = 0

    def _try_find(try_by, try_value, label):
        nonlocal snapshot_path, tried
        if tried >= MAX_REPAIR_ATTEMPTS:
            return None
        if is_failed(page_class, locator_key, try_by, try_value):
            last_errors.append(f'[{label}] 跳过缓存失败方案 ({try_by}, {try_value!r})')
            return None
        if is_dynamic_value(try_value):
            last_errors.append(f'[{label}] 跳过动态定位方案 ({try_by}, {try_value!r})')
            return None
        tried += 1
        driver.implicitly_wait(2)
        try:
            return driver.find_element(try_by, try_value)
        except Exception as exc:
            if not is_element_error(exc):
                raise
            if not snapshot_path:
                snapshot_path = save_dom_snapshot(driver, page_class, locator_key)
            record_failure(
                page_class, locator_key, try_by, try_value,
                str(exc), snapshot_path,
            )
            last_errors.append(f'[{label}] ({try_by}, {try_value!r}) -> {exc}')
            return None
        finally:
            driver.implicitly_wait(IMPLICIT_WAIT)

    # 原始方案（非动态且未在失败缓存中）
    if not _reject_dynamic_locator(by, value) and not is_failed(page_class, locator_key, by, value):
        el = _try_find(by, value, 'original')
        if el is not None:
            return el
    elif _reject_dynamic_locator(by, value):
        last_errors.append(f'[original] 跳过含动态属性的原始方案 ({by}, {value!r})')

    # 基于 DOM 按优先级推断：id → name → css → 相对 xpath
    if not snapshot_path:
        snapshot_path = save_dom_snapshot(driver, page_class, locator_key)
    html = Path(snapshot_path).read_text(encoding='utf-8')
    for try_by, try_value in suggest_locators(html, by, value):
        if tried >= MAX_REPAIR_ATTEMPTS:
            break
        el = _try_find(try_by, try_value, 'strategy')
        if el is not None:
            return el

    detail = '\n'.join(last_errors) if last_errors else '无有效尝试'
    raise NoSuchElementException(
        f'元素定位失败（已尝试 {tried} 次，上限 {MAX_REPAIR_ATTEMPTS}）。\n'
        f'策略优先级: id → name → css selector → 相对 xpath\n'
        f'页面对象: {page_class}, 定位键: {locator_key}\n'
        f'原始方案: ({by}, {value!r})\n'
        f'DOM 快照: {snapshot_path or "无"}\n'
        f'失败缓存: log/locator_failure_cache.json\n'
        f'尝试记录:\n{detail}'
    )


def format_repair_error(exc):
    """格式化修复失败后的报错信息。"""
    return ''.join(traceback.format_exception_only(type(exc), exc)).strip()
