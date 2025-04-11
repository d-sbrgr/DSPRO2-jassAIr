from __future__ import annotations

import random

import numpy as np
import cv2 as cv
from numpy.random import randint


def augment_image(image, augmentations: list[Augmentation]):
    """Applies random augmentations."""
    aug = list(augmentations)
    random.shuffle(aug)
    threshold = 0
    for augmentation in aug:
        threshold += random.random()
        if threshold > 0.6:
            image = augmentation(image)
            threshold = 0
    return image


class Augmentation:
    def __call__(self, image) -> np.ndarray:
        raise NotImplementedError


class RotateMult90(Augmentation):
    def __call__(self, image) -> np.ndarray:
        k = random.randint(0, 3)
        rotated = np.ascontiguousarray(np.rot90(image, k))
        return rotated


class GaussianBlur(Augmentation):
    def __init__(self, max_kernel: int = 30):
        self.max_kernel = max_kernel

    def __call__(self, image) -> np.ndarray:
        kernel_size = random.choice(range(1, self.max_kernel, 2))  # Odd kernel size
        return cv.GaussianBlur(image, (kernel_size, kernel_size), 0)


class NoiseNormal(Augmentation):
    def __init__(self, noise_level: int = 0.1):
        self.noise_level = int(noise_level * 255)

    def __call__(self, image) -> np.ndarray:
        noise = np.random.normal(0, self.noise_level, image.shape).astype(np.float32)
        noisy_image = image.astype(np.float32) + noise
        noisy_image = np.clip(noisy_image, 0, 255)
        return noisy_image.astype(np.uint8)


class WhiteBalanceShift(Augmentation):
    def __init__(self, shift_range: float = 0.5):
        shift_range = int(shift_range * 255)
        self.shift_range = (-shift_range, shift_range)

    def __call__(self, image) -> np.ndarray:
        b, g, r = cv.split(image)
        b = cv.add(b, random.randint(*self.shift_range))
        r = cv.add(r, random.randint(*self.shift_range))
        g = cv.add(g, random.randint(*self.shift_range))
        return cv.merge((b, g, r))


class ColorJitter(Augmentation):
    def __init__(self, brightness: float = 0.2, contrast: float = 0.2, saturation: float = 0.2, hue: float = 0):
        self.brightness = brightness
        self.saturation = saturation
        self.hue = hue
        self.contrast = contrast

    def __call__(self, image) -> np.ndarray:
        img = image.copy().astype(np.uint8)

        # Convert to HSV for brightness/saturation/hue
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV).astype(np.float32)

        # Brightness
        if self.brightness > 0:
            v_scale = random.uniform(1 - self.brightness, 1 + self.brightness)
            hsv[:, :, 2] *= v_scale

        # Saturation
        if self.saturation > 0:
            s_scale = random.uniform(1 - self.saturation, 1 + self.saturation)
            hsv[:, :, 1] *= s_scale

        # Hue
        if self.hue > 0:
            h_shift = random.uniform(-self.hue, self.hue) * 180  # hue range in OpenCV is [0, 180]
            hsv[:, :, 0] = (hsv[:, :, 0] + h_shift) % 180

        hsv = np.clip(hsv, 0, 255)
        img = cv.cvtColor(hsv.astype(np.uint8), cv.COLOR_HSV2BGR)

        # Contrast (in RGB)
        if self.contrast > 0:
            c_scale = random.uniform(1 - self.contrast, 1 + self.contrast)
            mean = np.mean(img, axis=(0, 1), keepdims=True)
            img = np.clip((img - mean) * c_scale + mean, 0, 255)

        return img.astype(np.uint8)


class LightSpots(Augmentation):
    def __init__(self, max_radius: int = 280, min_radius: int = 80, intensity: float = 1.0):
        self.radius_range = (min_radius, max_radius)
        intensity = int(intensity * 255)
        self.intensity = (intensity, intensity, intensity)

    def __call__(self, image) -> np.ndarray:
        h, w = image.shape[:2]

        x, y = random.randint(0, w), random.randint(0, h)
        radius = random.randint(*self.radius_range)
        light_spot = np.zeros((h, w, 3), dtype=np.uint8)
        cv.circle(light_spot, (x, y), radius, self.intensity, -1)

        blur_amount = int(radius * 0.6)  # Blur proportional to radius
        if blur_amount % 2 == 0:
            blur_amount += 1  # Kernel size must be odd for GaussianBlur
        light_spot = cv.GaussianBlur(light_spot, (blur_amount, blur_amount), 0)
        image = cv.addWeighted(image, 1, light_spot, 0.5, 0)

        return image


class LightingGradient(Augmentation):
    def __init__(self, max_strength: float = 0.5):
        self.max_strength = max_strength

    def __call__(self, image) -> np.ndarray:
        h, w = image.shape[:2]
        center = randint(w), randint(h)
        strength = random.uniform(0, self.max_strength)
        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
        max_dist = np.sqrt(center[0]**2 + center[1]**2)
        mask = 1 - (dist_from_center / max_dist)
        mask = (mask * strength + (1 - strength)).clip(0, 1)

        if len(image.shape) == 3:
            mask = np.expand_dims(mask, axis=-1)

        return (image.astype(np.float32) * mask).astype(np.uint8)


class Vignette(Augmentation):
    def __init__(self, min_strength: float = 0.5):
        self.min_strength = min_strength

    def __call__(self, image) -> np.ndarray:
        strength = random.uniform(self.min_strength, 0.5)
        rows, cols = image.shape[:2]

        sigma_x = cols * (1 - strength)
        sigma_y = rows * (1 - strength)

        kernel_x = cv.getGaussianKernel(cols, sigma_x)
        kernel_y = cv.getGaussianKernel(rows, sigma_y)
        kernel = kernel_y @ kernel_x.T

        mask = kernel / kernel.max()

        vignette = image.astype(np.float32)
        for i in range(3):
            vignette[:, :, i] *= mask

        return np.clip(vignette, 0, 255).astype(np.uint8)


class PerspectiveWarp(Augmentation):
    def __init__(self, max_warp: float = 0.2):
        self.max_warp = max_warp

    def __call__(self, image) -> np.ndarray:
        h, w = image.shape[:2]

        # Define original corner points
        src_pts = np.float32([
            [0, 0],
            [w, 0],
            [w, h],
            [0, h]
        ])

        random_offset = lambda val: np.random.uniform(-val, val)

        warp = random.uniform(0, self.max_warp)
        max_dx = w * warp
        max_dy = h * warp
        dst_pts = np.float32([
            [0 + random_offset(max_dx), 0 + random_offset(max_dy)],
            [w + random_offset(max_dx), 0 + random_offset(max_dy)],
            [w + random_offset(max_dx), h + random_offset(max_dy)],
            [0 + random_offset(max_dx), h + random_offset(max_dy)],
        ])

        # Perspective transform matrix
        M = cv.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv.warpPerspective(image, M, (w, h), borderMode=cv.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        return warped
