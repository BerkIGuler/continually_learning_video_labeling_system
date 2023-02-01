import copy
import os
import cv2
import asone
from asone import ASOne
import yaml

import helpers

cwd = os.getcwd()
config_dir = os.path.join(cwd, "config_files")
colors_path = os.path.join(config_dir, "color_list.yaml")
class_path = os.path.join(config_dir, "class_list.yaml")

with open(colors_path, "r") as f_in:
    colors = yaml.safe_load(f_in)

with open(class_path, "r") as f_in:
    classes = yaml.safe_load(f_in)

zoom_level = 1
zoom_step = 0.1

# To write x and y values & classes
bboxes = []
class_ids = []

# To show added labels frame
display_frame = None
drawing = False
ix, iy = 0, 0

# To save desired deleting labels
desired_deletes = []

# To change class name
desired_change_name = []
desired_change_point = []

pressed = False
cache = None

dt_obj = ASOne(
    tracker=asone.DEEPSORT,
    detector=asone.YOLOV7_PYTORCH,
    use_cuda=True)

# None to track all classes
filter_classes = None


def mouse_click(event, x, y, flags, param):
    global bboxes, class_ids, display_frame, drawing, ix, iy,\
        desired_deletes, desired_change_name, zoom_level, zoom_step, pressed, cache, classDict

    # Check if you started to hold left click
    if event == cv2.EVENT_LBUTTONDOWN:
        ix, iy = x, y
        pressed = True
        cache = copy.deepcopy(display_frame)

    if event == cv2.EVENT_MOUSEMOVE and pressed:
        cv2.rectangle(cache, (ix, iy), (x, y), (0, 0, 255), 2)
        cv2.imshow("window", cache)
        cache = copy.deepcopy(display_frame)
    # Check if you finished holding left click
    if event == cv2.EVENT_LBUTTONUP:
        bboxes.append([ix, iy, x, y])
        pressed = False

        # Get the class with keyboard
        key = cv2.waitKey(0)
        if key == ord("1"):
            class_ids.append(7)  # Person
        elif key == ord("2"):
            class_ids.append(1)  # Car
        elif key == ord("3"):
            class_ids.append(24)  # Apartment
        elif key == ord("4"):
            class_ids.append(32)  # Forest
        elif key == ord("5"):
            class_ids.append(31)  # Cloud

        # Draw bounding box
        cv2.rectangle(display_frame, (ix, iy), (x, y), (0, 0, 255), 2)
        cv2.putText(
            display_frame, classes[class_ids[-1]], (min(x, ix), min(y, iy) - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1,
            cv2.LINE_4)

        cv2.imshow("window", display_frame)

    # When right clicked
    if event == cv2.EVENT_RBUTTONDOWN:
        print("Right clicked: ", x, y)
        desired_deletes.append((x, y))

    # If middle button is clicked
    if event == cv2.EVENT_MBUTTONDOWN:
        print("Middle pressed: ", x, y)
        desired_change_point.append((x, y))

        # Get desired class name
        key = cv2.waitKey(0)
        if key == ord("1"):
            class_ids.append(7) # Person
        elif key == ord("2"):
            class_ids.append(1) # Car
        elif key == ord("3"):
            class_ids.append(24) # Apartment
        elif key == ord("4"):
            class_ids.append(32) # Forest
        elif key == ord("5"):
            class_ids.append(31)  # Cloud

    if event == cv2.EVENT_MOUSEWHEEL:
        print("Mouse wheel touched")
        # If the mouse scroll is moved up, zoom in
        if flags > 0:
            print((x, y))
            zoom_level += zoom_step
            print(zoom_level)
            display_frame = cv2.resize(
                display_frame, None, fx=zoom_level,
                fy=zoom_level, interpolation=cv2.INTER_LINEAR)
            cv2.imshow("window", display_frame)
        # If the mouse scroll is moved down, zoom out
        elif flags < 0:
            print((x, y))
            zoom_level -= zoom_step
            print(zoom_level)
            display_frame = cv2.resize(
                display_frame, None, fx=zoom_level,
                fy=zoom_level, interpolation=cv2.INTER_LINEAR)

            # Get the new size of the image
            # rows, cols, _ = display_frame.shape
            # Get the new center of the image
            # new_center = (x,y)
            # Calculate the translation to keep the center at the same position
            # Middle = np.float32([[1, 0, new_center[0] - center[0]], [0, 1, new_center[1] - center[1]]])
            # display_frame = cv2.warpAffine(display_frame, new_center, (cols, rows))

            cv2.imshow("window", display_frame)



def update_labels(vid_name, frame_num, labels_path, x_size, y_size):
    global bboxes, class_ids

    # If there is already labeled info, append
    if os.path.exists("{}/{}_{}.txt".format(labels_path, vid_name, frame_num)):
        file = open("{}/{}_{}.txt".format(labels_path, vid_name, frame_num), "a")
        cnt = 0
        for i in range(0, len(bboxes)):
            centerPointx = (bboxes[i][0] + bboxes[i][2]) / 2 / x_size
            centerPointy = (bboxes[i][1] + bboxes[i][3]) / 2 / y_size
            width = abs(bboxes[i][0] - bboxes[i][2]) / x_size
            height = abs(bboxes[i][1] - bboxes[i][3]) / y_size
            file.write(str(class_ids[cnt]) + " ")
            file.write("{:.6f}".format(centerPointx) + " ")
            file.write("{:.6f}".format(centerPointy) + " ")
            file.write("{:.6f}".format(width) + " ")
            file.write("{:.6f}".format(height) + "\n")
            cnt += 1

    # If there is not any label yet, create and write
    else:
        file = open("{}/{}_{}.txt".format(labels_path, vid_name, frame_num), "w")
        cnt = 0
        for i in range(0, len(bboxes)):
            centerPointx = (bboxes[i][0] + bboxes[i][2]) / 2 / x_size
            centerPointy = (bboxes[i][1] + bboxes[i][3]) / 2 / y_size
            width = abs(bboxes[i][0] - bboxes[i][2]) / x_size
            height = abs(bboxes[i][1] - bboxes[i][3]) / y_size
            file.write(str(class_ids[cnt]) + " ")
            file.write("{:.6f}".format(centerPointx) + " ")
            file.write("{:.6f}".format(centerPointy) + " ")
            file.write("{:.6f}".format(width) + " ")
            file.write("{:.6f}".format(height) + "\n")
            cnt += 1

    # Make bboxes ready for next annotations
    bboxes = []
    class_ids = []


def save_annotated_frames(vid_name, anno_frame, frame_num, anno_frames_path):
    cv2.imwrite("{}/{}_{}.jpg".format(anno_frames_path, vid_name, frame_num), anno_frame)


def delete_labels(vid_name, frame_num, labels_path):
    global desired_deletes

    lines_list = []
    removal_list = []

    # Open file to read
    f1 = open("{}/{}_{}.txt".format(labels_path, vid_name, frame_num), "r")

    # Get lines
    for line in f1:
        lines_list.append(line)

    # Get indices where point is inside any label
    cnt = 0
    for i in range(len(lines_list)):
        values = lines_list[i].split("\t")
        x1, y1, x2, y2 = int(values[1]), int(values[2]), int(values[3]), int(values[4])
        for point in desired_deletes:
            xp, yp = int(point[0]), int(point[1])
            if max(x1, x2) > xp > min(x1, x2) and max(y1, y2) > yp > min(y1, y2):
                if cnt not in removal_list:
                    removal_list.append(cnt)
        cnt += 1

    # Open file to write
    f2 = open("{}/{}_{}.txt".format(labels_path, vid_name, frame_num), "w")

    for i in range(len(lines_list)):
        if i not in removal_list:
            f2.write(lines_list[i])

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


def annotation_from_local_video(
        video_path, fps, x_size, y_size,
        frames_path, labels_path, annotated_frames_path):
    global bboxes, display_frame, desired_deletes, desired_change_name, zoom_level, zoom_step
    # Zoom level and step size for each scroll
    zoom_level = 1
    zoom_step = 0.1

    # tracking function
    track_fn = dt_obj.track_video(
        video_path, output_dir="./temp",
        save_result=False, display=False,
        filter_classes=filter_classes)

    video_name = os.path.basename(video_path).split(".")[0]

    # Loop over track_fn to retrieve outputs of each frame
    for bbox_details, frame_details in track_fn:
        bboxes, track_ids, _, class_ids = bbox_details
        display_frame, frame_num, _ = frame_details
        # Save raw frames
        # cv2.imwrite("{}/{}_{}.jpg".format(frames_path, video_name, frame_num), display_frame)

        # draw initial bboxes
        bboxes = list(bboxes)
        display_frame = helpers.init_frame(display_frame, bboxes, class_ids)
        display_frame = cv2.resize(display_frame, (x_size, y_size))

        # display initial detections
        cv2.imshow("window", display_frame)
        key = cv2.waitKey(50) & 0xFF  # determines display fps

        # Stop video if "q" pressed
        if key == ord("q"):
            break

        if key & 0xFF == ord("a"):
            print("Annotation Mode opened, video paused!")
            cv2.setMouseCallback('window', mouse_click)
            cv2.waitKey(0)

            # Update Labels if you get any x and y values
            if len(bboxes) != 0:
                print("Saving annotated frames")
                save_annotated_frames(video_name, display_frame, frame_num, annotated_frames_path)
                print("Saving labels of annotated frames")
                update_labels(video_name, frame_num, labels_path, x_size, y_size)

            # If right is clicked and it is desired to delete some labels
            if len(desired_deletes) > 0:
                print("Deleting desired labels")
                delete_labels(video_name, frame_num, labels_path)

            if len(desired_change_name) > 0:
                print("Changing class names of desired labels")
                change_class_name(video_name, frame_num, labels_path)

    # When everything done, release the capture
    cv2.destroyAllWindows()
