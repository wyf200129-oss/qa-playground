'''
===========================================================
  API 关键字驱动客户端 —— ERP 接口自动化测试框架
===========================================================
设计思路：
  1. 统一封装 HTTP 请求方法，支持 GET / POST / PUT / DELETE
  2. 基于 ini 配置文件一键切换测试环境（Test / Dev / Staging）
  3. JSONPath 提取响应数据，实现接口间数据关联（如 token 传递）
  4. 请求头自动拼接：基础 headers + 用户自定义 + token 自动注入
  5. 断言校验：预期值 vs 实际值，错误信息友好可读
'''

import jsonpath
import requests

from conf.config_loader import read_conf


class ApiClient:
    """API 关键字驱动客户端"""

    def __init__(self):
        self.env = None  # 当前环境标识，需调用 set_env() 设置

    def set_env(self, env: str):
        """切换测试环境，对应 server.ini 中的 [section]"""
        self.env = env

    # ===========================
    #  核心请求方法
    # ===========================

    def request(self, method: str, path: str = None, headers: dict = None, **kwargs):
        """
        统一的 HTTP 请求入口。

        :param method:  请求方法 (get / post / put / delete)
        :param path:    接口路径（不含域名），如 /user_services/login
        :param headers: 额外请求头，会自动合并到基础 headers
        :param kwargs:  其他 requests 参数 (json / params / data 等)
        :return:        requests.Response 对象
        """
        url = self._build_url(path)
        merged_headers = self._build_headers(headers)
        return requests.request(method=method, url=url, headers=merged_headers, **kwargs)

    def _build_url(self, path: str) -> str:
        """拼接完整 URL：从 ini 读取 host + 接口路径"""
        host = read_conf(self.env, 'host')
        if path:
            return host.rstrip('/') + path
        return host

    def _build_headers(self, extra_headers: dict = None) -> dict:
        """构建请求头：基础 UA + 自定义 headers + 已保存的 token"""
        base = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/135.0.0.0 Safari/537.36'
            )
        }
        if extra_headers:
            base.update(extra_headers)

        # 若 token 已通过前置用例写入 ini，则自动注入 Authorization
        saved_token = read_conf('data', 'token')
        if saved_token:
            base['Authorization'] = saved_token
        return base

    # ===========================
    #  数据提取 & 断言
    # ===========================

    def get_text(self, response_json: dict, key: str):
        """
        通过 JSONPath 从响应 JSON 中提取字段值。
        若只匹配到 1 个结果则直接返回值，否则返回列表。
        """
        values = jsonpath.jsonpath(response_json, f'$..{key}')
        if values:
            if len(values) == 1:
                return values[0]
            return values
        return None

    def assert_equal(self, expected, response_json: dict, key: str):
        """
        断言响应中某个字段的实际值是否等于预期值。
        失败时输出详细对比信息。
        """
        actual = self.get_text(response_json, key)
        assert expected == actual, (
            f'❌ 断言失败\n'
            f'  预期值：{expected}\n'
            f'  实际值：{actual}\n'
            f'  关系：{expected} ≠ {actual}'
        )
