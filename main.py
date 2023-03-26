import os

from dotenv import load_dotenv
load_dotenv() # must be done first

import milvus
import encode
import const
from  matplotlib import pyplot as plt

def main():
    if not processed_faces_saved():
        milvus.delete_old_collection(const.COLLECTION_NAME) 
        encode.preprocess_faces()

    if not images_indexed():
        milvus.delete_old_collection(const.COLLECTION_NAME)

    if milvus.create_collection(const.COLLECTION_NAME):
        milvus.import_all_embeddings()

    milvus.search_image("images/test.jpg")
    plt.show()

def processed_faces_saved():
    return (os.path.isfile(const.ENCODED_SAVE_FILE) 
            and os.path.isfile(const.IDENTITY_SAVE_FILE))

def images_indexed():
    os.path.isfile(const.IMG_INDEX_TO_CLASS_FILE)

main()