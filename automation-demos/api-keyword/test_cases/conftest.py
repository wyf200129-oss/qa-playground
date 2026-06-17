'''
  pytest 全局 Fixture 定义
'''
import pytest

from api_client import ApiClient
from conf.config_loader import write_conf


@pytest.fixture(scope='session')
def api():
    """
    session 级别的 API 客户端单例。
    整个测试会话共享同一个 api 对象，
    方便 token 等数据在不同用例之间传递。
    """
    client = ApiClient()
    return client


@pytest.fixture(scope='function')
def set_env(request, api):
    """
    通过 pytest.mark.parametrize(indirect=True) 注入环境名，
    实现不同用例跑不同环境。
    用法：
        @pytest.mark.parametrize('set_env', ['Test_Env'], indirect=True)
    """
    env = request.param
    api.set_env(env)


@pytest.fixture(scope='function')
def clear_token(request):
    """用例结束后自动清空 ini 中缓存的 token，避免脏数据影响后续用例"""
    def _cleanup():
        write_conf('data', 'token', '')
    request.addfinalizer(_cleanup)
