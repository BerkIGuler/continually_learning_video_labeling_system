import os
import yaml


id_to_class = None
id_to_color = None
key_to_class = None
config = None


def init_yaml_config(cfg: dict):
    for key, value in cfg.items():
        try:
            if value.lower() == "none":
                cfg[key] = None
        except AttributeError:
            continue
    return cfg


def init_yaml_color_list(cfg: dict):
    for key, value in cfg.items():
        value = value[1:-1]
        cfg[key] = tuple([int(val) for val in value.split(", ")])
    return cfg


def init_key_to_class(cfg: dict):
    new_cfg = {}
    for key, value in cfg.items():
        new_cfg[ord(str(key))] = cfg[key]
    return new_cfg


def init_config():
    global config, id_to_class, id_to_color, key_to_class

    cwd = os.getcwd()
    config_dir = os.path.join(cwd, "config_files")

    config_path = os.path.join(config_dir, "config.yaml")
    with open(config_path, "r") as f_in:
        config = init_yaml_config(yaml.safe_load(f_in))

    colors_path = os.path.join(config_dir, config["ID_TO_COLOR_CFG"])
    class_path = os.path.join(config_dir, config["ID_TO_CLASS_CFG"])
    key_to_class_path = os.path.join(config_dir, config["KEY_TO_CLASS_CFG"])

    with open(colors_path, "r") as f_in:
        id_to_color = init_yaml_color_list(yaml.safe_load(f_in))

    with open(class_path, "r") as f_in:
        id_to_class = yaml.safe_load(f_in)

    with open(key_to_class_path, "r") as f_in:
        key_to_class = init_key_to_class(yaml.safe_load(f_in))

    os.makedirs(config["FRAMES_DIR"], exist_ok=True)
    os.makedirs(config["LABELS_DIR"], exist_ok=True)
    os.makedirs(config["VIDEO_DIR"], exist_ok=True)
    os.makedirs(config["ORIGINAL_DIR"], exist_ok=True)
    os.makedirs(config["ANNOTATED_FRAMES_DIR"], exist_ok=True)
    os.makedirs(config["EDITED_LABELS_DIR"], exist_ok=True)


# for testing only
if __name__ == "__main__":
    init_config()
    print(key_to_class)