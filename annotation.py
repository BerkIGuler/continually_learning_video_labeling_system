import copy
import os
import cv2
from loguru import logger

import cfg
import asone

from anno import (select_class_by_keyboard, init_boxes, init_frame, show_frame,
                  BBox, to_ordered_xyxy, activate_box, modify_active_box,
                  xyxy_to_yolo, setup_tracker)


display_frame = None
ix, iy = 0, 0
boxes = []

pressed = False
waiting_key = False
frame_cache = None
empty_frame = None


def mouse_click(event, x, y, flags, param):
    global boxes, display_frame, ix, iy, \
        pressed, frame_cache, empty_frame, \
        waiting_key

    if event == cv2.EVENT_LBUTTONDOWN:
        ix, iy = x, y
        pressed = True
        # copy frame
        boxed_frame = copy.deepcopy(empty_frame)
        init_frame(boxed_frame, boxes)
        frame_cache = copy.deepcopy(boxed_frame)

    elif pressed and event == cv2.EVENT_MOUSEMOVE:
        cv2.rectangle(frame_cache, (ix, iy), (x, y), (0, 0, 255), 1)
        show_frame(frame_cache, "window", mode="annotate")
        boxed_frame = copy.deepcopy(empty_frame)
        init_frame(boxed_frame, boxes)
        frame_cache = copy.deepcopy(boxed_frame)

    elif event == cv2.EVENT_LBUTTONUP:
        pressed = False
        # Get the class id with keyboard
        key = cv2.waitKey(0) & 0xFF
        selected_class_id = select_class_by_keyboard(key)
        current_box = BBox(
            coords=to_ordered_xyxy(ix, iy, x, y),
            color=cfg.id_to_color[selected_class_id],
            class_id=selected_class_id,
            frame_width=cfg.config["X_SIZE"],
            frame_height=cfg.config["Y_SIZE"]
        )
        boxes.append(current_box)
        # Draw bounding box
        display_frame = copy.deepcopy(empty_frame)
        init_frame(display_frame, boxes)
        show_frame(display_frame, "window", mode="annotate")

    elif event == cv2.EVENT_RBUTTONDOWN:
        delete_bbox = activate_box(boxes, x, y, cfg.config["X_SIZE"], cfg.config["Y_SIZE"])
        display_frame = copy.deepcopy(empty_frame)
        init_frame(display_frame, boxes)
        show_frame(display_frame, "window", mode="annotate")
        if delete_bbox:
            modify_active_box(
                boxes, task="delete")
        elif not waiting_key:
            waiting_key = True
            key = cv2.waitKey(0) & 0xFF
            waiting_key = False
            selected_class_id = select_class_by_keyboard(key)
            if selected_class_id:
                modify_active_box(
                    boxes, task="update_label",
                    new_class_id=selected_class_id)
        display_frame = copy.deepcopy(empty_frame)
        init_frame(display_frame, boxes)
        show_frame(display_frame, "window", mode="annotate")


def update_labels(frame_num, annotated: bool, vid_name=None, is_real_time=False, **kwargs):
    global boxes
    if annotated:
        labels_dir = cfg.config["EDITED_LABELS_DIR"]
    else:
        labels_dir = cfg.config["LABELS_DIR"]
    if is_real_time:
        with open(f"{labels_dir}/real_time_vid_{frame_num}.txt", "w") as fp:
            file_content = []
            for i, box in enumerate(boxes):
                file_content.append(xyxy_to_yolo(box))
            fp.write("\n".join(file_content))
    else:
        with open(f"{labels_dir}/{vid_name}_{frame_num}.txt", "w") as fp:
            file_content = []
            for i, box in enumerate(boxes):
                file_content.append(xyxy_to_yolo(box))
            fp.write("\n".join(file_content))

    # Make bboxes ready for next annotations
    if annotated:  # To make annotated label.txt have all label data
        boxes = []


def annotate(video_path=None, is_real_time=False):
    global boxes, display_frame, empty_frame

    frames_path = cfg.config["FRAMES_DIR"]  # raw frames
    anno_frames_dir = cfg.config["ANNOTATED_FRAMES_DIR"]
    x_size_window = cfg.config["X_SIZE"]
    y_size_window = cfg.config["Y_SIZE"]

    if not is_real_time:
        video_name = os.path.basename(video_path).split(".")[0]

    cv2.namedWindow("window", cv2.WINDOW_GUI_NORMAL)
    cv2.resizeWindow("window", x_size_window, y_size_window)

    track_fn = setup_tracker(real_time=is_real_time, video_path=video_path)

    for bbox_details, frame_details, action in track_fn:
        if action == "stream":
            bboxes, track_ids, _, class_ids = bbox_details
            display_frame, frame_id, frame_count, fps = frame_details
        elif action == "annotation":
            cv2.setMouseCallback('window', mouse_click)
            logger.info("Annotation Mode opened, video paused!")
            key = cv2.waitKey(0) & 0xFF  # stop the video
            while key != asone.ESC_KEY:  # press ESC to quit anno mode
                key = cv2.waitKey(0) & 0xFF
            # deactivate mouse event trigger
            cv2.setMouseCallback('window', lambda *args: None)

            if len(boxes) != 0:
                if is_real_time and cfg.config["SAVE_EDITED_FRAMES"]:
                    cv2.imwrite(f"{anno_frames_dir}/real_time_vid_{frame_id}.jpg", display_frame)
                    update_labels(frame_num=frame_id, annotated=True, is_real_time=True)
                elif cfg.config["SAVE_EDITED_FRAMES"]:
                    cv2.imwrite(f"{anno_frames_dir}/{video_name}_{frame_id}.jpg", display_frame)
                    update_labels(vid_name=video_name, frame_num=frame_id, annotated=True)
            continue

        if is_real_time and cfg.config["SAVE_RAW"]:
            cv2.imwrite(f"{frames_path}/real_time_vid_{frame_id}.jpg", display_frame)
        elif cfg.config["SAVE_RAW"]:
            cv2.imwrite(f"{frames_path}/{video_name}_{frame_id}.jpg", display_frame)

        original_height, original_width = display_frame.shape[:2]
        boxes = init_boxes(
            bboxes, class_ids, track_ids,
            original_width, original_height)
        display_frame = cv2.resize(display_frame, (x_size_window, y_size_window))
        empty_frame = copy.deepcopy(display_frame)
        init_frame(display_frame, boxes)

        show_frame(display_frame, "window", fps, frame_id, frame_count)
        if is_real_time and cfg.config["SAVE_RAW"]:
            cv2.imwrite(f"{frames_path}/real_time_vid_{frame_id}.jpg", display_frame)
        elif cfg.config["SAVE_NON_EDITED_FRAMES"]:
            update_labels(vid_name=video_name, frame_num=frame_id, annotated=False)

    cv2.destroyAllWindows()
