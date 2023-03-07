import math

import cfg
from anno.utils import xyxy_to_yolo, in_box
import anno


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

    def __init__(
            self, coords=None, color=None, class_id=None,
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
            box.state = "passive"


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
    closest_dist = anno.MAX_DISTANCE
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
