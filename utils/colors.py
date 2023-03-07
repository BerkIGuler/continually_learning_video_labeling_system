import colorsys
import random


def hsv_to_rgb(h, s, v):
    (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
    return f"({int(255 * r)}, {int(255 * g)}, {int(255 * b)})"


def get_distinct_colors(n):
    hue_partition = 1.0 / (n + 1)
    cols = [hsv_to_rgb(hue_partition * value, 1.0, 1.0) for value in range(0, n)]
    random.shuffle(cols)
    return cols


colors = get_distinct_colors(48)

for i, color in enumerate(colors):
    print(f"{i}: {color}")
