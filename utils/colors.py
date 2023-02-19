import colorsys


def HSVToRGB(h, s, v):
    (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
    return f"({int(255 * r)}, {int(255 * g)}, {int(255 * b)})"


def getDistinctColors(n):
    huePartition = 1.0 / (n + 1)
    return (HSVToRGB(huePartition * value, 1.0, 1.0) for value in range(0, n))


for i, color in enumerate(getDistinctColors(80)):
    print(f"{i}: {color}")