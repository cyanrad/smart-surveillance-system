from fastapi import APIRouter, File
from pymilvus import Collection


class Server:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route(
            "/face/{img_class}", self.add_new_face, methods=["POST"])

    def add_new_face(self, img_class: str, img: bytes = File()):
        return {"file_size": len(img)}
        # milvus.upload_embedding_from_img(self.collection, img, [img_class])
