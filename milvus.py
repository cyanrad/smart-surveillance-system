from pymilvus import (
    connections, 
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
import pickle

# TODO: should be loaded from env
HOST = '127.0.0.1'
PORT = '19530' 
VECTOR_DIAMENSION = 512
INDEX_FILE_SIZE = 32
# TODO: change name of this 
# not clear what is does
ID_TO_IDENTITY = None   # loaded in create_collection()
COLLECTION = None       # loaded in create_collection()
COLLECTION_NAME = 'faces'

connections.connect("default", host=HOST, port=PORT)

def create_collection():
    global ID_TO_IDENTITY
    global COLLECTION

    if not utility.has_collection(COLLECTION_NAME):
        print("Creating a collection on Milvus Database...📊️")
        fields = [
            FieldSchema(name='id', dtype=DataType.INT64, descrition='ids', is_primary=True, auto_id=False),
            FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, descrition='embedding vectors', dim=VECTOR_DIAMENSION)
        ]
        schema = CollectionSchema(fields=fields)
        collection = Collection(name=COLLECTION_NAME, schema=schema)
        print("Collection created✅️")
    
        print("Indexing the Collection...🔢️")
        index_params = {
            'metric_type':'L2',
            'index_type':"IVF_FLAT",
            'params':{"nlist":4096}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        print("Collection indexed✅️")
        return 1  

    else:
        print("Collection exsits")
        collection = Collection(COLLECTION_NAME)
        try:
            with open('id_to_class', 'rb') as fp:
                ID_TO_IDENTITY = pickle.load(fp)
            return 0
        except:
            return 1