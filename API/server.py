from fastapi import APIRouter, File
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

    def add_new_face(self, img_class: str, img_bytes: bytes = File()):
        buffered_data = io.BytesIO(img_bytes)
        image = Image.open(buffered_data)

        ok = milvus.upload_embedding_from_img(
            self.collection, image, [img_class])
        return {"ok": ok}
