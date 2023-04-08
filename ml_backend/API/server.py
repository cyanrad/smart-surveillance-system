from fastapi import APIRouter, File, WebSocket
from pymilvus import Collection
from PIL import Image
import io

import milvus


class Server:
    def __init__(self, collection: Collection):
        self.collection = collection
        self.router = APIRouter()

        self.router.add_api_route(
            "/face/{img_class}", self.add_new_face, methods=["POST"])
        self.router.add_websocket_route(
            "/stream/{device_name}", self.stream_face_recognition
        )

    def add_new_face(self, img_class: str, img_bytes: bytes = File()):
        buffered_data = io.BytesIO(img_bytes)
        img = Image.open(buffered_data)

        ok = milvus.upload_embedding_from_img(
            self.collection, img, [img_class])
        return {"ok": ok}

    async def stream_face_recognition(self, websocket: WebSocket):
        await websocket.accept()
        while True:
            img_bytes = await websocket.receive_bytes()

            buffered_data = io.BytesIO(img_bytes)
            img = Image.open(buffered_data)
            result = milvus.quick_search(self.collection, img)

            await websocket.send_json({"detected": result})
