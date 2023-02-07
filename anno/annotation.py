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

desired_deletes = []
desired_change_name = []
desired_change_point = []

pressed = False
frame_cache = None
zoom_level = 1
zoom_step = 0.1

dt_obj = ASOne(
    tracker=asone.DEEPSORT,
    detector=asone.YOLOV7_PYTORCH,
    use_cuda=True)


def mouse_click(event, x, y, flags, param):
    global boxes, display_frame, ix, iy, desired_deletes,\
        desired_change_name, pressed, frame_cache

    if event == cv2.EVENT_LBUTTONDOWN:
        ix, iy = x, y
        pressed = True
        # copy frame
        frame_cache = copy.deepcopy(display_frame)

    if pressed and event == cv2.EVENT_MOUSEMOVE:
        cv2.rectangle(frame_cache, (ix, iy), (x, y), (0, 0, 255), 2)
        cv2.imshow("window", frame_cache)
        frame_cache = copy.deepcopy(display_frame)
    # Check if you finished holding left click
    if event == cv2.EVENT_LBUTTONUP:
        pressed = False

        # Get the class with keyboard
        key = cv2.waitKey(0) & 0xFF
        selected_class_id = helpers.select_class_by_keyboard(key)

        current_box = BBox(
            coords = helpers.to_ordered_xyxy(ix, iy, x, y),
            color = cfg.id_to_color[selected_class_id],
            class_id = selected_class_id,
            frame_width=cfg.config["X_SIZE"],
            frame_height=cfg.config["Y_SIZE"])

        boxes.append(current_box)
        print(current_box.coords)

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

    if event == cv2.EVENT_RBUTTONDOWN:
        print("Right clicked: ", x, y)
        desired_deletes.append((x, y))

    # If middle button is clicked
    if event == cv2.EVENT_MBUTTONDOWN:
        print("Middle pressed: ", x, y)
        desired_change_point.append((x, y))

        # Get desired class name
        key = cv2.waitKey(0) & 0xFF
        selected_class_id = helpers.select_class_by_keyboard(key)

def update_labels(vid_name, frame_num, x_size, y_size):
    global boxes
    labels_dir = cfg.config["LABELS_DIR"]

    with open(f"{labels_dir}/{vid_name}_{frame_num}.txt", "w") as fp:
        file_content = []
        for i, box in enumerate(boxes):
            file_content.append(helpers.xyxy_to_yolo(box))
        fp.write("\n".join(file_content))

    # Make bboxes ready for next annotations
    boxes = []


def delete_labels(vid_name, frame_num, labels_path):
    global desired_deletes

    removal_list = []

    with open(f"{labels_path}/{vid_name}_{frame_num}.txt", "r+") as f_in:
        current_labels = f_in.read().split("\n")

        # Get indices where point is inside any label
        for i, label_info in enumerate(current_labels):
            c_id, xc, yc, w, h = label_info.split()
            x1, y1, x2, y2 = helpers.xywh_to_xyxy(xc, yc, w, h)
            for x_delete, y_delete in desired_deletes:
                if max(x1, x2) > x_delete > min(x1, x2) and max(y1, y2) > y_delete > min(y1, y2):
                    if i not in removal_list:
                        removal_list.append(i)

        f_in.seek(0)
        f_in.truncate()

        for i, label_info in enumerate(current_labels):
            if i not in removal_list:
                f_in.write(label_info)

    # Prepare desired_deletes for next frames
    desired_deletes = []


def change_class_name(vid_name, frame_num, labels_path):
    global desired_change_name, desired_change_point

    lines_list = []
    changed_line_list = []

    # Open file
    f1 = open("{}/{}_{}.txt".format(labels_path, vid_name, frame_num), "r")

    # Get lines
    for line in f1:
        lines_list.append(line)
        changed_line_list.append(line)

    # Get indices where point is inside any label
    cnt = 0
    for i in range(len(lines_list)):
        values = lines_list[i].split("\t")
        x1, y1, x2, y2 = int(values[1]), int(values[2]), int(values[3]), int(values[4])
        cnt_p = 0
        for point in desired_change_point:
            xp, yp = int(point[0]), int(point[1])
            if max(x1, x2) > xp > min(x1, x2) and max(y1, y2) > yp > min(y1, y2):
                new_class = desired_change_name[cnt_p]
                new_line = new_class + "\t" + str(x1) + "\t" + str(y1) + "\t" + str(x2) + "\t" + str(y2) + "\n"
                changed_line_list.pop(cnt)
                changed_line_list.insert(cnt, new_line)
                break
            cnt_p += 1

        cnt += 1

    # Open file to write
    f2 = open("{}/{}_{}.txt".format(labels_path, vid_name, frame_num), "w")

    for line in changed_line_list:
        f2.write(line)

    # Prepare them for next frames
    desired_change_name = []
    desired_change_point = []


def annotation_from_local_video(video_path):
    global boxes, display_frame, desired_deletes, \
        desired_change_name, zoom_level, zoom_step

    # Zoom level and step size for each scroll
    zoom_level = 1
    zoom_step = 0.1

    frames_path = cfg.config["FRAMES_DIR"]
    anno_frames_dir = cfg.config["ANNOTATED_FRAMES_DIR"]
    x_size = cfg.config["X_SIZE"]
    y_size = cfg.config["Y_SIZE"]
    # vid name without file extension
    video_name = os.path.basename(video_path).split(".")[0]

    # tracking function
    track_fn = dt_obj.track_video(
        video_path, output_dir="./temp",
        save_result=cfg.config["SAVE_ORIGINAL"], display=cfg.config["DISPLAY_ORIGINAL"],
        filter_classes=cfg.config["FILTERED_CLASSES"])

    # Loop over track_fn to retrieve outputs of each frame
    for bbox_details, frame_details in track_fn:
        bboxes, track_ids, _, class_ids = bbox_details
        display_frame, frame_num, _ = frame_details
        if cfg.config["SAVE_RAW"]:
            cv2.imwrite(f"{frames_path}/{video_name}_{frame_num}.jpg", display_frame)

        original_width, original_height = display_frame.shape[0], display_frame.shape[1]

        # insert initial bboxes on frame
        display_frame, boxes = helpers.init_frame(display_frame, bboxes, class_ids, track_ids,
                                                  original_width, original_height)
        display_frame = cv2.resize(display_frame, (x_size, y_size))
        # display initial detections
        cv2.imshow("window", display_frame)
        key = cv2.waitKey(50) & 0xFF  # determines display fps

        # quit progam if "q" pressed
        if key == ord("q"):
            break

        elif key == ord("a"):
            print("Annotation Mode opened, video paused!")
            cv2.setMouseCallback('window', mouse_click)
            cv2.waitKey(0)

            if len(boxes) != 0:
                if cfg.config["SAVE_ANNOTATED_FRAMES"]:
                    cv2.imwrite(f"{anno_frames_dir}/{video_name}_{frame_num}.jpg", display_frame)

                update_labels(video_name, frame_num, x_size, y_size)

            # If right is clicked and it is desired to delete some labels
            if len(desired_deletes) > 0:
                print("Deleting desired labels")
                delete_labels(video_name, frame_num)

            if len(desired_change_name) > 0:
                print("Changing class names of desired labels")
                change_class_name(video_name, frame_num)

    # close windows
    cv2.destroyAllWindows()
