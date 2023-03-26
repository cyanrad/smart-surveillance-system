import os
from  matplotlib import pyplot as plt
from dotenv import load_dotenv
load_dotenv() # must be done before custom imports

import milvus
import encode
import img_index_to_class
#NOTE: all files indicated by the const import are generated if not exist
import const



def main():
    collection_name = 'faces'

    if not processed_faces_saved():
        milvus.delete_old_collection(collection_name) 
        encode.preprocess_faces()

    if not img_index_to_class.saved():
        milvus.delete_old_collection(collection_name)

    collection = None
    if milvus.collection_exists(collection_name):
        collection = milvus.get_collection(collection_name)
    else:
        collection = milvus.create_collection(collection_name)
    
    milvus.upload_embeddings(collection)

    milvus.search_image(collection, "images/test.jpg")
    plt.show()

def processed_faces_saved():
    return (os.path.isfile(const.ENCODED_SAVE_FILE) 
            and os.path.isfile(const.IDENTITY_SAVE_FILE))

main()