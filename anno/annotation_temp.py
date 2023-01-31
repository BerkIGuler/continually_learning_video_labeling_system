import copy
import os
import cv2

zoom_level = 0.1
zoom_step = 0.1
center = None

# To write x and y values & classes
frame_list = []
frame_list_classes = []

# To show added labels frame
display_frame = ""
drawing = False
ix, iy = 0, 0

# To save desired deleting labels
desired_deletes = []

# To change class name
desired_change_name = []
desired_change_point = []

pressed = False
cache = None

def mouse_click(event, x, y, flags, param):
    global frame_list, frame_list_classes, display_frame, drawing, ix, iy,\
        desired_deletes, desired_change_name, zoom_level, zoom_step, pressed, cache

    # Check if you started to hold left click
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Left start: ", x, y)
        ix, iy = x, y
        pressed = True
        cache = copy.deepcopy(display_frame)

    if event == cv2.EVENT_MOUSEMOVE and pressed:
        cv2.rectangle(cache, (ix, iy), (x, y), (0, 0, 255), 2)
        cv2.imshow("window", cache)
        cache = copy.deepcopy(display_frame)
    # Check if you finished holding left click
    if event == cv2.EVENT_LBUTTONUP:
        print("Left release: ", x, y)
        frame_list.append([ix, iy, x, y])
        pressed = False

        # Get the class with keyboard
        key = cv2.waitKey(0)
        if key == ord("1"):
            frame_list_classes.append("Person")
        elif key == ord("2"):
            frame_list_classes.append("Car")

        # Draw bounding box
        cv2.rectangle(display_frame, (ix, iy), (x, y), (0, 0, 255), 2)
        cv2.putText(
            display_frame, frame_list_classes[-1], (ix, iy - 5),
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
            desired_change_name.append("Person")
        elif key == ord("2"):
            desired_change_name.append("Car")
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


def update_labels(frame_num, labels_path):
    global frame_list, frame_list_classes

    # If there is already labeled info, append
    if os.path.exists("{}/{}.txt".format(labels_path, frame_num)):
        file = open("{}/{}.txt".format(labels_path, frame_num), "a")
        cnt = 0
        for i in range(0, len(frame_list)):
            file.write(frame_list_classes[cnt] + "\t")
            file.write(str(frame_list[i][0]) + "\t")
            file.write(str(frame_list[i][1]) + "\t")
            file.write(str(frame_list[i][2]) + "\t")
            file.write(str(frame_list[i][3]) + "\n")
            cnt += 1

    # If there is not any label yet, create and write
    else:
        file = open("{}/{}.txt".format(labels_path, frame_num), "w")
        cnt = 0
        for i in range(0, len(frame_list)):
            file.write(frame_list_classes[cnt] + "\t")
            file.write(str(frame_list[i][0]) + "\t")
            file.write(str(frame_list[i][1]) + "\t")
            file.write(str(frame_list[i][2]) + "\t")
            file.write(str(frame_list[i][3]) + "\n")
            cnt += 1

    # Make frame_list ready for next annotations
    frame_list = []
    frame_list_classes = []


def save_annotated_frames(anno_frame, frame_num, anno_frames_path):
    cv2.imwrite("{}/{}.jpg".format(anno_frames_path, frame_num), anno_frame)


def delete_labels(frame_num, labels_path):
    global desired_deletes

    lines_list = []
    removal_list = []

    # Open file to read
    f1 = open("{}/{}.txt".format(labels_path, frame_num), "r")

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
    f2 = open("{}/{}.txt".format(labels_path, frame_num), "w")

    for i in range(len(lines_list)):
        if i not in removal_list:
            f2.write(lines_list[i])

    # Prepare desired_deletes for next frames
    desired_deletes = []


def change_class_name(frame_num, labels_path):
    global desired_change_name, desired_change_point

    lines_list = []
    changed_line_list = []

    # Open file
    f1 = open("{}/{}.txt".format(labels_path, frame_num), "r")

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
    f2 = open("{}/{}.txt".format(labels_path, frame_num), "w")

    for line in changed_line_list:
        f2.write(line)

    # Prepare them for next frames
    desired_change_name = []
    desired_change_point = []


def annotation_from_local_video(
        video_path, fps, x_size, y_size,
        frames_path, labels_path, annotated_frames_path):
    global frame_list, display_frame, desired_deletes, desired_change_name, zoom_level, zoom_step
    # Zoom level and step size for each scroll
    zoom_level = 1
    zoom_step = 0.1

    # Capture Video
    captured = cv2.VideoCapture(video_path)

    frame_num = 0
    while True:
        # Capture frame-by-frame
        ret, frame = captured.read()
        frame = cv2.resize(frame, (x_size, y_size))
        display_frame = frame
        # Get the size of the image
        rows, cols, _ = display_frame.shape
        # Get the center of the image
        center = (cols // 2, rows // 2)
        # Display the resulting frame
        cv2.imshow("window", frame)

        # !!! Save raw frames
        # cv2.imwrite("{}/{}.jpg".format(frames_path, frame_num), frame)
        print(frame_num)

        key = cv2.waitKey(fps)  # fps variable is actually states the delay in milliseconds

        # Stop video if "q" pressed
        if key & 0xFF == ord("q"):
            break

        if key & 0xFF == ord("a"):
            print("Annotation Mode opened, video paused!")
            cv2.setMouseCallback('window', mouse_click)
            key = cv2.waitKey(0) & 0xFF
            cv2.setMouseCallback('window', mouse_click)
            # Setting zoom level and step size to their original values
            zoom_level = 1
            zoom_step = 0.1

            # Update Labels if you get any x and y values
            if len(frame_list) != 0:
                print("Saving annotated frames")
                save_annotated_frames(display_frame, frame_num, annotated_frames_path)
                print("Saving labels of annotated frames")
                update_labels(frame_num, labels_path)

            # If right is clicked and it is desired to delete some labels
            if len(desired_deletes) > 0:
                print("Deleting desired labels")
                delete_labels(frame_num, labels_path)

            if len(desired_change_name) > 0:
                print("Changing class names of desired labels")
                change_class_name(frame_num, labels_path)

        frame_num += 1

    # When everything done, release the capture
    captured.release()
    cv2.destroyAllWindows()
