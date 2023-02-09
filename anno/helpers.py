import cv2
import cfg
import math

MAX_DISTANCE = 1.5
# opencv uses BGR by default
RED_RGB = (0, 0, 255)


class BBox:
    def __init__(self, coords=None, color=None, class_id=None,
                 track_id=None, frame_width=None, frame_height=None, state="passive"):
        self.coords = coords
        self.color = color
        self.class_id = class_id
        self.track_id = track_id
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.state = state


def init_boxes(bboxes, ids, track_ids, x_size, y_size):
    boxes = []

    if not isinstance(bboxes, list):
        bboxes = bboxes.tolist()

    for bbox, c_id, t_id in zip(bboxes, ids, track_ids):
        boxes.append(BBox(
            coords=bbox,
            color=cfg.id_to_color[c_id],
            class_id=c_id,
            track_id=t_id,
            frame_height=x_size,
            frame_width=y_size,
            state="passive"
        ))
    return boxes


def init_frame(frame, boxes):
    if not boxes:
        return frame
    for i, box in enumerate(boxes):
        if box.state == "passive":
            cv2.rectangle(
                frame, box.coords[:2], box.coords[2:],
                cfg.id_to_color[box.class_id], 1)
            cv2.putText(
                frame, cfg.id_to_class[box.class_id], (box.coords[0], box.coords[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, cfg.id_to_color[box.class_id], 1,
                cv2.LINE_4)
        elif box.state == "active":
            cv2.rectangle(frame, box.coords[:2], box.coords[:2], RED_RGB, 1)
            cv2.putText(
                frame, cfg.id_to_class[box.class_id], (box.coords[0], box.coords[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED_RGB, 1,
                cv2.LINE_4)
    return frame


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


def xyxy_to_yolo(box, return_type="str"):
    x1, y1, x2, y2 = box.coords
    w = abs(x2 - x1) / box.frame_width
    h = abs(y2 - y1) / box.frame_height
    xc = (x1 + x2) / (2 * box.frame_width)
    yc = (y1 + y2) / (2 * box.frame_height)
    if return_type == "str":
        yolo_formatted = f"{box.class_id} {xc:.5} {yc:.5} {w:.5} {h:.5}"
    elif return_type == "tuple":
        yolo_formatted = box.class_id, xc, yc, w, h
    else:
        raise ValueError("return_type must be either 'str' or 'tuple'")
    return yolo_formatted


def to_ordered_xyxy(ix, iy, x, y):

    x1, x2 = (ix, x) if ix < x else (x, ix)
    y1, y2 = (iy, y) if iy < y else (y, iy)

    return [x1, y1, x2, y2]


def activate_box(boxes, x, y, x_size, y_size):
    norm_x, norm_y = x / x_size, y / y_size
    # distance cant be smaller than sqrt(2)
    closest_dist = MAX_DISTANCE
    candidate_box_id = None
    for i, box in enumerate(boxes):
        c_id, xc, yc, w, h = xyxy_to_yolo(box, return_type="tuple")
        euc_dist = math.sqrt((xc-norm_x)**2 + (yc-norm_y)**2)
        if euc_dist < closest_dist and in_box(norm_x, norm_y, xc, yc, w, h):
            closest_dist = euc_dist
            candidate_box_id = i
            box.state = "active"

    if candidate_box_id:
        for i, box in enumerate(boxes):
            if i != candidate_box_id and box.state == "active":
                box.state = "passive"


def in_box(norm_x, norm_y, xc, yc, w, h):
    left_x = xc - w/2 if xc - w/2 > 0 else 0
    right_x = xc + w/2 if xc + w/2 < 1 else 1
    top_y = yc - h/2 if yc - h/2  > 0 else 0
    bottom_y = yc + h/2 if yc + h/2 < 1 else 1

    if bottom_y > norm_y > top_y and right_x > norm_x > left_x:
        status = True
    else:
        status = False

    return status


if __name__ == "__main__":
    pass
