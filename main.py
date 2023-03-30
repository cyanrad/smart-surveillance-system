import envImport  # has to be first
import milvus
import encode
import camera
import const
import img_index_to_class
from PIL import Image
import os

# creating saved processed data folder
if not os.path.exists(const.SAVED_PROCESSING_FOLDER):
    os.makedirs(const.SAVED_PROCESSING_FOLDER)
# TODO: create asserts for files and folders


def main():
    collection_name = 'faces'

    if not processed_faces_saved():
        milvus.delete_outdated_collection(collection_name)
        encode.preprocess_faces()

    if not img_index_to_class.saved():
        milvus.delete_outdated_collection(collection_name)

    collection = None
    if milvus.collection_exists(collection_name):
        collection = milvus.get_collection(collection_name)
    else:
        collection = milvus.create_collection(collection_name)
        milvus.load_embeddings_into_memory(collection)

    camera.streamDetection(collection)


def processed_faces_saved():
    return (os.path.isfile(const.ENCODED_SAVE_FILE)
            and os.path.isfile(const.CLASS_SAVE_FILE))


main()
