import copy
import os
import cv2
import asone
from asone import ASOne

import helpers
from helpers import BBox
import cfg


display_frame = None
# initial x y
ix, iy = 0, 0
boxes = []

pressed = False
frame_cache = None
empty_frame = None

dt_obj = ASOne(
    tracker=asone.DEEPSORT,
    detector=asone.YOLOV7_PYTORCH,
    use_cuda=True)


def mouse_click(event, x, y, flags, param):
    global boxes, display_frame, ix, iy, \
        pressed, frame_cache, empty_frame

    if event == cv2.EVENT_LBUTTONDOWN:
        ix, iy = x, y
        pressed = True
        # copy frame
        frame_cache = copy.deepcopy(display_frame)

    elif pressed and event == cv2.EVENT_MOUSEMOVE:
        cv2.rectangle(frame_cache, (ix, iy), (x, y), (0, 0, 255), 2)
        cv2.imshow("window", frame_cache)
        frame_cache = copy.deepcopy(display_frame)

    elif event == cv2.EVENT_LBUTTONUP:
        pressed = False

        # Get the class with keyboard
        key = cv2.waitKey(0) & 0xFF
        selected_class_id = helpers.select_class_by_keyboard(key)

        current_box = BBox(
            coords=helpers.to_ordered_xyxy(ix, iy, x, y),
            color=cfg.id_to_color[selected_class_id],
            class_id=selected_class_id,
            frame_width=cfg.config["X_SIZE"],
            frame_height=cfg.config["Y_SIZE"]
        )

        boxes.append(current_box)
        print(current_box.coords)  # TEMP, FOR DEBUGGING

        # Draw bounding box
        cv2.rectangle(
            display_frame, current_box.coords[:2],
            current_box.coords[2:], current_box.color, 1)
        text_position = (min(current_box.coords[0], current_box.coords[2]),
                         min(current_box.coords[1], current_box.coords[3]) - 5)
        cv2.putText(
            display_frame, cfg.id_to_class[current_box.class_id], text_position,
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, current_box.color, 1,
            cv2.LINE_4)

        cv2.imshow("window", display_frame)

    elif event == cv2.EVENT_RBUTTONDOWN:
        helpers.activate_box(boxes, x, y, cfg.config["X_SIZE"], cfg.config["Y_SIZE"])
        cache_empty_frame = copy.deepcopy(empty_frame)
        helpers.init_frame(empty_frame, boxes)
        display_frame = empty_frame
        cv2.imshow("window", display_frame)
        key = cv2.waitKey(0) & 0xFF
        selected_class_id = helpers.select_class_by_keyboard(key)
        helpers.modify_active_box(
            boxes, task="update_label",
            new_class_id=selected_class_id)
        helpers.init_frame(cache_empty_frame, boxes)
        display_frame = cache_empty_frame
        cv2.imshow("window", display_frame)


def update_labels(vid_name, frame_num):
    global boxes
    labels_dir = cfg.config["LABELS_DIR"]

    with open(f"{labels_dir}/{vid_name}_{frame_num}.txt", "w") as fp:
        file_content = []
        for i, box in enumerate(boxes):
            file_content.append(helpers.xyxy_to_yolo(box))
        fp.write("\n".join(file_content))

    # Make bboxes ready for next annotations
    boxes = []


def annotation_from_local_video(video_path):
    global boxes, display_frame, empty_frame

    frames_path = cfg.config["FRAMES_DIR"]
    anno_frames_dir = cfg.config["ANNOTATED_FRAMES_DIR"]
    x_size = cfg.config["X_SIZE"]
    y_size = cfg.config["Y_SIZE"]

    # vid name without file extension
    video_name = os.path.basename(video_path).split(".")[0]

    # tracking function
    track_fn = dt_obj.track_video(
        video_path, output_dir="./temp", save_result=cfg.config["SAVE_ORIGINAL"],
        display=cfg.config["DISPLAY_ORIGINAL"],
        filter_classes=cfg.config["FILTERED_CLASSES"])

    # Loop over track_fn to retrieve outputs of each frame
    for bbox_details, frame_details in track_fn:
        bboxes, track_ids, _, class_ids = bbox_details
        display_frame, frame_num, _ = frame_details

        if cfg.config["SAVE_RAW"]:
            cv2.imwrite(f"{frames_path}/{video_name}_{frame_num}.jpg", display_frame)

        original_height, original_width = display_frame.shape[:2]

        boxes = helpers.init_boxes(
            bboxes, class_ids, track_ids,
            original_width, original_height)

        display_frame = cv2.resize(display_frame, (x_size, y_size))
        empty_frame = copy.deepcopy(display_frame)
        helpers.init_frame(display_frame, boxes)
        # display yolo detections
        cv2.imshow("window", display_frame)
        key = cv2.pollKey() & 0xFF
        print(key)
        # quit program if "q" pressed
        if key == ord("a"):
            break

        elif key == ord("q"):
            cv2.setMouseCallback('window', mouse_click)
            cv2.waitKey(0)
            print("Annotation Mode opened, video paused!")

            if len(boxes) != 0:
                if cfg.config["SAVE_ANNOTATED_FRAMES"]:
                    cv2.imwrite(f"{anno_frames_dir}/{video_name}_{frame_num}.jpg", display_frame)

                update_labels(video_name, frame_num)

    cv2.destroyAllWindows()
