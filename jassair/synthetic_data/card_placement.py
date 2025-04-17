import numpy as np
import cv2 as cv


def rotate_image(img, angle):
    """Rotates the image without cropping any part of it."""
    h, w = img.shape[:2]
    center = (w // 2, h // 2)

    # Compute the bounding box of the rotated image
    rot_matrix = cv.getRotationMatrix2D(center, angle, 1.0)
    cos = np.abs(rot_matrix[0, 0])
    sin = np.abs(rot_matrix[0, 1])

    # Compute new bounding box dimensions
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # Adjust the rotation matrix to consider the new image size
    rot_matrix[0, 2] += (new_w // 2) - center[0]
    rot_matrix[1, 2] += (new_h // 2) - center[1]

    # Perform rotation
    rotated_fg = cv.warpAffine(img, rot_matrix, (new_w, new_h), borderMode=cv.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    return rotated_fg


def add_drop_shadow(card_rgba, offset=(10, 10), blur=15, shadow_intensity=0.5):
    h_o, w_o = offset
    h, w = card_rgba.shape[:2]

    shadow = np.zeros((h + 2*h_o, w + 2*w_o, 4), dtype=np.uint8)

    shadow_alpha = card_rgba[:, :, 3]
    mask = shadow_alpha < 100
    card_rgba[mask] = 0

    shadow_mask = np.zeros_like(shadow[:, :, 3])
    shadow_mask[h_o:h_o + h, w_o:w_o + w] = shadow_alpha
    shadow_mask = cv.GaussianBlur(shadow_mask, (0, 0), blur)

    # Create semi-transparent black shadow (RGBA)
    shadow[:, :, 3] = (shadow_mask * shadow_intensity).astype(np.uint8)

    # Place the card on a transparent background
    canvas = np.zeros_like(shadow, dtype=np.uint16)
    canvas[h_o:h_o + h, w_o:w_o + w] = card_rgba
    canvas[:, :, 3] += shadow[:, :, 3]
    return np.clip(canvas, 0, 255).astype(np.uint8)


def get_yolo_boxes(regions: np.ndarray, num_cards: int) -> list[str]:
    result = []
    h, w = regions.shape[:2]
    for index in range(1, num_cards + 1):
        y_indices, x_indices = np.where(regions == index)
        min_x, max_x = x_indices.min(), x_indices.max()
        min_y, max_y = y_indices.min(), y_indices.max()
        cx = (min_x + max_x) / (2 * w)
        cy = (min_y + max_y) / (2 * h)
        bw = (max_x - min_x) / w
        bh = (max_y - min_y) / h
        result.append(f"{cx} {cy} {bw} {bh}")
    return result
