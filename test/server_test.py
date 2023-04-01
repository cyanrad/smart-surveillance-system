from fastapi import FastAPI
from fastapi.testclient import TestClient
import os

import envImport
from API.server import Server
from milvus import *


collection_name = 'api_testing'
delete_outdated_collection(collection_name)
collection = create_collection(collection_name)

app = FastAPI()
s = Server()
app.include_router(s.router)
client = TestClient(app)

test_img_path = "./test_resources/test_face.jpg"


def test_add_new_face():
    fd = os.open(test_img_path, os.O_RDONLY | os.O_BINARY)
    contents = os.read(fd, os.path.getsize(test_img_path))
    os.close(fd)

    expected_length = len(contents)
    response = client.post("/face/id1", files={"img": contents})
    assert response.json() == {"file_size": expected_length}
