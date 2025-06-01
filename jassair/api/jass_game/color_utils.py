import colorsys

def generate_distinct_colors(n):
    hsv_colors = [(i / n, 1.0, 1.0) for i in range(n)]
    rgb_colors = [tuple(int(c * 255) for c in colorsys.hsv_to_rgb(*hsv)) for hsv in hsv_colors]
    return [tuple(reversed(rgb)) for rgb in rgb_colors]
