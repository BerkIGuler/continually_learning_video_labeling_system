from anno.interact import select_class_by_keyboard
from anno.frames import init_frame
from anno.boxes import BBox, init_boxes, modify_active_box, activate_box
from anno.utils import to_ordered_xyxy, xyxy_to_yolo


MAX_DISTANCE = 1.5
RED_RGB = (0, 0, 255)  # opencv uses BGR by default
