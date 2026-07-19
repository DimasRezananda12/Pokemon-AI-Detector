import pytest
import numpy as np
import cv2
from app.services.preprocessing import (
    validate_image_quality,
    crop_card_region,
    normalize_dimensions,
    TARGET_WIDTH,
    TARGET_HEIGHT
)

def create_dummy_image(width, height, color=128):
    return np.full((height, width, 3), color, dtype=np.uint8)

def test_validate_image_quality_resolution():
    # Too small
    small_img = create_dummy_image(300, 300)
    assert not validate_image_quality(small_img)
    
    # Valid size
    valid_img = create_dummy_image(500, 700)
    # To pass laplacian variance, we need some edges. Let's add noise or a sharp square.
    cv2.rectangle(valid_img, (50, 50), (450, 650), (255, 255, 255), -1)
    cv2.rectangle(valid_img, (100, 100), (400, 600), (0, 0, 0), -1)
    
    assert validate_image_quality(valid_img)
    
def test_validate_image_quality_exposure():
    # Too dark
    dark_img = create_dummy_image(500, 700, color=10)
    cv2.rectangle(dark_img, (50, 50), (450, 650), (20, 20, 20), -1)
    assert not validate_image_quality(dark_img)
    
    # Too bright
    bright_img = create_dummy_image(500, 700, color=250)
    cv2.rectangle(bright_img, (50, 50), (450, 650), (255, 255, 255), -1)
    assert not validate_image_quality(bright_img)

def test_crop_card_region():
    # Create a dummy image with a white "card" in the middle of a black background
    bg = np.zeros((800, 600, 3), dtype=np.uint8)
    
    # Draw a rotated white rectangle (card)
    center = (300, 400)
    size = (400, 600)
    angle = 10
    rect = (center, size, angle)
    box = cv2.boxPoints(rect)
    box = np.int32(box)
    cv2.drawContours(bg, [box], 0, (255, 255, 255), -1)
    
    cropped = crop_card_region(bg)
    
    # The cropped region should approximate the size of the card
    h, w = cropped.shape[:2]
    assert h >= 580 and h <= 620
    assert w >= 380 and w <= 420

def test_normalize_dimensions():
    # Test a wider image
    wide = create_dummy_image(800, 600)
    norm_wide = normalize_dimensions(wide)
    assert norm_wide.shape[:2] == (TARGET_HEIGHT, TARGET_WIDTH)
    
    # Test a taller image
    tall = create_dummy_image(400, 800)
    norm_tall = normalize_dimensions(tall)
    assert norm_tall.shape[:2] == (TARGET_HEIGHT, TARGET_WIDTH)
