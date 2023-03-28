import cv2 as cv
import milvus
from PIL import Image


def streamDetection(collection):
    cam = initializeCamera()
    while True:
        frame = getFrame(cam)
        PIL_frame = Image.fromarray(frame)

        result = milvus.quick_search(collection, PIL_frame)
        print(result)

        if cv.waitKey(10) == 27:
            break

        cv.imshow('Capture - Face detection', frame)


def initializeCamera(camera_device=0):
    cam = cv.VideoCapture(camera_device)
    if not cam.isOpened:
        print('--(!)Error opening video capture')
        exit(0)

    return cam


def getFrame(cam):
    _, frame = cam.read()
    if frame is None:
        print('--(!) No captured frame -- Break!')
        exit(0)

    return frame
