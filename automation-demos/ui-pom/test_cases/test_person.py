"""
经手人新增流程 — pytest + POM 模式：
    1. 页面对象封装元素定位与业务操作（LoginPage / PersonPage）
    2. Fixture 管理 driver 作用域与环境切换
    3. YAML 仅存放业务测试数据，不再存放定位信息
    4. 用例层只调用页面对象方法，不直接操作 driver
"""
import allure
import pytest

from conf.yaml_conf import read


@allure.epic('基础资料')
@allure.feature('经手人管理')
@allure.story('后台新增并删除经手人')
@allure.title('添加经手人并删除验证')
@allure.description('登录后新增经手人，查询断言存在，删除后查询断言已不存在')
@pytest.mark.parametrize('serve', ['TEST_ENV'], indirect=True)
@pytest.mark.parametrize('login', read('test_data/login.yaml'), indirect=True)
@pytest.mark.parametrize('data', read('test_data/person.yaml'))
def test_add_person(person_page, serve, login, data):
    """经手人流程：登录 → 新增 → 断言存在 → 删除 → 断言已删除。"""
    person_data = data['person']
    name = person_data['name']
    try:
        with allure.step('1. 新增经手人'):
            person_page.add_person(
                name=name,
                person_type=person_data['type'],
                sort=person_data.get('sort', ''),
            )
        with allure.step('2. 等待页面刷新'):
            person_page.wait(data.get('wait', 3))
        with allure.step('3. 查询并断言经手人已存在'):
            person_page.search(name=name)
            person_page.assert_text(
                name,
                'xpath',
                f'//td[contains(text(), "{name}")]',
            )
        with allure.step('4. 删除刚创建的经手人'):
            person_page.delete_person(name)
            person_page.wait(data.get('wait', 3))
        with allure.step('5. 查询并断言经手人已删除'):
            person_page.assert_person_not_exists(name)
    except Exception:
        allure.attach(person_page.get_png(), '报错截图', allure.attachment_type.PNG)
        raise
