'''
  ERP 系统 —— 用户登录 & 信息获取接口测试

  测试链路：
    1. 登录 → 提取 token → 写入 ini 缓存
    2. 获取用户信息 → 断言关键字段
    3. token 自动注入后续请求头
    4. 用例结束后清空 token（clear_token fixture）

  运行方式：
    cd api-keyword/test_cases
    pytest test_erp_user.py -sv
    pytest test_erp_user.py -sv --alluredir=allure_data
'''

import allure
import pytest

from conf.config_loader import load_yaml, write_conf


# ===========================
#  用例 1：登录并提取 token
# ===========================

@allure.epic('ERP 用户管理')
@allure.feature('用户登录 → 获取信息 业务流程')
@allure.story('用户登录')
@allure.title('test_login — 登录成功后提取 token')
@allure.step('步骤：发送登录请求 → 提取 token → 写入缓存')
@pytest.mark.parametrize('set_env', ['Test_Env'], indirect=True)
@pytest.mark.parametrize('data', load_yaml('../test_data/erp_login.yaml'))
def test_login(api, set_env, data):
    with allure.step('1. 调用登录接口'):
        res = api.request(**data['login'])

    with allure.step('2. 校验 HTTP 状态码'):
        assert res.status_code == 200, f'登录失败，状态码: {res.status_code}'

    with allure.step('3. 提取 token 并写入缓存'):
        token = api.get_text(res.json(), 'token')
        assert token, '❌ 未提取到 token，登录可能失败'
        write_conf('data', 'token', token)
        allure.attach(str(token), 'Token', allure.attachment_type.TEXT)


# ===========================
#  用例 2：获取用户信息并断言
# ===========================

@allure.epic('ERP 用户管理')
@allure.feature('用户登录 → 获取信息 业务流程')
@allure.story('获取用户信息')
@allure.title('test_user_info — 获取用户信息并校验关键字段')
@allure.step('步骤：请求用户信息 → 断言 username / role 等字段')
@pytest.mark.parametrize('data', load_yaml('../test_data/erp_login.yaml'))
def test_user_info(api, data, clear_token):
    with allure.step('1. 发送获取用户信息请求（token 自动注入）'):
        res = api.request(**data['userInfo'])

    with allure.step('2. 校验 HTTP 状态码'):
        assert res.status_code == 200, f'获取用户信息失败，状态码: {res.status_code}'

    with allure.step('3. 断言关键字段'):
        resp_json = res.json()
        api.assert_equal(data['expect']['username'], resp_json, 'username')
        api.assert_equal(data['expect']['role'], resp_json, 'role')

    with allure.step('4. 记录完整响应（用于报告追溯）'):
        allure.attach(str(res.json()), 'UserInfo Response', allure.attachment_type.JSON)
