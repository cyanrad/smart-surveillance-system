import os
from dotenv import load_dotenv

load_dotenv()

import milvus
import encode
from  matplotlib import pyplot as plt


milvus.delete_collection()

if not (os.path.isfile("./encoded_save.npy") and os.path.isfile("./identity_save.npy")):
    print("Processing Images...")
    milvus.delete_collection()
    encode.preprocess_images()
if not (os.path.isfile("./id_to_class")):
    milvus.delete_collection()
if milvus.create_collection():
    milvus.import_all_embeddings()
milvus.search_image("images/test.jpg")
plt.show()