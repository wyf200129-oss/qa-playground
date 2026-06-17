'''
  ini 配置文件读写 + YAML 测试数据加载
'''
import configparser
import pathlib

import yaml

# server.ini 绝对路径（与当前文件同级）
_FILE = pathlib.Path(__file__).parent.resolve() / 'server.ini'
_conf = configparser.ConfigParser()


def read_conf(section: str, option: str) -> str:
    """读取 ini 配置项，不存在时返回空字符串"""
    _conf.read(_FILE)
    try:
        return _conf.get(section=section, option=option)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return ''


def write_conf(section: str, option: str, value: str):
    """写入/更新 ini 配置项"""
    _conf.read(_FILE)
    if not _conf.has_section(section):
        _conf.add_section(section)
    _conf.set(section, option, value)
    with open(_FILE, 'w') as f:
        _conf.write(f)


def load_yaml(file_path: str) -> list:
    """加载 YAML 测试数据文件，返回列表（兼容 pytest parametrize）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
