from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image
import os
import io
import pytest
import cv2

import envImport
from API.server import Server
from milvus import *


# database should be initialized for each test so data doesn't collide
# created here so we can initialize the server, but is deleted after
collection_name = 'api_testing'
delete_outdated_collection(collection_name)
collection = create_collection(collection_name)

# server & test client creation
app = FastAPI()
s = Server(collection)
app.include_router(s.router)
delete_outdated_collection(collection_name)

# testing resource paths
test_face_path = "./test_resources/test_face.jpg"
test_multi_face_path = "./test_resources/test_multi_face.jpg"
test_noise_path = "./test_resources/test_noise.jpg"
test_video_path = "./test_resources/test_video.mp4"


@pytest.mark.skip(reason="temporarely taken out")
def test_add_new_face():
    delete_outdated_collection(collection_name)
    collection = create_collection(collection_name)
    s.collection = collection

    client = TestClient(app)

    # testing a single face
    resp1 = upload_testing_img(client, test_face_path)
    assert resp1.json() == {"ok": True}

    # testing a multiple faces
    resp2 = upload_testing_img(client, test_multi_face_path)
    assert resp2.json() == {"ok": False}

    # testing a noise picture
    resp3 = upload_testing_img(client, test_noise_path)
    assert resp3.json() == {"ok": False}

    delete_outdated_collection(collection_name)


def upload_testing_img(client, img_path):
    # reading a file (using os as to be standard across lanuages)
    fd = os.open(img_path, os.O_RDONLY | os.O_BINARY)
    contents = os.read(fd, os.path.getsize(img_path))
    os.close(fd)

    # sends the testing face under the id1 class
    # the server will take it, detect the face, encode it, then add it to the collection
    return client.post("/face/id1", files={"img_bytes": contents})


def test_stream_face_recognition():
    delete_outdated_collection(collection_name)
    collection = create_collection(collection_name)
    s.collection = collection

    client = TestClient(app)

    try:
        with client.websocket_connect("/stream/123") as ws:
            cap = cv2.VideoCapture(test_video_path)
            if not cap.isOpened:
                return

            while (cap.isOpened()):
                _, frame = cap.read()
                if frame is None:
                    return

                ok, img_byte_buf = cv2.imencode(".jpg", frame)
                if ok:
                    ws.send_bytes(img_byte_buf.tobytes())
                    resp = ws.receive_json()
                    print(resp)
    except:
        print("done")

    delete_outdated_collection(collection_name)


@pytest.mark.skip(reason="no longer useful, was used to demonstate that conversion works")
def test_bytes_to_image():
    test_img_path = "./test_resources/test_face.jpg"
    fd = os.open(test_img_path, os.O_RDONLY | os.O_BINARY)
    contents = os.read(fd, os.path.getsize(test_img_path))
    os.close(fd)

    buffered_data = io.BytesIO(contents)
    image = Image.open(buffered_data)

    image.show()
