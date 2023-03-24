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


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def import_all_embeddings():
    global ID_TO_IDENTITY
    global COLLECTION

    print("Loading in encoded vectors...")
    encoded = np.load("encoded_save.npy")
    identity = np.load("identity_save.npy")

    encoded = np.array_split(encoded, 4, axis=0)
    identity = identity.astype(int)

    identity = np.array_split(identity, 4, axis=0)

    ID_TO_IDENTITY = []

    entities = [0,0]
    embeddings = []
    indexing = []
    counter = 1
    for encode in encoded:
        for embed in encode:
            embeddings.append(embed)
            indexing.append(counter)
            counter += 1
            # print(counter)

    indexing = list(split(indexing, 5))
    embeddings = list(split(embeddings, 5))

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

#TODO: CHECK PYMILVUS VERSIONS