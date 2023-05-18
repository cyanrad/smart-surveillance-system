import cv2 as cv
import os
import asyncio
import websockets

from dotenv import load_dotenv


async def sendVideo():
    videoFiles = os.listdir('./videos')
    for file in videoFiles:
        video = cv.VideoCapture('./videos/' + file)

        async with websockets.connect("ws://localhost:8000/stream/0") as ws:
            while True:
                ok, frame = video.read()
                if not ok:
                    break

                _, frame_bytes = cv.imencode(".jpg", frame)

                await ws.send(frame_bytes.tobytes())
                replyData = await ws.recv()
                print("data: ", replyData)

            video.release()
            ws.close()


load_dotenv()
if __name__ == "__main__":
    asyncio.run(sendVideo())
