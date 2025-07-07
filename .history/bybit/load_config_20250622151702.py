import yaml

def load_config(filepath="config.yaml"):
    with open(filepath, "r") as f:
        return yaml.safe_load(f)
