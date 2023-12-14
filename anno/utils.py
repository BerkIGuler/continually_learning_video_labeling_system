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
        if w != 0.0 and h != 0.0:
            return yolo_formatted
        else:
            return None
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


def get_xy_to_box_position(box, x, y, error_margin=7):
    """gets cursor's position wrt box object

    Args:
        box (box object): box object agains which
            to compare relative position
        x (int): The x-coordinate of the cursor
        y (int): The y-coordinate of the cursor
        error_margin (int): vertical and/or horizantal
            error margin used to decide the relative position

    Returns:
        str or NoneType: one of [up, down, left, right,
            upper_left, upper_right, down_left, down_right]
            or None
    """
    x1, y1, x2, y2 = box.coords
    if (x1 + error_margin) < x < (x2 - error_margin) and abs(y - y1) < error_margin:
        pos = "up"
    elif (x1 + error_margin) < x < (x2 - error_margin) and abs(y - y2) < error_margin:
        pos = "down"
    elif (y1 + error_margin) < y < (y2 - error_margin) and abs(x - x1) < error_margin:
        pos = "left"
    elif (y1 + error_margin) < y < (y2 - error_margin) and abs(x - x2) < error_margin:
        pos = "right"
    elif abs(x - x1) < error_margin and abs(y - y1) < error_margin:
        pos = "upper_left"
    elif abs(x - x2) < error_margin and abs(y - y1) < error_margin:
        pos = "upper_right"
    elif abs(x - x1) < error_margin and abs(y - y2) < error_margin:
        pos = "down_left"
    elif abs(x - x2) < error_margin and abs(y - y2) < error_margin:
        pos = "down_right"
    elif (x1 + error_margin) < x < (x2 - error_margin) and \
            (y1 + error_margin) < y < (y2 - error_margin):
        pos = "mid"
    else:
        pos = None
    return pos
