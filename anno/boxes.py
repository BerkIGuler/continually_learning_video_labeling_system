import math

import cfg
from anno.utils import xyxy_to_yolo, in_box, get_xy_to_box_position
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

    def get_scaled_coords(self, scaling_side, x, y, ix=None, iy=None):
        x1, y1, x2, y2 = self.coords
        if scaling_side == "up":
            new_coords = x1, y, x2, y2
        elif scaling_side == "down":
            new_coords = x1, y1, x2, y
        elif scaling_side == "left":
            new_coords = x, y1, x2, y2
        elif scaling_side == "right":
            new_coords = x1, y1, x, y2
        elif scaling_side == "upper_left":
            new_coords = x, y, x2, y2
        elif scaling_side == "upper_right":
            new_coords = x1, y, x, y2
        elif scaling_side == "down_left":
            new_coords = x, y1, x2, y
        elif scaling_side == "down_right":
            new_coords = x1, y1, x, y
        elif scaling_side == "mid":
            x_translation = x - ix
            y_translation = y - iy
            new_coords = (x1 + x_translation,
                          y1 + y_translation,
                          x2 + x_translation,
                          y2 + y_translation)
        else:
            raise ValueError("invalid scaling side arg")

        return new_coords

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


def get_cursor_to_abox_status(x, y, boxes):
    """gets cursor's position wrt the current active box

    Args:
        x (float): The x-coordinate of the cursor.
        y (float): The y-coordinate of the cursor.
        boxes (list): List of box objects

    Returns:
        Two-tuple of the active box object and string position
    """
    a_box_inds = [box_idx for box_idx in range(len(boxes)) if boxes[box_idx].state == "active"]
    assert len(a_box_inds) < 2, "there must be one active box at most at a time"
    if a_box_inds:
        a_box_idx = a_box_inds[0]
        a_box = boxes[a_box_idx]
        pos = get_xy_to_box_position(a_box, x, y)
        return a_box, pos
    else:
        return None, None


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
        str: action to be taken
    """
    norm_x, norm_y = x / x_size, y / y_size
    closest_dist = anno.MAX_DISTANCE
    closest_box_id = -1
    already_active_id = -1
    for i, box in enumerate(boxes):
        c_id, xc, yc, w, h = xyxy_to_yolo(box, return_type="tuple")
        if box.state == "active":
            already_active_id = i
        # if the cursor in the current box
        if in_box(norm_x, norm_y, xc, yc, w, h):
            euc_dist = math.sqrt((xc - norm_x) ** 2 + (yc - norm_y) ** 2)
            if euc_dist < closest_dist:
                closest_dist = euc_dist
                closest_box_id = i

    for i, box in enumerate(boxes):
        if i == closest_box_id:
            box.state = "active"
        else:
            box.state = "passive"

    if already_active_id == closest_box_id and already_active_id != -1:
        action = "delete"
    else:
        action = "wait_key"
    return action
