"""
测试数据幂等工具：递增 YAML 中不可重复字段，避免重复执行失败。
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent.resolve()


def _get_nested(data, dotted_key):
    """按 depot.name 形式读取嵌套值。"""
    keys = dotted_key.split('.')
    node = data
    for key in keys:
        node = node[key]
    return node, keys


def _set_nested(data, keys, value):
    """按键路径写入嵌套值。"""
    node = data
    for key in keys[:-1]:
        node = node[key]
    node[keys[-1]] = value


def bump_suffix(value):
    """末尾数字 +1；无数字则追加 01。"""
    text = str(value)
    match = re.search(r'(\d+)$', text)
    if match:
        num = int(match.group(1)) + 1
        return text[: match.start(1)] + str(num).zfill(len(match.group(1)))
    return f'{text}01'


def bump_timestamp(value):
    """追加时间戳后缀（保留原值前缀）。"""
    stamp = datetime.now().strftime('%m%d%H%M')
    text = str(value)
    base = re.sub(r'\d{10,}$', '', text).rstrip('_')
    return f'{base}{stamp}'


def main():
    """递增 YAML 指定字段并写回文件。"""
    parser = argparse.ArgumentParser(description='测试数据幂等递增')
    parser.add_argument('--file', required=True, help='YAML 路径，如 test_data/depot.yaml')
    parser.add_argument('--fields', required=True, help='逗号分隔字段，如 depot.name')
    parser.add_argument(
        '--strategy',
        choices=['suffix', 'timestamp'],
        default='suffix',
        help='suffix=末尾数字+1；timestamp=追加时间戳',
    )
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.is_absolute():
        file_path = ROOT / file_path
    if not file_path.exists():
        print(f'[ERROR] 文件不存在: {file_path}')
        sys.exit(1)

    with open(file_path, encoding='utf-8') as f:
        records = yaml.safe_load(f)

    bump_fn = bump_suffix if args.strategy == 'suffix' else bump_timestamp
    for field in args.fields.split(','):
        field = field.strip()
        for record in records:
            old_value, keys = _get_nested(record, field)
            new_value = bump_fn(old_value)
            _set_nested(record, keys, new_value)
            print(f'{field}: {old_value!r} -> {new_value!r}')

    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(records, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f'已更新: {file_path}')


if __name__ == '__main__':
    main()
