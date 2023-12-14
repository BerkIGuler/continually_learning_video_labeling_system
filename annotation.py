import copy
import os
import cv2
import numpy as np
from loguru import logger
from datetime import datetime

import cfg
import asone

import anno
from anno import (select_class_by_keyboard, init_boxes, init_frame, show_frame,
                  BBox, to_ordered_xyxy, activate_box, modify_active_box,
                  setup_tracker, get_cursor_to_abox_status)

from network.client import TCPClient

# global array shared and displayed by the functions
display_frame = np.array([])
ix, iy = 0, 0  # initial cursor point when mouse left-clicked
boxes = []  # store all box object belonging to current frame

pressed = False  # if left mouse clicked
# flag to raise when the program waits for a keyboard event
waiting_key = False
frame_cache = None  # used to store a frame array
empty_frame = np.array([])  # frame without any boxes drawn

# to keep where the cursor lies wrt to active box
cursor_to_a_box_pos = None
# to store active box
a_box = None

counter = 0

cfg.init_config()
# store global label number counters
initial_label_count, session_label_count = anno.init_frame_counters(
    cfg.config["ANNOTATED_FRAMES_DIR"],
    cfg.config["ANNOTATED_LABELS_DIR"])


def mouse_click(event, x, y, flags, param):
    """what to do on mouse click event"""

    global boxes, display_frame, ix, iy, \
        pressed, frame_cache, empty_frame, \
        waiting_key, cursor_to_a_box_pos, a_box

    if event == cv2.EVENT_LBUTTONDOWN:
        pressed = True
        boxed_frame = copy.deepcopy(empty_frame)
        a_box, cursor_to_a_box_pos = get_cursor_to_abox_status(x, y, boxes)
        # if cursor_to_a_box_pos is None,
        # there is not any active box yet
        if not cursor_to_a_box_pos:
            ix, iy = x, y
        # if the active box is clicked in the middle
        # enter move bbox mode
        elif cursor_to_a_box_pos == "mid":
            ix, iy = x, y
            # remove the active box so that it
            # is redrawn during mouse move event
            boxes.remove(a_box)
        # scale active box in one of 8 directions
        else:
            boxes.remove(a_box)
        # copy frame
        init_frame(boxed_frame, boxes)
        frame_cache = copy.deepcopy(boxed_frame)

    elif pressed and event == cv2.EVENT_MOUSEMOVE:
        # draw new bbox
        if not cursor_to_a_box_pos:
            cv2.rectangle(frame_cache, (ix, iy), (x, y), (0, 0, 255), 1)
        # move bbox
        elif cursor_to_a_box_pos == "mid":
            x1, y1, x2, y2 = a_box.get_scaled_coords(cursor_to_a_box_pos, x, y, ix, iy)
            cv2.rectangle(frame_cache, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # scale in one of 8 directions
        else:
            x1, y1, x2, y2 = a_box.get_scaled_coords(cursor_to_a_box_pos, x, y)
            cv2.rectangle(frame_cache, (x1, y1), (x2, y2), (0, 0, 255), 2)

        show_frame(frame_cache, "window", mode="annotate")
        boxed_frame = copy.deepcopy(empty_frame)
        init_frame(boxed_frame, boxes)
        frame_cache = copy.deepcopy(boxed_frame)

    elif event == cv2.EVENT_LBUTTONUP:
        pressed = False

        # new box added
        if not cursor_to_a_box_pos:
            key = cv2.waitKey(1000) & 0xFF  # wait for new class if not continue not to block
            if key != 255 and key != asone.ESC_KEY:
                selected_class_id = select_class_by_keyboard(key)
                current_box = BBox(
                    coords=to_ordered_xyxy(ix, iy, x, y),
                    color=cfg.id_to_color[selected_class_id],
                    class_id=selected_class_id,
                    frame_width=cfg.config["X_SIZE"],
                    frame_height=cfg.config["Y_SIZE"]
                )
                boxes.append(current_box)
        # move box mode
        elif cursor_to_a_box_pos == "mid":
            new_coords = a_box.get_scaled_coords(cursor_to_a_box_pos, x, y, ix, iy)
            a_box.coords = list(new_coords)
            boxes.append(a_box)
        # scale box mde
        else:
            new_coords = a_box.get_scaled_coords(cursor_to_a_box_pos, x, y)
            a_box.coords = list(new_coords)
            boxes.append(a_box)

        display_frame = copy.deepcopy(empty_frame)
        init_frame(display_frame, boxes)
        show_frame(display_frame, "window", mode="annotate")

    elif event == cv2.EVENT_RBUTTONDOWN:
        # modifies boxes' states as well
        action = activate_box(boxes, x, y, cfg.config["X_SIZE"], cfg.config["Y_SIZE"])

        display_frame = copy.deepcopy(empty_frame)
        init_frame(display_frame, boxes)
        show_frame(display_frame, "window", mode="annotate")
        # delete active box if clicked on it twice
        if action == "delete":
            modify_active_box(
                boxes, task="delete")
        # update bbox class
        elif not waiting_key:
            waiting_key = True
            key = cv2.waitKey(0) & 0xFF
            waiting_key = False
            if key != asone.ESC_KEY:
                selected_class_id = select_class_by_keyboard(key)

                # could be None
                if selected_class_id:
                    modify_active_box(
                        boxes, task="update_label",
                        new_class_id=selected_class_id)

        display_frame = copy.deepcopy(empty_frame)
        init_frame(display_frame, boxes)
        show_frame(display_frame, "window", mode="annotate")


def annotate(video_path=None):
    global boxes, display_frame, empty_frame, initial_label_count, session_label_count

    frames_path = cfg.config["FRAMES_DIR"]  # raw frames
    anno_frames_path = cfg.config["ANNOTATED_FRAMES_DIR"]  # annotated frames
    labels_path = cfg.config["LABELS_DIR"]  # yolo+ds labels
    anno_labels_path = cfg.config["ANNOTATED_LABELS_DIR"]  # annotated labels
    x_size_window = cfg.config["X_SIZE"]
    y_size_window = cfg.config["Y_SIZE"]

    if not cfg.config["REAL_TIME"]:
        video_name = os.path.basename(video_path).split(".")[0]
    else:
        # generate unique rt vid save name
        video_name = str(datetime.now()).replace(" ", "")

    # window configuration
    cv2.namedWindow("window", cv2.WINDOW_GUI_NORMAL)
    cv2.resizeWindow("window", x_size_window, y_size_window)

    track_fn = setup_tracker(
        real_time=cfg.config["REAL_TIME"], video_path=video_path)

    for bbox_details, frame_details, action in track_fn:

        if action == "stream":  # keep reading next frame
            bboxes, track_ids, _, class_ids = bbox_details
            display_frame, frame_id, frame_count, fps = frame_details

        elif action == "annotation":  # stop reading frames and annotate
            cv2.setMouseCallback('window', mouse_click)
            logger.info("Annotation Mode opened, video paused!")
            key = cv2.waitKey(0) & 0xFF  # stop the video
            while key != asone.ESC_KEY:  # press ESC to quit anno mode
                key = cv2.waitKey(0) & 0xFF
            # deactivate mouse event trigger by setting it dummy func.
            cv2.setMouseCallback('window', lambda *args: None)

            # if there are boxes after annotation of curr. frame save
            if cfg.config["SAVE_EDITED_FRAMES"] and len(boxes) != 0:
                new_label_count = anno.interact.save_labels(
                        boxes=boxes,
                        anno_im_dir=anno_frames_path,
                        anno_labels_dir=anno_labels_path,
                        frame_id=frame_id,
                        im=empty_frame,
                        vid_name=video_name)

                # gets incremented by one
                session_label_count += new_label_count
                # empty boxes for next frame annotation
                boxes = []

            # if the track_fn yields a value different from stream
            # a frame is not read hence continue for next frame
            continue

        elif action == "send":
            logger.info('Send mode')
            show_frame(
                empty_frame, "window", ses_label_count=session_label_count,
                init_label_count=initial_label_count, mode="send")
            cv2.waitKey(1)
            client = TCPClient(cfg.config['HOST'], cfg.config['PORT'])
            client.send()
            show_frame(empty_frame, "window", mode="after_send")
            cv2.waitKey(3000)
            anno.interact.flush_sent_files()  # delete sent files
            initial_label_count, session_label_count = 0, 0  # reset counters

        elif action == 'receive':
            logger.info('Entered receive mode')
            show_frame(empty_frame, "window", mode="recv")
            cv2.waitKey(1)
            client = TCPClient(cfg.config['HOST'], cfg.config['PORT'])
            client.receive()
            show_frame(empty_frame, "window", mode="after_recv")
            cv2.waitKey(4000)
            anno.interact.update_weights()

        original_height, original_width = display_frame.shape[:2]
        boxes = init_boxes(
            bboxes, class_ids, track_ids,
            original_width, original_height)
        display_frame = cv2.resize(display_frame, (x_size_window, y_size_window))
        empty_frame = copy.deepcopy(display_frame)
        init_frame(display_frame, boxes)
        show_frame(
            display_frame, "window", fps, frame_id,
            frame_count, "view",
            session_label_count, initial_label_count)

        if cfg.config["SAVE_RAW"]:
            anno.interact.save_labels(
                boxes=boxes,
                raw_im_dir=frames_path,
                raw_labels_dir=labels_path,
                frame_id=frame_id,
                im=empty_frame,
                vid_name=video_name)

    cv2.destroyAllWindows()
