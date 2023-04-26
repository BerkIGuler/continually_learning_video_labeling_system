import os
import shutil

import cv2
import zipfile

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


class Unzipper:
    def __init__(self, zip_file, output_folder=None):
        self.zip_file = zip_file
        self.output_folder = output_folder if output_folder else os.path.dirname(zip_file)

    def unzip(self):
        if not zipfile.is_zipfile(self.zip_file):
            print(f"{self.zip_file} is not a valid ZIP file.")
            return

        with zipfile.ZipFile(self.zip_file, 'r') as zip_ref:
            try:
                zip_ref.extractall(self.output_folder)
                print(f"Files extracted to: {self.output_folder}")
            except Exception as e:
                print(f"Error occurred while extracting files: {e}")


def update_weights(zip_file_path="./receive_file.zip", inside_temp_folder="./temp_dir/sent_model", temp_folder="./temp_dir", file_name="best.pt", target_folder="./yolov7/weights/"):
    unzipper = Unzipper(zip_file_path, temp_folder)
    unzipper.unzip()
    delete_file(target_folder, "yolov7.pt")
    move_file(inside_temp_folder, file_name)


def delete_file(folder, file_name):
    file_path = os.path.join(folder, file_name)

    if not os.path.exists(folder):
        print(f"Folder '{folder}' does not exist.")
        return

    if not os.path.isfile(file_path):
        print(f"File '{file_name}' not found in '{folder}'.")
        return

    try:
        os.remove(file_path)
        print(f"File '{file_name}' deleted from '{folder}'.")
    except Exception as e:
        print(f"Error occurred while deleting file: {e}")


def move_file(source_folder, file_name, target_folder="./yolov7/weights/", target_file_name='yolov7.pt'):
    source_path = os.path.join(source_folder, file_name)
    target_path = os.path.join(target_folder, target_file_name)

    if not os.path.exists(source_folder):
        print(f"Source folder '{source_folder}' does not exist.")
        return

    if not os.path.exists(target_folder):
        print(f"Target folder '{target_folder}' does not exist. Creating it.")
        os.makedirs(target_folder)

    if not os.path.isfile(source_path):
        print(f"File '{file_name}' not found in '{source_folder}'.")
        return

    try:
        shutil.move(source_path, target_path)
        print(f"File '{file_name}' moved from '{source_folder}' to '{target_folder}'.")
    except Exception as e:
        print(f"Error occurred while moving file: {e}")


if __name__ == "__main__":
    target_folder = "../yolov7/weights"
    file_name = "best.pt"
    temp_folder = "../temp_dir"
    zip_file_path = "../receive_file.zip"
    inside_temp_folder = "../temp_dir/sent_model"
    update_weights(zip_file_path, inside_temp_folder, temp_folder, file_name)
