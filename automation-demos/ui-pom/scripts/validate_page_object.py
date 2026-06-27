"""
页面对象自检脚本：登录后执行业务主流程并断言，供流水线 Step 2 使用。
失败时输出 traceback 并保存截图，exit code 1。
"""
import argparse
import importlib
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from conf.serve_conf import read as read_env
from conf.yaml_conf import read as read_yaml
from page_object.login_page import LoginPage
from utils.browser import open_browser

# 内置页面对象 → (类名, 主流程方法, 业务键, 断言字段)
PAGE_REGISTRY = {
    'depot': ('DepotPage', 'add_depot', 'depot', 'name'),
    'vendor': ('VendorPage', 'add_supplier', 'vendor', 'name'),
    'person': ('PersonPage', 'add_person', 'person', 'name'),
}


def _load_page(page_key, driver, base_url):
    """按模块名动态加载页面对象类。"""
    module = importlib.import_module(f'page_object.{page_key}_page')
    class_name = PAGE_REGISTRY[page_key][0]
    return getattr(module, class_name)(driver, base_url=base_url)


def _call_biz_method(page, page_key, biz_data, cfg):
    """调用页面对象主流程方法。"""
    method_name = cfg.get('method') or PAGE_REGISTRY[page_key][1]
    biz_key = cfg.get('biz_key') or PAGE_REGISTRY[page_key][2]
    data = biz_data[biz_key]
    method = getattr(page, method_name)

    if page_key == 'depot':
        method(
            name=data['name'],
            address=data.get('address', ''),
            warehousing=data.get('warehousing', ''),
            truckage=data.get('truckage', ''),
            principal=data.get('principal', ''),
            sort=data.get('sort', ''),
            remark=data.get('remark', ''),
        )
    elif page_key == 'vendor':
        method(data['name'], data['tele'])
    elif page_key == 'person':
        method(
            name=data['name'],
            person_type=data['type'],
            sort=data.get('sort', ''),
        )
    else:
        method(**{k: v for k, v in data.items() if k != 'wait'})


def _assert_result(page, page_key, biz_data, cfg):
    """查询并断言关键字段出现在列表中。"""
    biz_key = cfg.get('biz_key') or PAGE_REGISTRY[page_key][2]
    assert_field = cfg.get('assert_field') or PAGE_REGISTRY[page_key][3]
    data = biz_data[biz_key]
    value = data[assert_field]

    if hasattr(page, 'search'):
        if page_key == 'depot':
            page.search(name=value)
        elif page_key == 'vendor':
            page.search(value)
        elif page_key == 'person':
            page.search(name=value)

    xpath = cfg.get('assert_xpath') or f'//td[contains(text(), "{value}")]'
    page.assert_text(value, 'xpath', xpath)


def main():
    """执行页面对象自检主入口。"""
    parser = argparse.ArgumentParser(description='POM 页面对象自检')
    parser.add_argument('--page', required=True, help='页面对象模块名，如 depot')
    parser.add_argument('--data', required=True, help='校验 YAML 路径，如 test_data/validate/depot.yaml')
    parser.add_argument('--env', default='TEST_ENV', help='server_conf.ini 环境节名')
    args = parser.parse_args()

    page_key = args.page.lower()
    if page_key not in PAGE_REGISTRY:
        print(f'[ERROR] 未注册页面对象: {page_key}，请在 PAGE_REGISTRY 中添加映射')
        sys.exit(1)

    data_path = Path(args.data)
    if not data_path.is_absolute():
        data_path = ROOT / data_path
    if not data_path.exists():
        print(f'[ERROR] 校验数据文件不存在: {data_path}')
        sys.exit(1)

    payload = read_yaml(str(data_path.relative_to(ROOT)))[0]
    cfg = payload.get('validate', {})
    biz_data = {k: v for k, v in payload.items() if k not in ('wait', 'validate')}
    login_data = read_yaml('test_data/login.yaml')[0]
    base_url = read_env(args.env)['url']

    driver = open_browser('Chrome')
    screenshot = ROOT / 'log' / f'validate_{page_key}_error.png'
    try:
        print(f'[1/4] 登录 ({args.env})...')
        login_page = LoginPage(driver, base_url=base_url)
        login_page.login(login_data['user'], login_data['pwd'], login_data.get('wait', 2))

        print(f'[2/4] 加载页面对象 {page_key}_page...')
        page = _load_page(page_key, driver, base_url)

        print(f'[3/4] 执行业务主流程...')
        _call_biz_method(page, page_key, biz_data, cfg)
        page.wait(payload.get('wait', 3))

        print(f'[4/4] 查询并断言...')
        _assert_result(page, page_key, biz_data, cfg)
        print('页面对象自检通过')
    except Exception:
        print('页面对象自检失败，错误信息如下：')
        traceback.print_exc()
        try:
            screenshot.write_bytes(driver.get_screenshot_as_png())
            print(f'截图已保存: {screenshot}')
        except Exception:
            pass
        sys.exit(1)
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
