import cv2 as cv
import os
import asyncio
import websockets
import requests
from dotenv import load_dotenv


def addFace(filepath: str, faceClass: str, ownerUuid: str):
    r = requests.post(
        os.getenv("URI") + "/face/" + ownerUuid + "/" + faceClass,
        files={"img_bytes": open(filepath, "rb")}
    )


async def sendVideo():
    videoFiles = os.listdir('./videos')

    for file in videoFiles:
        video = cv.VideoCapture('./videos/' + file)

        async with websockets.connect(os.getenv('WS_URI') + "/stream/0") as ws:
            while True:
                ok, frame = video.read()
                if not ok:
                    break

                _, frame_bytes = cv.imencode(".jpg", frame)

                await ws.send(frame_bytes.tobytes())
                replyData = await ws.recv()
                print("data: ", replyData)

            video.release()
            await ws.close()


load_dotenv()

if __name__ == "__main__":
    # for face in os.listdir("./faces"):
    #     for img in os.listdir("./faces/" + face):
    #         addFace("./faces/" + face + "/" + img, face, "0")
    asyncio.run(sendVideo())
