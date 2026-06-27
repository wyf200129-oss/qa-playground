import pathlib

import yaml

ROOT = pathlib.Path(__file__).parents[1].resolve()


def read(file):
    path = ROOT / file if not pathlib.Path(file).is_absolute() else pathlib.Path(file)
    with open(path, mode='r', encoding='utf-8') as f:
        values = yaml.safe_load(f)
    return values
