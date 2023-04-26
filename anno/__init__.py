from anno.interact import select_class_by_keyboard, init_frame_counters
from anno.frames import init_frame, show_frame
from anno.boxes import BBox, init_boxes, modify_active_box, activate_box, get_cursor_to_abox_status
from anno.utils import to_ordered_xyxy, xyxy_to_yolo
from anno.tracker import setup_tracker


# max distance in normalized coordinates cannot be greater than sqrt(2)
MAX_DISTANCE = 1.5
RED_RGB = (0, 0, 255)  # opencv uses BGR by default
