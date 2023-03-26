from pymilvus import (
    connections, 
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
import pickle
import numpy as np
from  matplotlib import pyplot as plt
import matplotlib.image as mpimg
import os
import encode

VECTOR_DIAMENSION = 512

# Initialized in import_all_embeddings() loaded in create_collection()
IMG_INDEX_TO_CLASS = []

# loaded in create_collection()
COLLECTION = None
COLLECTION_NAME = 'faces'

connections.connect("default", host=os.getenv('HOST'), port=os.getenv('PORT'))

# TODO: there should be a function for initializationa and one to create a connection
def create_collection():
    """
    Creates a collection & indexes it using an L2 metric and an IVF_FLAT index type.
    @ collection exists, load a pickled dictionary called 'img_index_to_class' into IMG_INDEX_TO_CLASS

    Returns:
        0 @ default
        1 @ collection created or img_index_to_class file doesn't exist
    """
    global IMG_INDEX_TO_CLASS
    global COLLECTION
    global COLLECTION_NAME

    if not utility.has_collection(COLLECTION_NAME):
        print("Creating a collection on Milvus Database...📊️")
        fields = [
            FieldSchema(name='id', dtype=DataType.INT64, descrition='ids', is_primary=True, auto_id=False),
            FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, descrition='embedding vectors', dim=VECTOR_DIAMENSION)
        ]
        schema = CollectionSchema(fields=fields)
        COLLECTION = Collection(name=COLLECTION_NAME, schema=schema)
        print("Collection created✅️")
        return 1  

    else:
        #NOTE should be it's own function
        print("Collection exsits")
        COLLECTION = Collection(COLLECTION_NAME)
        try:
            with open('img_index_to_class', 'rb') as fp:
                IMG_INDEX_TO_CLASS = pickle.load(fp)
            return 0
        except:
            return 1


def import_all_embeddings():
    global IMG_INDEX_TO_CLASS
    global COLLECTION

    # loading embedding and identity data
    print("Loading in encoded vectors...")
    encoded = np.load("encoded_save.npy")
    identity = np.load("identity_save.npy")

    #NOTE: unclear: loading embeddings into python lists
    embeddings = []
    indexing = []
    counter = 1
    for embed in encoded:
        embeddings.append(embed)
        indexing.append(counter)
        counter += 1

    # inserting data into collection
    print("Inserting data into a collection")
    insertInfo = COLLECTION.insert([indexing, embeddings])
    print(insertInfo)

    # indexing embeddings
    index_params = {
        'metric_type':'L2',     # the distance metric (Euclidean distance)
        'index_type':"FLAT",    # Chose flat since we're dealing with a small dataset
        'params':{},
    }
    COLLECTION.create_index(field_name="embedding", index_params=index_params)

    # loading data into memory for querying
    COLLECTION.load()

    # Loading IMG_INDEX_TO_IDENTITY data, and saving it as pickle
    for i in range(len(indexing)):
        IMG_INDEX_TO_CLASS.append((indexing[i], identity[i]))

    with open('img_index_to_class', 'wb') as fp:
        pickle.dump(IMG_INDEX_TO_CLASS, fp)
    print("Image index to class data saved")


# Search for the nearest neighbor of the given image. 
def search_image(file_loc):
    global COLLECTION
    global IMG_INDEX_TO_CLASS

    query_vectors  = encode.encode_faces(file_loc)
    insert_image = encode.draw_box_on_face(file_loc)
    
    print("Searching for the image ...🧐️")
    
    query_vector = query_vectors[0]
    search_params = {
        "params": {}, # since we're using FLAT index
    }
    results = COLLECTION.search(query_vector, "embedding", search_params, limit=3)
    print(results)

    if results is not None:
        temp = []

        plt.imshow(insert_image)

        for x in range(len(results)):
            for img_index, img_class in IMG_INDEX_TO_CLASS:
                result_img_index = results[x][0].id
                if result_img_index == img_index:
                    temp.append(img_class)
        print(temp)

        # Displaing similar faces
        for i, x in enumerate(temp):
            fig = plt.figure()
            fig.suptitle('Face-' + str(i) + ", Celeb Folder: " + str(x))
            currentFolder = os.getenv('DATA_FOLDER') + str(x)
            total = min(len(os.listdir(currentFolder)), 6)

            for i, file in enumerate(os.listdir(currentFolder)[0:total], 1):
                fullpath = currentFolder+ "/" + file
                img = mpimg.imread(fullpath)
                plt.subplot(2, 3, i)
                plt.imshow(img)
        plt.show(block = False)
        if(len(temp))!=0:
            print("Wohoo, Similar Images found!🥳️")


# Delete the collection
def delete_collection():
    print("deleteing collection")
    utility.drop_collection(COLLECTION_NAME)