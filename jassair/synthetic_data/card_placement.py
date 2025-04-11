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
    rot_matrix[0, 2] += (new_w / 2) - center[0]
    rot_matrix[1, 2] += (new_h / 2) - center[1]

    # Perform rotation
    rotated_fg = cv.warpAffine(img, rot_matrix, (new_w, new_h), borderMode=cv.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    return rotated_fg


def add_drop_shadow(card_rgba, offset=(10, 10), blur=15, shadow_intensity=0.5):
    h, w = card_rgba.shape[:2]

    # Create a blank shadow canvas (with padding to account for shadow offset)
    shadow = np.zeros((h + offset[1], w + offset[0], 4), dtype=np.uint8)

    # Extract alpha channel from the card
    shadow_alpha = card_rgba[:, :, 3]
    shadow_mask = np.zeros_like(shadow[:, :, 3])

    # Place shadow alpha into the shadow mask
    shadow_mask[offset[1]:offset[1] + h, offset[0]:offset[0] + w] = shadow_alpha

    # Smooth the shadow mask using Gaussian blur
    shadow_mask = cv.GaussianBlur(shadow_mask, (0, 0), blur)

    # Create semi-transparent black shadow (RGBA)
    shadow[:, :, :3] = 0
    shadow[:, :, 3] = (shadow_mask * shadow_intensity).astype(np.uint8)

    # Place the card on a transparent background
    canvas = np.zeros_like(shadow, dtype=np.uint8)
    canvas[offset[1]:offset[1] + h, offset[0]:offset[0] + w] = card_rgba

    # Add the shadow to the card with transparency blending
    combined = cv.addWeighted(shadow, 1.0, canvas, 1.0, 0)

    # Final blend respecting the alpha channel
    final_rgba = np.zeros_like(combined, dtype=np.uint8)
    final_rgba[:, :, :3] = cv.addWeighted(shadow[:, :, :3], 1, canvas[:, :, :3], 1, 0)
    final_rgba[:, :, 3] = np.maximum(shadow[:, :, 3], canvas[:, :, 3])

    return final_rgba
