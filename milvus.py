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
                    descrition='Index/Identifier of the embedding', is_primary=True, auto_id=True),
        FieldSchema(name='class', dtype=DataType.VARCHAR,  # arbitrary max_length (should handle most full names)
                    descrition='The class (i.e. the person\'s identity) the embedding belongs to', max_length=64),
        FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR,
                    descrition='embedding vectors representing a face in the database', dim=VECTOR_DIAMENSION),
    ]
    schema = CollectionSchema(fields=fields)
    return Collection(name=name, schema=schema)


def get_collection(name):
    return Collection(name)


def uploading_embeddings(collection):
    print("Loading saved encodings & identity data")
    embeddings = np.load(const.ENCODED_SAVE_FILE)
    embeddings_class = np.load(const.CLASS_SAVE_FILE)

    # inserting data into collection
    print("Inserting data into a collection")
    insert_info = collection.insert([embeddings_class, embeddings])
    print(insert_info)

    # indexing embeddings
    index_params = {
        'metric_type': 'L2',     # the distance metric (Euclidean distance)
        'index_type': "FLAT",    # Chose flat since we're dealing with a small dataset
        'params': {},
    }
    collection.create_index(field_name="embedding", index_params=index_params)

    # loading data into memory for querying
    collection.load()


def upload_new_embedding(collection, img, img_class):
    embeddings = np.concatenate(encode.encode_faces(img))
    insert_info = collection.insert([img_class, embeddings])
    print(insert_info)


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
