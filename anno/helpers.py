import cv2
import yaml
import os
import cfg


class BBox:
    def __init__(self, coords=None, color=None, class_id=None, track_id=None, frame_width=None, frame_height=None):
        self.coords = coords
        self.color = color
        self.class_id = class_id
        self.track_id = track_id
        self.frame_width = frame_width
        self.frame_height = frame_height


def init_frame(frame, bboxes, ids, track_ids, x_size, y_size):
    boxes = []

    if not isinstance(bboxes, list):
        bboxes = bboxes.tolist()

    for bbox, c_id, t_id in zip(bboxes, ids, track_ids):
        cv2.rectangle(frame, bbox[:2], bbox[2:], cfg.id_to_color[c_id], 1)
        cv2.putText(
            frame, cfg.id_to_class[c_id], (min(bbox[0], bbox[2]), min(bbox[1], bbox[3]) - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, cfg.id_to_color[c_id], 1,
            cv2.LINE_4)
        boxes.append(BBox(
            coords=bbox,
            color=cfg.id_to_color[c_id],
            class_id=c_id,
            track_id=t_id,
            frame_height=x_size,
            frame_width=y_size
        ))

    return frame, boxes


def xywh_to_xyxy(x, y, w, h):
    x1 = min(round(x + w / 2), round(x - w / 2))
    x2 = max(round(x + w / 2), round(x - w / 2))
    y1 = max(round(y + h / 2), round(y - h / 2))
    y2 = min(round(y + h / 2), round(y - h / 2))

    return [x1, y1, x2, y2]

def select_class_by_keyboard(key):
    if key == ord("1"):
        selected_class_id = 0  # person
    elif key == ord("2"):
        selected_class_id = 1  # car
    elif key == ord("3"):
        selected_class_id = 24  # apartment
    elif key == ord("4"):
        selected_class_id = 32  # forest
    elif key == ord("5"):
        selected_class_id = 31  # cloud
    else:
        raise "nondefined class_id\nEnter a valid key"

    return selected_class_id


def xyxy_to_yolo(box):
    x1, y1, x2, y2 = box.coords
    w = abs(x2 - x1) / box.frame_width
    h = abs(y2 - y1) / box.frame_height
    xc = (x1 + x2) / (2 * box.frame_width)
    yc = (y1 + y2) / (2 * box.frame_height)
    yolo_formatted = f"{box.class_id} {xc:.5} {yc:.5} {w:.5} {h:.5}"
    return yolo_formatted


def to_ordered_xyxy(ix, iy, x, y):

    x1, x2 = (ix, x) if ix < x else (x, ix)
    y1, y2 = (iy, y) if iy < y else (y, iy)

    return [x1, y1, x2, y2]



if __name__ == "__main__":
    test_case = (10, 20, 4, 8)
    result = xywh_to_xyxy(*test_case)
    print(result)
    print(round(1.52))
