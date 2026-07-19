import cv2
import numpy as np

TARGET_WIDTH = 300
TARGET_HEIGHT = 420
MIN_RESOLUTION_WIDTH = 400
MIN_RESOLUTION_HEIGHT = 600
MIN_LAPLACIAN_VARIANCE = 50.0
MIN_BRIGHTNESS = 40.0
MAX_BRIGHTNESS = 240.0


def validate_image_quality(image: np.ndarray) -> bool:
    """
    Check resolution (min 400x600)
    Check blur (Laplacian variance > threshold)
    Check exposure (mean brightness)
    Return True if acceptable, else False
    """
    if image is None or len(image.shape) < 2:
        return False

    height, width = image.shape[:2]
    # In some cases people might upload landscape cards, so check both dimensions
    if max(width, height) < MIN_RESOLUTION_HEIGHT or min(width, height) < MIN_RESOLUTION_WIDTH:
        return False

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < MIN_LAPLACIAN_VARIANCE:
        return False

    mean_brightness = gray.mean()
    if mean_brightness < MIN_BRIGHTNESS or mean_brightness > MAX_BRIGHTNESS:
        return False

    return True


def order_quadrilateral_points(points: np.ndarray) -> np.ndarray:
    points = points.astype(np.float32)
    sums = points.sum(axis=1)
    diffs = np.diff(points, axis=1).reshape(-1)

    top_left = points[np.argmin(sums)]
    bottom_right = points[np.argmax(sums)]
    top_right = points[np.argmin(diffs)]
    bottom_left = points[np.argmax(diffs)]

    return np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)


def crop_card_region(image: np.ndarray) -> np.ndarray:
    """
    Detect card boundaries using edge detection (Canny)
    Crop to card region using perspective transform.
    Return cropped image, or original image if no card detected.
    """
    if image is None or len(image.shape) < 2:
        return image

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 75, 200)
    kernel = np.ones((3, 3), dtype=np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=2)
    edges = cv2.erode(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image

    image_area = float(image.shape[0] * image.shape[1])
    min_area = image_area * 0.1  # Card should be at least 10% of the image

    candidates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        perimeter = cv2.arcLength(contour, True)
        approximation = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if len(approximation) == 4:
            candidates.append((area, approximation))

    if not candidates:
        return image

    # Sort by area descending and take the largest 4-point contour
    candidates.sort(key=lambda item: item[0], reverse=True)
    best_contour = candidates[0][1]

    points = best_contour.reshape(4, 2)
    rect = order_quadrilateral_points(points)

    # Compute width and height of the new image
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    if maxWidth == 0 or maxHeight == 0:
        return image

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


def normalize_dimensions(image: np.ndarray) -> np.ndarray:
    """
    Resize to 300x420 (standard Pokémon card aspect ratio ~2.27:3)
    Preserve aspect ratio, pad if needed.
    """
    if image is None:
        return image
        
    h, w = image.shape[:2]
    
    # Target aspect ratio: width/height = 300/420 = 5/7
    target_aspect = TARGET_WIDTH / TARGET_HEIGHT
    aspect = w / float(h)
    
    if aspect > target_aspect:
        # Image is wider than target. Scale width to TARGET_WIDTH, pad height.
        new_w = TARGET_WIDTH
        new_h = int(TARGET_WIDTH / aspect)
    else:
        # Image is taller than target. Scale height to TARGET_HEIGHT, pad width.
        new_h = TARGET_HEIGHT
        new_w = int(TARGET_HEIGHT * aspect)
        
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Compute padding
    delta_w = TARGET_WIDTH - new_w
    delta_h = TARGET_HEIGHT - new_h
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)
    
    color = [0, 0, 0] if len(image.shape) == 3 else 0
    padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    
    return padded
