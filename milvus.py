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

# TODO: should be loaded from env
HOST = '127.0.0.1'
PORT = '19530' 
VECTOR_DIAMENSION = 512
INDEX_FILE_SIZE = 32
# TODO: change name of this not clear what is does
ID_TO_IDENTITY = None   # loaded in create_collection()
COLLECTION = None       # loaded in create_collection()
COLLECTION_NAME = 'faces'

connections.connect("default", host=HOST, port=PORT)

# TODO: there should be a function for initializationa and one to create a connection
def create_collection():
    global ID_TO_IDENTITY
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
    
        print("Indexing the Collection...🔢️")
        index_params = {
            'metric_type':'L2',
            'index_type':"IVF_FLAT",
            'params':{"nlist":4096}
        }
        COLLECTION.create_index(field_name="embedding", index_params=index_params)
        print("Collection indexed✅️")
        return 1  

    else:
        print("Collection exsits")
        COLLECTION = Collection(COLLECTION_NAME)
        try:
            with open('id_to_class', 'rb') as fp:
                ID_TO_IDENTITY = pickle.load(fp)
            return 0
        except:
            return 1


def split_list(src_list, slices_count):
    """
    Split a list into a specified number of slices.

    Args:
    src_list (list): The list to be split.
    num_slices (int): The number of slices to create.

    Returns:
    dst_list (list[slices]): A list of the slices
    """
    slice_length, reminder = divmod(len(src_list), slices_count)

    slices = []
    for i in range(slices_count):
        start = i*slice_length + min(i, reminder)
        end = (i+1)*slice_length + min(i+1, reminder)
        slices.append(src_list[start:end])
    
    return slices


def import_all_embeddings():
    global ID_TO_IDENTITY
    global COLLECTION

    print("Loading in encoded vectors...")
    encoded = np.load("encoded_save.npy")
    identity = np.load("identity_save.npy")

    #NOTE: why are we splitting into 4 arrays?
    identity = identity.astype(int)
    identity = np.array_split(identity, 4)
    encoded = np.array_split(encoded, 4)

    #NOTE: we're loading ID_TO_IDENTITY in create collection then emptying it here?
    ID_TO_IDENTITY = []

    entities = [0,0]
    embeddings = []
    indexing = []
    counter = 1

    # loading embeddings #NOTE: why are we doing this after splitting the array into 4???
    for encode in encoded:
        for embed in encode:
            embeddings.append(embed)
            indexing.append(counter)
            counter += 1

    #NOTE: the fuck?
    indexing = list(split_list(indexing, 5))
    embeddings = list(split_list(embeddings, 5))
    print(type(embeddings))

    for i in range(5):
        entities[0] = indexing[i]
        entities[1] = embeddings[i]
        print("Initiating Data Insertion {}".format(i))
        print(COLLECTION.insert(entities))
        print("Data Inserted {}".format(i))

    for x in range(len(encoded)):
        for z in range(len(indexing)):
            ID_TO_IDENTITY.append((indexing[z], identity[x][z]))
    print("Id to identity Done")

    # TODO: this works but this is terrible modify it
    index_params = {
        'metric_type':'L2',
        'index_type':"IVF_FLAT",
        'params':{"nlist":4096}
    }
    COLLECTION.create_index(field_name="embedding", index_params=index_params)
    COLLECTION.load() # RPC error here

    with open('id_to_class', 'wb') as fp:
        pickle.dump(ID_TO_IDENTITY, fp)
    print("Vectors loaded in.✅️")

# Search for the nearest neighbor of the given image. 
def search_image(file_loc):
    global COLLECTION
    global ID_TO_IDENTITY

    query_vectors  = encode.encode_faces(file_loc)
    insert_image = encode.draw_box_on_face(file_loc)
    
    print("Searching for the image ...🧐️")
    search_params = {
        "params": {"nprobe": 2056},
    }
    query_vector = query_vectors[0]
    results = COLLECTION.search(query_vector, "embedding", search_params, limit=3)
    print(results)

    if results:
        temp = []
        plt.imshow(insert_image)
        for x in range(len(results)):
            for i, v in ID_TO_IDENTITY:
                if results[x][0].id == i:
                    temp.append(v)
        print(temp)
        for i, x in enumerate(temp):
            fig = plt.figure()
            fig.suptitle('Face-' + str(i) + ", Celeb Folder: " + str(x))
            currentFolder = './dataFull/' + str(x)
            total = min(len(os.listdir(currentFolder)), 6)

            for i, file in enumerate(os.listdir(currentFolder)[0:total], 1):
                fullpath = currentFolder+ "/" + file
                img = mpimg.imread(fullpath)
                plt.subplot(2, 3, i)
                plt.imshow(img)
        plt.show(block = False)
        if(len(temp))!=0:
            print("Wohoo, Similar Images found!🥳️")
        print(temp)

# Delete the collection
def delete_collection():
    print("deleteing collection")
    utility.drop_collection(COLLECTION_NAME)