import cv2
import cfg
import math

MAX_DISTANCE = 1.5
# opencv uses BGR by default
RED_RGB = (0, 0, 255)


class BBox:
    """Bounding Box Class

    A class to store information related to a bounding box in an image.
    It includes properties like coordinates, class id, color, track id,
    width, height and state of the box.

    Attributes:
        coords (list): list of 4 integers representing x1, y1, x2, y2
            coordinates of the box.
        color (str): color of the bounding box.
        class_id (int): class id of the object the bounding box represents.
        track_id (int): track id of the bounding box.
        frame_width (int): width of the frame in pixels.
        frame_height (int): height of the frame in pixels.
        state (str): state of the bounding box, default "passive".

    """

    def __init__(self, coords=None, color=None, class_id=None,
                 track_id=None, frame_width=None, frame_height=None, state="passive"):
        """
        Initializes the BBox object with the given attributes.

        Args:
            coords (list, optional): list of 4 integers representing
                x1, y1, x2, y2 coordinates of the box.
            color (str, optional): color of the bounding box.
            class_id (int, optional): class id of the object the
                bounding box represents.
            track_id (int, optional): track id of the bounding box.
            frame_width (int, optional): width of the frame in pixels.
            frame_height (int, optional): height of the frame in pixels.
            state (str, optional): state of the bounding box, default "passive".

        """
        self.coords = coords
        self.color = color
        self.class_id = class_id
        self.track_id = track_id
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.state = state

    def reshape(self, new_frame_h, new_frame_w):
        """
        Reshape the bounding box based on new frame height and width.

        Args:
            new_frame_h (int): height of the new frame in pixels.
            new_frame_w (int): width of the new frame in pixels.

        """
        x1, y1, x2, y2 = self.coords
        new_x1 = round((x1 / self.frame_width) * new_frame_w)
        new_x2 = round((x2 / self.frame_width) * new_frame_w)
        new_y1 = round((y1 / self.frame_height) * new_frame_h)
        new_y2 = round((y2 / self.frame_height) * new_frame_h)
        self.coords = [new_x1, new_y1, new_x2, new_y2]
        self.frame_width = new_frame_w
        self.frame_height = new_frame_h

    def __repr__(self):
        """
        String representation of the BBox object.

        Returns:
            str: String representation of the BBox object.

        """
        repr_str = ""
        for attribute, value in self.__dict__.items():
            repr_str += f"{attribute}: {value}\n"
        return repr_str


