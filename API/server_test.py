from fastapi import FastAPI
from fastapi.testclient import TestClient
from server import Server
import milvus

# collection_name = 'api_testing'
# milvus.delete_outdated_collection(collection_name)
# collection = milvus.create_collection(collection_name)

app = FastAPI()
s = Server()
app.include_router(s.router)

client = TestClient(app)


def test_add_new_face():
    img_data = open("../images/face.jpg", "rb").read()
    expected_length = len(img_data)
    response = client.post("/face/id1", files={"img": img_data})
    assert response.json() == {"file_size": expected_length}
