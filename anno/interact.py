import os
import shutil
import cv2
import zipfile

import cfg
import anno
from loguru import logger


def select_class_by_keyboard(key):
    """return class_id based on key from cv2.waitKey()"""
    class_to_id = {value: key for (key, value) in cfg.id_to_class.items()}

    try:
        # {"c":"car", "a":"apartment", ...}
        class_name = cfg.key_to_class[key]
        # {"car": 6, "apartment": 13, ...}
        selected_class_id = class_to_id[class_name]
        return selected_class_id
    except KeyError:
        return None


def init_frame_counters(anno_frames_path, labels_path):
    """get initial values for counters displayed during annotation"""
    initial_anno_frame_count = sum([1 for file in
                                    os.listdir(anno_frames_path)
                                    if file.endswith(".jpg")
                                    ]
                                   )

    initial_label_count = sum([1 for file in
                               os.listdir(labels_path)
                               if file.endswith(".txt")
                               ]
                              )

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
    """saves labels and frames to disk"""
    # new_label is the increment for annotated frame counter
    new_label = 0
    if anno_im_dir:
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
    """saves a txt file in yolo format"""
    with open(file_name, "w") as fp:
        file_content = []
        for i, box in enumerate(save_bboxes):
            bbox_yolo_format = anno.xyxy_to_yolo(box)
            if bbox_yolo_format is not None:
                file_content.append(bbox_yolo_format)
        fp.write("\n".join(file_content))


def flush_sent_files():
    """deletes sent files from the disk"""
    cwd = os.getcwd()
    rm_dir = os.path.join(cwd, cfg.config["FOLDER_SENT"])
    shutil.rmtree(rm_dir, ignore_errors=True)  # rm
    os.remove(rm_dir + ".zip")  # remove temp zip file
    # create an empty frames & labels dir
    os.makedirs(cfg.config["ANNOTATED_FRAMES_DIR"], exist_ok=True)
    os.makedirs(cfg.config["ANNOTATED_LABELS_DIR"], exist_ok=True)


class Unzipper:
    """Decompresses a zip file"""
    def __init__(self, zip_file, output_folder):
        self.zip_file = zip_file
        self.output_folder = output_folder

    def unzip(self):
        if not zipfile.is_zipfile(self.zip_file):
            raise TypeError(f"{self.zip_file} is not a valid ZIP file.")

        with zipfile.ZipFile(self.zip_file, 'r') as zip_ref:
            try:
                zip_ref.extractall(self.output_folder)
            except Exception as e:
                logger.error(f"Error occurred {e}")


def update_weights(temp_folder_name="temp_dir"):
    """replaces the old model file with the new one"""

    cwd = os.getcwd()
    zip_file_name = cfg.config["RECEIVE_SAVE_NAME"]
    zip_file_path = os.path.join(cwd, f"{zip_file_name}.zip")
    temp_folder_path = os.path.join(cwd, temp_folder_name)
    # unzip into temp_folder
    unzipper = Unzipper(zip_file_path, temp_folder_path)
    unzipper.unzip()
    # rm zip file
    os.remove(zip_file_path)

    # assumes there is only one folder inside
    assert len(os.listdir(temp_folder_path)) == 1, \
        "zip file must contain one folder which contains a folder with the .pt file"
    inside_temp_folder_path = os.path.join(temp_folder_path, os.listdir(temp_folder_path)[0])
    # assuming there is only one file inside
    assert len(os.listdir(inside_temp_folder_path)) == 1, \
        "zip file must contain one folder which contains a folder with the .pt file"
    model_dir = os.path.join(inside_temp_folder_path, os.listdir(inside_temp_folder_path)[0])
    assert len(os.listdir(model_dir)) == 1, \
        "zip file must contain one folder which contains a folder with the .pt file"
    model_path = os.path.join(model_dir, os.listdir(model_dir)[0])

    # if the new model name is different from the expected, rename
    if os.path.basename(model_path) != "best.pt":
        new_model_path = os.path.join(
            os.path.dirname(model_path),
            "best.pt"
        )
        os.rename(
            model_path,
            new_model_path
        )
        model_path = new_model_path

    # move the new model file to yolov7 dir
    target_path = os.path.join(cwd, "yolov7", "weights")
    shutil.move(model_path, target_path)
    # rm temp dir
    shutil.rmtree(temp_folder_path)
    # rm old model file
    os.remove(os.path.join(target_path, "yolov7.pt"))
    # rename new model file to yolov7.pt
    os.rename(
        os.path.join(target_path, "best.pt"),
        os.path.join(target_path, "yolov7.pt")
    )
