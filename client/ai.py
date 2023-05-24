import time
import json
import os
import requests
import websockets
import cv2 as cv
import authentication
import math

# loading env uri for posting faces
HTTP_URI: str
temp = os.getenv("HTTP_URI")
if temp is not None:
    HTTP_URI = temp
else:
    exit(1)

# locaing env uri for websocket streaming
WS_URI: str
temp = os.getenv("WS_URI")
if temp is not None:
    WS_URI = temp
else:
    exit(1)


# modes
# 0: video file         (file path to video)
# 1: streaming link     (ip link to stream)
# 2: system camera      (integer)
async def sendVideo(camera: dict, path) -> None:
    video = cv.VideoCapture(path)

    # we want to send 15 frames per second
    fps = video.get(cv.CAP_PROP_FPS)
    ignore_ratio, i = 0, 0
    max_fps = 10
    if fps > max_fps:
        ignore_ratio = math.floor(fps/max_fps)

    # fps metrics
    frame_counter = 0

    async with websockets.connect(WS_URI + "/stream/" + str(camera["ID"])) as ws:
        # initial fps counter timer
        tic = time.time()

        # reading video frame by frame
        while True:
            ok, frame = video.read()
            if not ok:
                break
            frame = cv.resize(frame, (480, 270))

            # regulating sent frames count to 15 per second for effeciency
            if not (i == ignore_ratio):
                # if display_frame(camera, frame): break
                i += 1
                continue
            else:
                i = 0

            frame_counter += 1
            if frame_counter == max_fps:
                toc = time.time()
                # print("framerate: ", max_fps/(toc-tic))

                tic = time.time()
                frame_counter = 0

            # converting bytes to jpg
            _, frame_bytes = cv.imencode(".jpg", frame)

            # sending message and recieving detected faces
            await ws.send(frame_bytes.tobytes())
            respData = await ws.recv()

            # @ empty response
            if len(respData) <= 0:
                continue

            # getting found faces
            respMap = json.loads(respData)

            if len(respMap["detected"]) == 0:
                if display_frame(camera, frame):
                    break

            pos = respMap["positions"]
            for i, detected in enumerate(respMap["detected"]):
                # getting position of detected face i
                x1 = pos[i][0]
                y1 = pos[i][1]
                x2 = pos[i][2]
                y2 = pos[i][3]

                # if there is a face detected but unkown
                if detected == "":
                    # print(str(camera["ID"]) + "-unknown person detected")
                    draw_box_with_text(frame, x1, y1, x2, y2,
                                       "Unknown", (0, 255, 255))
                    continue

                person_id_pair = detected.split("_")

                # getting if the person is authorized on the camera
                access = authentication.getAccess(
                    camera["ID"], person_id_pair[1])

                # handling auth conditions
                if camera["Is_Black_List"] ^ (access is None):
                    # print(str(camera["ID"]) + "-unauthorized detected: ", detected)
                    draw_box_with_text(frame, x1, y1, x2, y2,
                                       str(camera["ID"]) + "-unauthorized: " + detected, (0, 0, 255))
                else:
                    # print(str(camera["ID"]) + "-detected: ", detected)
                    draw_box_with_text(frame, x1, y1, x2, y2,
                                       str(camera["ID"]) + "-authorized: " + detected, (0, 255, 0))

            # calculaing fps and resetting timer

            display_frame(camera, frame)

        video.release()
        await ws.close()


# this function adds a face of a person to the database
def addFace(filepath: str, faceClass: str, ownerUuid: str):
    return requests.post(
        HTTP_URI + "/face/" + ownerUuid + "/" + faceClass,
        files={"img_bytes": open(filepath, "rb")}
    )


# displaying the image on a window
def display_frame(camera, frame) -> bool:
    # displaying the image on a window
    cv.imshow('stream_' + str(camera["ID"]), frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        return True
    return False


def draw_box_with_text(frame, x1, y1, x2, y2, text, color):
    cv.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
    cv.putText(frame, text, (int(x1), int(y1)-10),
               cv.FONT_HERSHEY_SIMPLEX, 0.5,  color, 1)
