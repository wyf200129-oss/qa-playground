"""
仓库信息新增流程 — pytest + POM 模式：
    1. 页面对象封装元素定位与业务操作（LoginPage / DepotPage）
    2. Fixture 管理 driver 作用域与环境切换
    3. YAML 仅存放业务测试数据，不再存放定位信息
    4. 用例层只调用页面对象方法，不直接操作 driver
"""
import allure
import pytest

from conf.yaml_conf import read


@allure.epic('基础资料')
@allure.feature('仓库信息')
@allure.story('后台新增仓库')
@allure.title('添加仓库')
@allure.description('登录后进入仓库信息页，基于 POM 页面对象与 YAML 业务数据实现仓库新增')
@pytest.mark.parametrize('serve', ['TEST_ENV'], indirect=True)
@pytest.mark.parametrize('login', read('test_data/login.yaml'), indirect=True)
@pytest.mark.parametrize('data', read('test_data/depot.yaml'))
def test_add_depot(depot_page, serve, login, data):
    """仓库新增业务流程：登录 → 新增仓库 → 查询并断言列表中存在。"""
    depot_data = data['depot']
    try:
        with allure.step('1. 新增仓库'):
            depot_page.add_depot(
                name=depot_data['name'],
                address=depot_data.get('address', ''),
                warehousing=depot_data.get('warehousing', ''),
                truckage=depot_data.get('truckage', ''),
                principal=depot_data.get('principal', ''),
                sort=depot_data.get('sort', ''),
                remark=depot_data.get('remark', ''),
            )
        with allure.step('2. 等待页面刷新'):
            depot_page.wait(data.get('wait', 3))
        with allure.step('3. 查询并断言仓库已存在'):
            depot_page.search(name=depot_data['name'])
            depot_page.assert_text(
                depot_data['name'],
                'xpath',
                f'//td[contains(text(), "{depot_data["name"]}")]',
            )
    except Exception:
        allure.attach(depot_page.get_png(), '报错截图', allure.attachment_type.PNG)
        raise
