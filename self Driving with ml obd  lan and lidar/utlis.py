import cv2
import numpy as np

def thresholding(img):
    """
    Applies grayscale, Gaussian blur, and thresholding to an image 
    to isolate regions of interest.
    
    Parameters:
    - img (numpy.ndarray): Input image.

    Returns:
    - numpy.ndarray: Thresholded binary mask of either black or white regions based on pixel count.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold for detecting black and white regions
    _, mask_black = cv2.threshold(gray_blurred, 90, 255, cv2.THRESH_BINARY_INV)
    _, mask_white = cv2.threshold(gray_blurred, 180, 220, cv2.THRESH_BINARY)

    # Return mask with more detected pixels
    return mask_black if cv2.countNonZero(mask_black) > cv2.countNonZero(mask_white) else mask_white


def warp_image(img, points, width, height, inverse=False):
    """
    Warps the image to a top-down view or its original perspective based on the points.

    Parameters:
    - img (numpy.ndarray): Input image.
    - points (list): Points for perspective transformation.
    - width (int): Width of the output image.
    - height (int): Height of the output image.
    - inverse (bool): Whether to apply the inverse warp.

    Returns:
    - numpy.ndarray: Warped image.
    """
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    matrix = cv2.getPerspectiveTransform(pts2, pts1) if inverse else cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(img, matrix, (width, height))


def val_trackbar(wT=480, hT=240, x=[50, 180, 0, 236]):
    """
    Sets default points for perspective transformation based on provided dimensions.

    Returns:
    - numpy.ndarray: Array of points.
    """
    points = np.float32([
        (x[0], x[1]), (wT - x[0], x[1] - 3),
        (x[2] + 12, x[3]), (wT - x[2], x[3])
    ])
    return points


def draw_points(img, points):
    """
    Draws circles and lines on an image to visualize points.

    Parameters:
    - img (numpy.ndarray): Input image.
    - points (list): Points to draw.
    """
    for x in range(4):
        cv2.circle(img, (int(points[x][0]), int(points[x][1])), 5, (100, 100, 255), cv2.FILLED)
    cv2.polylines(img, [np.int32(points)], isClosed=True, color=(100, 100, 255), thickness=2)
    return img


def get_histogram(img, min_percentage=0.1, display=False, region=1):
    """
    Calculates a histogram based on pixel intensities across a specific region.

    Parameters:
    - img (numpy.ndarray): Input binary image.
    - min_percentage (float): Minimum threshold percentage of max value to detect a region.
    - display (bool): If True, displays the histogram.
    - region (int): Region of interest (1 = full, higher numbers reduce ROI).

    Returns:
    - tuple: Base point of detected region and (optional) histogram image.
    """
    roi = img[-img.shape[0] // region:, :]
    hist_values = np.sum(roi, axis=0)
    max_val = np.max(hist_values)
    min_val = min_percentage * max_val

    index_array = np.where(hist_values >= min_val)
    base_point = int(np.average(index_array)) if len(index_array[0]) > 0 else 0

    if display:
        img_hist = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
        for x, intensity in enumerate(hist_values):
            cv2.line(img_hist, (x, img.shape[0]), (x, int(img.shape[0] - intensity // 255 // region)), (0, 255, 0), 1)
        cv2.circle(img_hist, (base_point, img.shape[0]), 20, (255, 0, 0), cv2.FILLED)
        return base_point, img_hist

    return base_point


def stack_images(scale, img_array):
    """
    Stacks multiple images in a grid for display.

    Parameters:
    - scale (float): Scaling factor for the images.
    - img_array (list): Array of images to be stacked.

    Returns:
    - numpy.ndarray: Stacked image.
    """
    rows = len(img_array)
    cols = len(img_array[0]) if isinstance(img_array[0], list) else 1
    width = img_array[0][0].shape[1]
    height = img_array[0][0].shape[0]

    if isinstance(img_array[0], list):
        img_array = [
            [
                cv2.resize(img, (width, height), None, scale, scale) if img.shape[:2] != (height, width) else img
                for img in row
            ]
            for row in img_array
        ]
        image_blank = np.zeros((height, width, 3), np.uint8)
        hor = [np.hstack(row) for row in img_array]
        ver = np.vstack(hor)
    else:
        img_array = [cv2.resize(img, (width, height), None, scale, scale) for img in img_array]
        ver = np.hstack(img_array)
    
    return ver


if __name__ == "__main__":
    pass
