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


# TODO: this should absolutely be handled somewhere else
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
    collection = Collection(name=name, schema=schema)

    # indexing embeddings
    index_params = {
        'metric_type': 'L2',     # the distance metric (Euclidean distance)
        'index_type': "FLAT",    # Chose flat since we're dealing with a small dataset
        'params': {},
    }
    collection.create_index(field_name="embedding", index_params=index_params)

    # loading data into memory for querying
    collection.load()

    return collection


def get_collection(name: str):
    return Collection(name)


def delete_outdated_collection(name):
    utility.drop_collection(name)


def collection_exists(name):
    return utility.has_collection(name)


def upload_embeddings_from_save(collection):
    # check if files actually exist
    # TODO: should do a warning if it fails
    if not (os.path.isfile(const.ENCODED_SAVE_FILE)
            and os.path.isfile(const.CLASS_SAVE_FILE)):
        return

    embeddings = np.load(const.ENCODED_SAVE_FILE)
    embeddings_class = np.load(const.CLASS_SAVE_FILE)

    insert_info = collection.insert([embeddings_class, embeddings])
    print(insert_info)


def upload_embeddings_from_dataset(collection, dataset):
    embeddings, embeddings_class = encode.encode_faces_from_dataset(dataset)

    insert_info = collection.insert([embeddings_class, embeddings])
    print(insert_info)


def upload_embedding_from_img(collection, img, img_class):
    embeddings_and_boxes = encode.encode_faces(img, 1, 1)
    if not embeddings_and_boxes:
        return False

    embeddings = np.concatenate(embeddings_and_boxes[0])

    insert_info = collection.insert([img_class, embeddings])
    print(insert_info)
    return True


# return: an array of found faces
def quick_search(collection, img, threshold=0.3):
    embeddings_and_boxes = encode.encode_faces(img)
    if not embeddings_and_boxes:
        return []

    search_params = {
        "params": {},  # empty since we're using FLAT index
    }

    results = collection.search(
        embeddings_and_boxes[0][0], "embedding", search_params, limit=1, output_fields=["class"])

    # detected but not known
    # e.g. (["", "", ""], [pos1, pos2, pos3])
    if not results[0]:
        # yes i know this is fucked byond comprihension
        # i'm just tying to get shit done okay
        # in short it just returns n empty strings, where n is the number of detected faces in an image
        # alogside the position of the detected faces
        return (["" for _ in range(embeddings_and_boxes[0][0].shape[0])], embeddings_and_boxes[1])

    detected_classes = []
    for result in results:
        # detected and known
        print(result[0].distance)
        if result[0].distance < threshold:
            detected_classes.append(result[0].entity.get('class'))
        # detected but not confident
        # e.g. (["", "", ""], [pos1, pos2, pos3])
        else:
            detected_classes.append("")

    return (detected_classes, embeddings_and_boxes[1])
