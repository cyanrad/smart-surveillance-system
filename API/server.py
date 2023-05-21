from fastapi import APIRouter, File, HTTPException, WebSocket, WebSocketDisconnect
from pymilvus import Collection
from PIL import Image
import io

import milvus


class Server:
    def __init__(self, collection_name: str):
        self.collection: Collection

        # creating collection
        if milvus.collection_exists(collection_name):
            self.collection = milvus.get_collection(collection_name)
        else:
            self.collection = milvus.create_collection(collection_name)

        # starting the API
        self.router = APIRouter()

        self.router.add_api_route(
            "/face/{owner_uuid}/{img_class}", self.add_face, methods=["POST"])
        self.router.add_websocket_route(
            "/stream/{device_name}", self.stream_face_recognition
        )
        self.router.add_websocket_route(
            "/blockstream/{device_name}", self.block_stream_face_recognition
        )

    def add_face(self, img_class: str, owner_uuid: str, img_bytes: bytes = File()):
        buffered_data = io.BytesIO(img_bytes)
        img = Image.open(buffered_data)

        ok = milvus.upload_embedding_from_img(
            self.collection, img, [img_class])

        if ok:
            return {
                "class": img_class,
                "owner": owner_uuid,
            }
        else:
            raise HTTPException(
                status_code=400, detail="error uploading image")

    async def stream_face_recognition(self, websocket: WebSocket):
        await websocket.accept()

        try:
            while True:
                img = await self.get_frame(websocket)
                result = milvus.quick_search(self.collection, img)

                if len(result) == 0:
                    await websocket.send_json({"detected": [], "positions": []})
                else:
                    await websocket.send_json({"detected": result[0], "positions": result[1].flatten().tolist()})
        except WebSocketDisconnect:
            print("disconnected")

    # don't use, changes not applied yet
    async def block_stream_face_recognition(self, websocket: WebSocket):
        await websocket.accept()

        # getting initial frame data
        initial_frame = await self.get_frame(websocket)
        stream_resolution = initial_frame.size

        # block image has 5 columns & 2 rows to hold stream frames
        block_image = Image.new(
            'RGB', (5*stream_resolution[0], 2*stream_resolution[1]))

        log = 0
        while True:
            # filling the block image
            for i in range(2):
                for j in range(5):
                    img = await self.get_frame(websocket)
                    block_image.paste(
                        img, (j*stream_resolution[0], i*stream_resolution[1]))

                    log += 1
                    print(log)

            results = milvus.quick_search(self.collection, block_image)
            await websocket.send_json({"detected": results})

            # clearing the block image
            block_image = Image.new(
                'RGB', (5*stream_resolution[0], 2*stream_resolution[1]))

    async def get_frame(self, websocket: WebSocket):
        img_bytes = await websocket.receive_bytes()
        buffered_data = io.BytesIO(img_bytes)
        return Image.open(buffered_data, formats=['JPEG'])
