import cv2
import cfg

import anno


def init_frame(frame, boxes):
    """Initialize a video frame with boxes.

    Args:
        frame (numpy.ndarray): A video frame.
        boxes (list[BBox]): A list of bounding boxes to be drawn on the frame.

    Returns:
        None. The `frame` is updated with the boxes.
    """
    # if boxes empty
    if not boxes:
        return
    frame_h, frame_w = frame.shape[:2]
    for i, box in enumerate(boxes):
        if box.frame_height != frame_h or box.frame_width != frame_w:
            box.reshape(frame_h, frame_w)
        if box.state == "passive":
            cv2.rectangle(
                frame, box.coords[:2], box.coords[2:],
                cfg.id_to_color[box.class_id], 1)
            cv2.putText(
                frame, cfg.id_to_class[box.class_id], (box.coords[0], box.coords[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, cfg.id_to_color[box.class_id], 1,
                cv2.LINE_4)
        elif box.state == "active":
            cv2.rectangle(frame, box.coords[:2], box.coords[2:], anno.RED_RGB, 2)
            cv2.putText(
                frame, cfg.id_to_class[box.class_id], (box.coords[0], box.coords[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, anno.RED_RGB, 2,
                cv2.LINE_4)


def show_frame(
        frame, window, fps=None,
        current_frame_id=None, total_frames=None,
        mode="view", ses_label_count=None, init_label_count=None):
    if mode == "view":
        # frame count line
        cv2.line(
            frame, (10, 12), (140, 12),
            [85, 45, 255], 10)
        cv2.putText(
            frame,
            f'fps:{int(fps)}|frame:{int(current_frame_id)}/{int(total_frames)}',
            (11, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, [225, 255, 255],
            thickness=1, lineType=cv2.LINE_AA)
        # saved files line
        total = init_label_count + ses_label_count
        cv2.line(
            frame, (10, 24), (140, 24),
            [85, 45, 255], 10)
        cv2.putText(
            frame,
            f'total:{total}|ses:{ses_label_count}',
            (11, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.4, [225, 255, 255],
            thickness=1, lineType=cv2.LINE_AA)
    elif mode == "annotate":
        cv2.line(
            frame, (10, 12), (140, 12),
            [85, 45, 255], 10)
        cv2.putText(
            frame, f'Annotation Mode',
            (11, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, [225, 255, 255],
            thickness=1, lineType=cv2.LINE_AA)
    elif mode == "send":
        sent_count = init_label_count + ses_label_count
        cv2.line(
            frame, (600, 700), (1250, 700),
            [85, 45, 255], 50)
        cv2.putText(
            frame, f"Sending {sent_count} images to remote machine",
            (600, 690), cv2.FONT_HERSHEY_SIMPLEX, 0.7, [225, 255, 255],
            thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(
            frame, f"Please Wait...",
            (770, 715), cv2.FONT_HERSHEY_SIMPLEX, 0.7, [225, 255, 255],
            thickness=2, lineType=cv2.LINE_AA)

    elif mode == "after_send":
        cv2.line(
            frame, (600, 700), (1250, 700),
            [85, 45, 255], 50)
        cv2.putText(
            frame, f"Files sent to remote machine",
            (675, 690), cv2.FONT_HERSHEY_SIMPLEX, 0.7, [225, 255, 255],
            thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(
            frame, f"Resuming Operation...",
            (720, 715), cv2.FONT_HERSHEY_SIMPLEX, 0.7, [225, 255, 255],
            thickness=2, lineType=cv2.LINE_AA)

    elif mode == "recv":
        cv2.line(
            frame, (600, 700), (1250, 700),
            [85, 45, 255], 50)
        cv2.putText(
            frame, f"Receiving the model file from remote",
            (600, 690), cv2.FONT_HERSHEY_SIMPLEX, 0.7, [225, 255, 255],
            thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(
            frame, f"Please Wait...",
            (770, 715), cv2.FONT_HERSHEY_SIMPLEX, 0.7, [225, 255, 255],
            thickness=2, lineType=cv2.LINE_AA)
    elif mode == "after_recv":
        cv2.line(
            frame, (600, 700), (1250, 700),
            [85, 45, 255], 50)
        cv2.putText(
            frame, f"Resuming operation...",
            (740, 690), cv2.FONT_HERSHEY_SIMPLEX, 0.7, [225, 255, 255],
            thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(
            frame, f"Please restart to use updated weights...",
            (600, 715), cv2.FONT_HERSHEY_SIMPLEX, 0.7, [225, 255, 255],
            thickness=2, lineType=cv2.LINE_AA)
    cv2.imshow(window, frame)
