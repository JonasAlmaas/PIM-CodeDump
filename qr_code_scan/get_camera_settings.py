import os
import cv2
import numpy as np

ret = np.load(os.path.join(os.path.dirname(__file__), "brio_camera_calibration/ret.npy"))
mtx = np.load(os.path.join(os.path.dirname(__file__), "brio_camera_calibration/mtx.npy"))
dist = np.load(os.path.join(os.path.dirname(__file__), "brio_camera_calibration/dist.npy"))
rvecs = np.load(os.path.join(os.path.dirname(__file__), "brio_camera_calibration/rvecs.npy"))
tvecs = np.load(os.path.join(os.path.dirname(__file__), "brio_camera_calibration/tvecs.npy"))

resolution = [4096, 2160]

cv2.namedWindow("Preview")
cv2.namedWindow("Sliders", cv2.WINDOW_AUTOSIZE)
fourcc = cv2.VideoWriter_fourcc("M", "J", "P", "G")
cap = cv2.VideoCapture()
cap.open(1 + cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FOURCC, fourcc)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
cap.set(cv2.CAP_PROP_FPS, 30)

# Camera settings
# Keep at 0.25 to disable auto_exposure. 0.75 is enabled
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)


def empty(value):
    pass

cv2.createTrackbar('Focus', "Sliders", 15, 255, empty)
cv2.createTrackbar('Exposure', "Sliders", -4, 0, empty)
cv2.setTrackbarMin('Exposure', "Sliders", -13)
cv2.createTrackbar('Contrast', "Sliders", 0, 255, empty)
cv2.setTrackbarMin('Contrast', "Sliders", -255)
cv2.createTrackbar('Hue', "Sliders", 0, 180, empty)
cv2.createTrackbar('Saturation', "Sliders", 0, 255, empty)
cv2.createTrackbar('Brightness', "Sliders", 0, 255, empty)
cv2.createTrackbar('RangeLow', "Sliders", 41, 255, empty)
cv2.createTrackbar('RangeHigh', "Sliders", 255, 255, empty)

while True:
    focus = cv2.getTrackbarPos("Focus", "Sliders")
    exposure = cv2.getTrackbarPos("Exposure", "Sliders")
    contrast = cv2.getTrackbarPos("Contrast", "Sliders")
    hue = cv2.getTrackbarPos("Hue", "Sliders")
    saturation = cv2.getTrackbarPos("Saturation", "Sliders")
    brightness = cv2.getTrackbarPos("Brightness", "Sliders")
    
    cap.set(cv2.CAP_PROP_FOCUS, focus)
    cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
    cap.set(cv2.CAP_PROP_CONTRAST, contrast)
    cap.set(cv2.CAP_PROP_HUE, hue)
    cap.set(cv2.CAP_PROP_SATURATION, saturation)
    cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)

    rval, frame = cap.read()

    if rval:
        original_source_image = cv2.cvtColor(frame, 1)
        original_source_image = cv2.cvtColor(original_source_image, cv2.COLOR_BGR2GRAY)

        range_low = cv2.getTrackbarPos("RangeLow", "Sliders")
        range_high = cv2.getTrackbarPos("RangeHigh", "Sliders")

        original_source_image = cv2.inRange(original_source_image, range_low, range_high)
        original_source_image = cv2.cvtColor(original_source_image, cv2.COLOR_RGB2RGBA)
    else:
        original_source_image = np.zeros((1,1), np.uint16)
    
    displayed_image = cv2.resize(original_source_image, (int(resolution[0] / 4), int(resolution[1] / 4)))
    cv2.imshow("Preview", displayed_image)
    key = cv2.waitKey(1)
    if key == 27:
        break
