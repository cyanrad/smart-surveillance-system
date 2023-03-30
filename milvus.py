from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
import numpy as np
import os

import encode
import const


connections.connect("default", host=os.getenv('HOST'), port=os.getenv('PORT'))


def create_collection(name):
    VECTOR_DIAMENSION = 512
    print("Creating a collection on Milvus Database...📊️")
    fields = [
        FieldSchema(name='id', dtype=DataType.INT64,
                    descrition='Index/Identifier of the embedding', is_primary=True, auto_id=False),
        FieldSchema(name='class', dtype=DataType.VARCHAR,  # arbitrary max_length (should handle most full names)
                    descrition='The class (i.e. the person\'s identity) the embedding belongs to', max_length=64),
        FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR,
                    descrition='embedding vectors representing a face in the database', dim=VECTOR_DIAMENSION),
    ]
    schema = CollectionSchema(fields=fields)
    return Collection(name=name, schema=schema)


def get_collection(name):
    return Collection(name)


# TODO: this should be split
def load_embeddings_into_memory(collection):
    # loading embedding and identity data
    # converting them to python lists for insertion into milvus
    print("Loading in encodings & identity")
    encoded = np.load(const.ENCODED_SAVE_FILE).tolist()
    identity = np.load(const.CLASS_SAVE_FILE).tolist()
    milvus_id = [i for i in range(len(encoded))]

    # inserting data into collection
    print("Inserting data into a collection")
    insertInfo = collection.insert([milvus_id, identity, encoded])
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


def quick_search(collection, img, threshold=0.6):
    query_vector = encode.encode_faces(img)
    search_params = {
        "params": {},  # since we're using FLAT index
    }

    if len(query_vector) == 0:
        return []

    results = collection.search(
        query_vector[0], "embedding", search_params, limit=1, output_fields=["class"])

    detected_classes = []
    for result in results:
        if result[0].distance < threshold:
            detected_classes.append(result[0].entity.get('class'))
        else:
            detected_classes.append(-1)

    return detected_classes


def delete_outdated_collection(name):
    utility.drop_collection(name)


def collection_exists(name):
    return utility.has_collection(name)
