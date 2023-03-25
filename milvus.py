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
    """
    Creates a collection & indexes it using an L2 metric and an IVF_FLAT index type.
    @ collection exists, load a pickled dictionary called 'id_to_class' into ID_TO_IDENTITIES

    Returns:
        0 @ default
        1 @ collection created or id_to_class file doesn't exist
    """
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



def import_all_embeddings():
    global ID_TO_IDENTITY
    global COLLECTION

    #NOTE: unclear: emptying data
    ID_TO_IDENTITY = []

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

    #NOTE: unclear: potentailly for performance/memory
    identity = identity.astype(int)
    identity = np.array_split(identity, 4)
    encoded = np.array_split(encoded, 4)

    #NOTE: unclear: potentailly for performance/memory
    indexing = split_list(indexing, 5)
    embeddings = split_list(embeddings, 5)

    # inserting data into collection
    entities = [[],[]]
    for i in range(5):
        entities[0] = indexing[i]
        entities[1] = embeddings[i]

        print(f"inserting data {i}")
        insertInfo = COLLECTION.insert(entities)
        print(insertInfo)

    # indexing embeddings
    index_params = {
        'metric_type':'L2',         # the distance metric (Euclidean distance)
        'index_type':"FLAT",        # Chose flat since we're dealing with a small dataset
        'params':{},
    }
    COLLECTION.create_index(field_name="embedding", index_params=index_params)

    # loading data into memory for querying
    COLLECTION.load()

    # loading data embedding & index data into ID_TO_IDENTITY
    # what the fuck is this??
    for x in range(len(encoded)):
        for z in range(len(indexing)):
            ID_TO_IDENTITY.append((indexing[z], identity[x][z]))
    print("Id to identity Done")

    # loading data embedding & index data into id_to_class file
    with open('id_to_class', 'wb') as fp:
        pickle.dump(ID_TO_IDENTITY, fp)
    print("Id to class Done")

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


# Search for the nearest neighbor of the given image. 
def search_image(file_loc):
    global COLLECTION
    global ID_TO_IDENTITY

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

        # this literally doesn't make any sence
        # they're COMPARING A TUPLE WIT HA LIST....WHAT??
        for x in range(len(results)):
            for i, v in ID_TO_IDENTITY:
                print(results[x][0])
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