def init_boxes(bboxes, ids, track_ids, x_size, y_size):
    """Initializes the bounding boxes based on the given parameters.

    Args:
    bboxes: A list of bounding box coordinates or an object that can be
        converted to a list.
    ids: A list of class ids for each bounding box.
    track_ids: A list of tracking ids for each bounding box.
    x_size: The width of the frame that the boxes belong to.
    y_size: The height of the frame that the boxes belong to.

    Returns:
    A list of initialized BBox objects.
    """

    boxes = []
    if not isinstance(bboxes, list):
        bboxes = bboxes.tolist()

    for bbox, c_id, t_id in zip(bboxes, ids, track_ids):
        boxes.append(
            BBox(
                coords=bbox, color=cfg.id_to_color[c_id],
                class_id=c_id, track_id=t_id, frame_height=y_size,
                frame_width=x_size, state="passive"
                )
            )
    return boxes


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
            cv2.rectangle(frame, box.coords[:2], box.coords[2:], RED_RGB, 1)
            cv2.putText(
                frame, cfg.id_to_class[box.class_id], (box.coords[0], box.coords[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED_RGB, 1,
                cv2.LINE_4)


def xywh_to_xyxy(x, y, w, h):
    x1 = min(round(x + w / 2), round(x - w / 2))
    x2 = max(round(x + w / 2), round(x - w / 2))
    y1 = max(round(y + h / 2), round(y - h / 2))
    y2 = min(round(y + h / 2), round(y - h / 2))

    return [x1, y1, x2, y2]


def select_class_by_keyboard(key):
    if key == ord("1"):
        selected_class_id = 10
    elif key == ord("2"):
        selected_class_id = 20
    elif key == ord("3"):
        selected_class_id = 30
    elif key == ord("4"):
        selected_class_id = 40
    elif key == ord("5"):
        selected_class_id = 50
    else:
        raise ValueError("undefined class_id... Enter a valid key")

    return selected_class_id


def xyxy_to_yolo(box, return_type="str"):
    """Converts xyxy coordinates to YOLO format.

    Given a box object with xyxy coordinates, this function calculates the
    center point `(xc, yc)`, width `w`, and height `h` in the YOLO format.
    The function can return the result as either a string or a tuple,
    based on the `return_type` argument.

    Args:
        box (Box): An instance of the `Box` class with xyxy coordinates.
        return_type (str, optional): The format of the returned value.
        Must be either "str" or "tuple".
            Defaults to "str".

    Returns:
        str or tuple: The YOLO-formatted string or tuple of values,
        depending on `return_type`. The string is of the form
        `"{class_id} {xc:.5} {yc:.5} {w:.5} {h:.5}"`, and the tuple is of
        the form `(class_id, xc, yc, w, h)`.

    Raises:
        ValueError: If `return_type` is neither "str" nor "tuple".
    """
    x1, y1, x2, y2 = box.coords
    w = abs(x2 - x1) / box.frame_width
    h = abs(y2 - y1) / box.frame_height
    xc = (x1 + x2) / (2 * box.frame_width)
    yc = (y1 + y2) / (2 * box.frame_height)
    if return_type == "str":
        yolo_formatted = f"{box.class_id} {xc:.5} {yc:.5} {w:.5} {h:.5}"
    elif return_type == "tuple":
        yolo_formatted = box.class_id, xc, yc, w, h
    else:
        raise ValueError("return_type must be either 'str' or 'tuple'")
    return yolo_formatted


def to_ordered_xyxy(ix, iy, x, y):
    """Converts a pair of coordinates to an ordered xyxy format.

    Given two sets of x and y coordinates, this function arranges them
    in the xyxy format, where (x1, y1) is the top left corner, and
    (x2, y2) is the bottom right corner.

    Args:
        ix (float): The x-coordinate of the first point.
        iy (float): The y-coordinate of the first point.
        x (float): The x-coordinate of the second point.
        y (float): The y-coordinate of the second point.

    Returns:
        list: List of four elements `[x1, y1, x2, y2]`, where `(x1, y1)`
        is the top left corner, and `(x2, y2)` is the bottom right corner.
    """
    x1, x2 = (ix, x) if ix < x else (x, ix)
    y1, y2 = (iy, y) if iy < y else (y, iy)

    return [x1, y1, x2, y2]


def modify_active_box(boxes, task="delete", new_class_id=None):
    for i, box in enumerate(boxes):
        if box.state == "active":
            if task == "delete":
                boxes.remove(box)
            elif task == "update_label" and new_class_id is not None:
                try:
                    box.color = cfg.id_to_color[new_class_id]
                    box.class_id = new_class_id
                except KeyError("invalid_new_class_id") as err:
                    print('enter a valid class id to assign a new label', err)
            else:
                raise ValueError("task must be either 'delete' or 'update_label'")


def activate_box(boxes, x, y, x_size, y_size):
    """Activates the closest box to a given point.

    Given a list of boxes, the function takes a point specified
    by its x and y coordinates, as well as the dimensions of
    the coordinate system. The function first normalizes the
    point's coordinates, and calculates the Euclidean distance
    from each box center. Only one box is assigned an active status
    at a time

    Args:
        boxes (list): List of boxes. Each box is a BBox object
        x (float): The x-coordinate of the point.
        y (float): The y-coordinate of the point.
        x_size (float): The size of the x-dimension of the coordinate system.
        y_size (float): The size of the y-dimension of the coordinate system.

    Returns:
        None
    """
    norm_x, norm_y = x / x_size, y / y_size
    closest_dist = MAX_DISTANCE
    candidate_box_id = None
    already_active_id = None
    for i, box in enumerate(boxes):
        c_id, xc, yc, w, h = xyxy_to_yolo(box, return_type="tuple")
        euc_dist = math.sqrt((xc - norm_x) ** 2 + (yc - norm_y) ** 2)
        if box.state == "active":
            already_active_id = i
        if euc_dist < closest_dist and in_box(norm_x, norm_y, xc, yc, w, h):
            closest_dist = euc_dist
            candidate_box_id = i
            box.state = "active"

    if candidate_box_id is not None:
        for i, box in enumerate(boxes):
            if i != candidate_box_id and box.state == "active":
                box.state = "passive"

    return already_active_id == candidate_box_id


def in_box(norm_x, norm_y, xc, yc, w, h):
    """Determines if a point is within a box in normalized coordinates.

    The function takes the coordinates of a point in a
    normalized coordinate system, where the values range from 0 to 1,
    The function returns `True` if the point is within the box,
    and `False` otherwise.

    Args:
        norm_x (float): The x-coordinate of the point in
            the normalized coordinate system.
        norm_y (float): The y-coordinate of the point in
            the normalized coordinate system.
        xc (float): The x-coordinate of the center of the box.
        yc (float): The y-coordinate of the center of the box.
        w (float): The width of the box.
        h (float): The height of the box.

    Returns:
        bool: `True` if the point is within the box, `False` otherwise.
    """
    left_x = xc - w / 2 if xc - w / 2 > 0 else 0
    right_x = xc + w / 2 if xc + w / 2 < 1 else 1
    top_y = yc - h / 2 if yc - h / 2 > 0 else 0
    bottom_y = yc + h / 2 if yc + h / 2 < 1 else 1

    if bottom_y > norm_y > top_y and right_x > norm_x > left_x:
        status = True
    else:
        status = False

    return status
