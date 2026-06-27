'''
    ERP 供应商新增流程 — pytest + POM 模式：
        1. 页面对象封装元素定位与业务操作（LoginPage / VendorPage）
        2. Fixture 管理 driver 作用域与环境切换
        3. YAML 仅存放业务测试数据，不再存放定位信息
        4. 用例层只调用页面对象方法，不直接操作 driver
'''
import allure
import pytest

from conf.yaml_conf import read


@allure.epic('实现供应商信息的添加操作业务流程')
@allure.feature('新增供应商')
@allure.story('基于后台实现对新的供应商进行添加，填写对应数据')
@allure.title('添加供应商')
@allure.description('基于 POM 页面对象与 YAML 业务数据实现供应商新增')
@pytest.mark.parametrize('serve', ['TEST_ENV'], indirect=True)
@pytest.mark.parametrize('login', read('test_data/login.yaml'), indirect=True)
@pytest.mark.parametrize('data', read('test_data/add.yaml'))
def test_add_vendor(vendor_page, serve, login, data):
    vendor_data = data['vendor']
    try:
        with allure.step('1. 新增供应商'):
            vendor_page.add_supplier(vendor_data['name'], vendor_data['tele'])
        with allure.step('2. 等待页面刷新'):
            vendor_page.wait(data.get('wait', 3))
        with allure.step('3. 查询并断言供应商已存在'):
            vendor_page.search(vendor_data['name'])
            vendor_page.assert_text(
                vendor_data['name'],
                'xpath',
                f'//td[contains(text(), "{vendor_data["name"]}")]',
            )
    except Exception:
        allure.attach(vendor_page.get_png(), '报错截图', allure.attachment_type.PNG)
        raise
