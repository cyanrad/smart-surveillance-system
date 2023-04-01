import envImport  # has to be first
import milvus
import camera

from PIL import Image
import os


def main():
    collection_name = 'faces'

    milvus.delete_outdated_collection(collection_name)

    collection = None
    if milvus.collection_exists(collection_name):
        collection = milvus.get_collection(collection_name)
    else:
        collection = milvus.create_collection(collection_name)
        milvus.upload_embeddings_from_dataset(
            collection, os.getenv('DATA_FOLDER'))

    camera.streamDetection(collection)

    # img = Image.open("./images/face.jpg")
    # milvus.upload_embedding_from_img(collection, img, ["4"])
    # time.sleep(1)
    # result = milvus.quick_search(collection, img)
    # print(result)


main()
