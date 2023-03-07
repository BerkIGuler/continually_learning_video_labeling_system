import cfg


def select_class_by_keyboard(key):
    class_to_id = {value: key for (key, value) in cfg.id_to_class.items()}

    try:
        class_name = cfg.key_to_class[key]
        selected_class_id = class_to_id[class_name]
        return selected_class_id
    except KeyError as e:
        print("undefined class", e)
