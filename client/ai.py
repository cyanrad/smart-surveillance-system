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


async def sendVideo(camera: dict, video_name: str) -> None:
    # reading video file
    video = cv.VideoCapture('./videos/' + video_name)

    # we want to send 15 frames per second
    fps = video.get(cv.CAP_PROP_FPS)
    ignore_ratio, i = 0, 0
    if fps > 15:
        ignore_ratio = math.floor(fps/15)
    print(ignore_ratio)

    async with websockets.connect(WS_URI + "/stream/" + str(camera["ID"])) as ws:
        # reading video frame by frame
        while True:
            ok, frame = video.read()
            if not ok:
                break
            frame = cv.resize(frame, (480, 270))

            # displaying the image on a window
            cv.imshow('stream_' + str(camera["ID"]), frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

            # regulating sent frames count to 15 per second for effeciency
            if not (i == ignore_ratio):
                print("skipped")
                i += 1
                continue
            else:
                i = 0
            print("processed")

            # Wait for the 'q' key to be pressed to exit

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

            # if len(respMap["detected"]) == 0:
            # print(str(camera["ID"]) + "-no people detected")

            for detected in respMap["detected"]:
                # if there is a face detected but unkown
                if detected == "":
                    # print(str(camera["ID"]) + "-unknown person detected")
                    continue

                person_id_pair = detected.split("_")

                # getting if the person is authorized on the camera
                access = authentication.getAccess(
                    camera["ID"], person_id_pair[1])

                # handling auth conditions
                # if camera["Is_Black_List"] ^ (access is None):
                # print(str(camera["ID"]) +
                #       "-unauthorized detected: ", detected)
                # else:
                # print(str(camera["ID"]) + "-detected: ", detected)

        video.release()
        await ws.close()


# this function adds a face of a person to the database
def addFace(filepath: str, faceClass: str, ownerUuid: str):
    return requests.post(
        HTTP_URI + "/face/" + ownerUuid + "/" + faceClass,
        files={"img_bytes": open(filepath, "rb")}
    )
