import os
import cv2

import cfg
import anno


def select_class_by_keyboard(key):
    class_to_id = {value: key for (key, value) in cfg.id_to_class.items()}

    try:
        class_name = cfg.key_to_class[key]
        selected_class_id = class_to_id[class_name]
        return selected_class_id
    except KeyError:
        return None


def init_frame_counters(anno_frames_path, labels_path):
    initial_anno_frame_count = sum([1 for file in
                                    os.listdir(anno_frames_path)
                                    if file.endswith(".jpg")
    ])

    initial_label_count = sum([1 for file in
                                    os.listdir(labels_path)
                                    if file.endswith(".txt")
    ])

    assert initial_label_count == initial_anno_frame_count
    return initial_label_count, 0


def save_labels(
        boxes,
        frame_id,
        im,
        vid_name,
        anno_im_dir=None,
        anno_labels_dir=None,
        raw_im_dir=None,
        raw_labels_dir=None,
):

    new_label = 0
    if cfg.config["SAVE_EDITED_FRAMES"] and anno_im_dir:
        cv2.imwrite(f"{anno_im_dir}/{vid_name}_{frame_id}.jpg", im)
        txt_name = f"{anno_labels_dir}/{vid_name}_{frame_id}.txt"
        save_txt(txt_name, boxes)
        new_label = 1
    if raw_im_dir:
        cv2.imwrite(f"{raw_im_dir}/{vid_name}_{frame_id}.jpg", im)
        txt_name = f"{raw_labels_dir}/{vid_name}_{frame_id}.txt"
        save_txt(txt_name, boxes)

    return new_label


def save_txt(file_name, save_bboxes):
    with open(file_name, "w") as fp:
        file_content = []
        for i, box in enumerate(save_bboxes):
            file_content.append(anno.xyxy_to_yolo(box))
        fp.write("\n".join(file_content))
