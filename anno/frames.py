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
