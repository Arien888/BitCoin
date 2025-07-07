import yaml
import os

def load_config(filename="config.yaml"):
    # main.pyから1つ上のディレクトリを基準に絶対パスを作成
    base_dir = os.path.dirname(os.path.abspath(__file__))    # load_config.py の場所
    parent_dir = os.path.dirname(base_dir)                   # 1つ上の階層
    config_path = os.path.join(parent_dir, filename)

    with open(config_path, "r") as f:
        return yaml.safe_load(f)
