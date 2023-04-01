from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image
import os
import io
import pytest

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
client = TestClient(app)
delete_outdated_collection(collection_name)

# testing resource paths
test_face_path = "./test_resources/test_face.jpg"
test_multi_face_path = "./test_resources/test_multi_face.jpg"
test_noise_path = "./test_resources/test_noise.jpg"


def add_testing_face(img_path):
    # reading a file (using os as to be standard across lanuages)
    fd = os.open(img_path, os.O_RDONLY | os.O_BINARY)
    contents = os.read(fd, os.path.getsize(img_path))
    os.close(fd)

    # sends the testing face under the id1 class
    # the server will take it, detect the face, encode it, then add it to the collection
    return client.post("/face/id1", files={"img_bytes": contents})


def test_add_new_face():
    delete_outdated_collection(collection_name)
    collection = create_collection(collection_name)
    s.collection = collection

    # testing a single face
    resp1 = add_testing_face(test_face_path)
    assert resp1.json() == {"ok": True}

    # testing a multiple faces
    resp2 = add_testing_face(test_multi_face_path)
    assert resp2.json() == {"ok": False}

    # testing a noise picture
    resp3 = add_testing_face(test_noise_path)
    assert resp3.json() == {"ok": False}

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
