import os
import sys

from pyzbar import pyzbar
import cv2

import numpy as np
import time

sys.path.insert(1, os.path.abspath('.'))
from urpy.urpy import urpy


class SweepPose():
    start = urpy.Pose(x=650, y=-775, z=500, rx=-1.48, ry=1.0, rz=-1.51)
    end = urpy.Pose(x=650, y=375, z=500, rx=-1.48, ry=1.0, rz=-1.51)

ret = np.load(os.path.join(os.path.dirname(__file__), "brio_camera_calibration/ret.npy"))
mtx = np.load(os.path.join(os.path.dirname(__file__), "brio_camera_calibration/mtx.npy"))
dist = np.load(os.path.join(os.path.dirname(__file__), "brio_camera_calibration/dist.npy"))
rvecs = np.load(os.path.join(os.path.dirname(__file__), "brio_camera_calibration/rvecs.npy"))
tvecs = np.load(os.path.join(os.path.dirname(__file__), "brio_camera_calibration/tvecs.npy"))

resolution = [4096, 2160]

cv2.namedWindow("Preview")
fourcc = cv2.VideoWriter_fourcc("M", "J", "P", "G")
cap = cv2.VideoCapture()
cap.open(1 + cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FOURCC, fourcc)
# Focus
cap.set(28, 0)
# Keep at 0.25 to disable auto_exposure. 0.75 is enabled
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
cap.set(cv2.CAP_PROP_EXPOSURE, -3)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
cap.set(cv2.CAP_PROP_FPS, 30)

qr_codes = []

TUNING_CAMERA = False

def do_the_camera_stuff():
    rval, frame = cap.read()

    if rval:
        original_source_image = cv2.cvtColor(frame, 1)
        
        original_source_image = cv2.cvtColor(original_source_image, cv2.COLOR_BGR2GRAY)
        original_source_image = cv2.inRange(original_source_image, 90, 210)
        original_source_image = cv2.cvtColor(original_source_image, cv2.COLOR_RGB2RGBA)
    else:
        original_source_image = np.zeros((1,1), np.uint16)

    # ######################## IMAGE CALIBRATION ######################

    # calibration
    h, w = original_source_image.shape[:2]

    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # undistort
    original_source_image = cv2.undistort(original_source_image, mtx, dist, None, newcameramtx)
    # crop the image
    x, y, w, h = roi
    original_source_image = original_source_image[y : y + h, x : x + w]

    barcodes = pyzbar.decode(original_source_image)

    for barcode in barcodes:
        (x, y, w, h) = barcode.rect
        cv2.rectangle(original_source_image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(original_source_image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        qr_codes.append(barcodeData)

    displayed_image = cv2.resize(original_source_image, (int(resolution[0] / 3.5), int(resolution[1] / 3.5)))
    # displayed_image = cv2.resize(original_source_image, (640, 480))
    cv2.imshow("Preview", displayed_image)
    cv2.waitKey(1)


if not TUNING_CAMERA:
    robot = urpy.UniversalRobot("192.168.1.101")

    percent = 0
    step_size = 0.05

    robot.move_to(SweepPose.start)

    while percent <= 1:
        robot.move_to(SweepPose.start.lerp(SweepPose.end, percent))
        percent += step_size

        time.sleep(2)

        do_the_camera_stuff()

    cap.release()
    cv2.destroyWindow("Preview")

    # Removes any duplicates.
    qr_codes = list(set(qr_codes))
    print("QR code list:", qr_codes)
    print("QR code list:", len(qr_codes))
else:
    while True:
        do_the_camera_stuff()

        qr_codes = list(set(qr_codes))
        print("QR code list:", qr_codes)
        print("QR code list:", len(qr_codes))
        qr_codes = []
