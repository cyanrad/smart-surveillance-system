from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import os

import encode
import const
import img_index_to_class


connections.connect("default", host=os.getenv('HOST'), port=os.getenv('PORT'))


def create_collection(name):
    VECTOR_DIAMENSION = 512
    print("Creating a collection on Milvus Database...📊️")
    fields = [
        FieldSchema(name='id', dtype=DataType.INT64,
                    descrition='ids', is_primary=True, auto_id=False),
        FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR,
                    descrition='embedding vectors', dim=VECTOR_DIAMENSION)
    ]
    schema = CollectionSchema(fields=fields)
    return Collection(name=name, schema=schema)


def get_collection(name):
    # NOTE: logically correct, but logic is not clear
    img_index_to_class.load_from_save()
    return Collection(name)


# TODO: this should be split
def load_embeddings_into_memory(collection):
    # loading embedding and identity data
    print("Loading in encodings & identity")
    encoded = np.load(const.ENCODED_SAVE_FILE)
    identity = np.load(const.IDENTITY_SAVE_FILE)

    # NOTE: unclear: loading embeddings into python lists
    embeddings = []
    indexing = []
    counter = 1
    for embed in encoded:
        embeddings.append(embed)
        indexing.append(counter)
        counter += 1

    # inserting data into collection
    print("Inserting data into a collection")
    insertInfo = collection.insert([indexing, embeddings])
    print(insertInfo)

    # indexing embeddings
    index_params = {
        'metric_type': 'L2',     # the distance metric (Euclidean distance)
        'index_type': "FLAT",    # Chose flat since we're dealing with a small dataset
        'params': {},
    }
    collection.create_index(field_name="embedding", index_params=index_params)

    # loading data into memory for querying
    collection.load()

    img_index_to_class.load_from_data(indexing, identity)
    img_index_to_class.save()


# Search for the nearest neighbor of the given image.
def search_image(collection, file_loc):
    query_vectors = encode.encode_faces(file_loc)
    insert_image = encode.draw_box_on_face(file_loc)

    print("Searching for the image ...🧐️")

    query_vector = query_vectors[0]
    search_params = {
        "params": {},  # since we're using FLAT index
    }
    results = collection.search(
        query_vector, "embedding", search_params, limit=3)
    print(results)

    if results is not None:
        temp = []

        plt.imshow(insert_image)
        for i in range(len(results)):
            img_class = img_index_to_class.get_class(results[i][0].id)
            temp.append(img_class)
        print(temp)

        # Displaing similar faces
        for i, x in enumerate(temp):
            fig = plt.figure()
            fig.suptitle('Face-' + str(i) + ", Celeb Folder: " + str(x))
            currentFolder = os.getenv('DATA_FOLDER') + str(x)
            total = min(len(os.listdir(currentFolder)), 6)

            for i, file in enumerate(os.listdir(currentFolder)[0:total], 1):
                fullpath = currentFolder + "/" + file
                img = mpimg.imread(fullpath)
                plt.subplot(2, 3, i)
                plt.imshow(img)
        plt.show(block=False)
        if (len(temp)) != 0:
            print("Wohoo, Similar Images found!🥳️")


def quick_search(collection, file_loc):
    query_vector = encode.encode_faces(file_loc)[0]
    search_params = {
        "params": {},  # since we're using FLAT index
    }
    results = collection.search(
        query_vector, "embedding", search_params, limit=1)
    ret = img_index_to_class.get_class(results[0][0].id)
    return ret


def delete_outdated_collection(name):
    utility.drop_collection(name)


def collection_exists(name):
    return utility.has_collection(name)
