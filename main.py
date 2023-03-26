import os

from dotenv import load_dotenv
load_dotenv()

import milvus
import encode
from  matplotlib import pyplot as plt

collection_name = 'faces'

def main():
    if not faces_processed():
        # if a clone collection exists
        milvus.delete_collection(collection_name) 
        encode.preprocess_images()
    if not (os.path.isfile("./id_to_class")):
        milvus.delete_collection(collection_name)
    if milvus.create_collection(collection_name):
        milvus.import_all_embeddings()
    milvus.search_image("images/test.jpg")
    plt.show()

def faces_processed():
    return (os.path.isfile("./encoded_save.npy") 
            and os.path.isfile("./identity_save.npy"))

