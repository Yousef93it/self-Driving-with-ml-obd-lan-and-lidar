import cv2
import numpy as np
import utlis

curveList = []
avgVal = 20

def getLaneCurve(img, display=0):
    """
    Calculates the lane curvature and drive direction from a given image.

    Parameters:
    img (numpy.ndarray): The input image from which lane curvature is to be calculated.
    display (int): Control the display of images:
        - 0: No display
        - 1: Display stacked images

    Returns:
    list: A list containing:
        - curve (float): Normalized curvature value (-1, 0, or 1)
        - drive (float): Drive direction (-1.0 for left, 1.0 for right)

    Process Overview:
    1. Threshold the image to isolate lane markings.
    2. Warp the thresholded image to a top-down view based on predefined points.
    3. Calculate the center point and curve point using histogram analysis.
    4. Update a list of recent curve values for smoothing.
    5. Prepare images for display, including the lane overlay and result.

    Notes:
    - The function uses external utilities (utlis) for image processing tasks.
    - Ensure that the image input is in the correct format for the operations.
    - The drive value is determined based on the proportion of zero elements in the warped image.

    Example usage:
    curve, drive = getLaneCurve(image, display=0)
    """
    imgThres = utlis.threshHolding(img)
    wT, hT, c = img.shape
    points = utlis.valTrackbars()
    imgWarp = utlis.wrapImg(imgThres, points, hT, wT)
    imgWarpPoints = utlis.drawPoints(img.copy(), points)

    # Calculate center and curve points
    centerPoint, imghis = utlis.getHistogram(imgWarp, minPer=0.2, display=True, region=4)
    curvePoint, imghis = utlis.getHistogram(imgWarp, minPer=0.9, display=True, region=1)
    curveRaw = centerPoint - curvePoint
    
    # Update curve list for smoothing
    curveList.append(curveRaw)
    if len(curveList) > avgVal:
        curveList.pop(0)
    curve = int(sum(curveList) / len(curveList))
    
    # Display processing
    if display != 0:
        imgInvWarp = utlis.wrapImg(imgWarp, points, hT, wT, inv=True)
        imgInvWarp = cv2.cvtColor(imgInvWarp, cv2.COLOR_GRAY2BGR)
        imgInvWarp[0:wT // 3, 0:hT] = 0, 0, 0
        imgLaneColor = np.zeros_like(img)
        imgLaneColor[:] = 250, 250, 0
        imgLaneColor = cv2.bitwise_and(imgInvWarp, imgLaneColor)

        imgResult = np.copy(img)
        if imgResult.shape != imgLaneColor.shape:
            imgLaneColor = cv2.resize(imgLaneColor, (imgResult.shape[1], imgResult.shape[0]))
        imgResult = cv2.addWeighted(imgResult, 1, imgLaneColor, 1, 0)
        cv2.putText(imgResult, str(curve), (wT // 2 - 80, 85), cv2.FONT_HERSHEY_COMPLEX, 2, (105, 100, 255), 3)

    if display == 1:
        imgStacked = utlis.stackImages(0.7, ([img, imgWarpPoints, imgWarp],
                                             [imghis, imgLaneColor, imgResult]))
        cv2.imshow('ImageStack', imgStacked)

    # Normalize curve value
    curve = curve / 100
    drive = 1.0 if curve > 0 else -1.0 if curve < 0 else 0.0
    
    # Check for zero elements in the warped image
    zero_percentage = (np.size(imgWarp) - np.count_nonzero(imgWarp)) / np.size(imgWarp)
    if zero_percentage > 0.9:
        drive = -1.0

    return [curve, drive]

if __name__ == "__main__":
    pass
