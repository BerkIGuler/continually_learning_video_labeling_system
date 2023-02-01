import cv2
import yaml
import os

cwd = os.getcwd()
config_dir = os.path.join(cwd, "config_files")
colors_path = os.path.join(config_dir, "color_list.yaml")
class_path = os.path.join(config_dir, "class_list.yaml")

with open(colors_path, "r") as f_in:
    colors = yaml.safe_load(f_in)

with open(class_path, "r") as f_in:
    classes = yaml.safe_load(f_in)

def init_frame(frame, bboxes, ids):
    for bbox, _id in zip(bboxes, ids):
        cv2.rectangle(frame, bbox[:2], bbox[2:], (0, 0, 255), 2)
        cv2.putText(
            frame, classes[_id], (min(bbox[0], bbox[2]), min(bbox[1], bbox[3]) - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1,
            cv2.LINE_4)

    return frame
