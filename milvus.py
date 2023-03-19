from pymilvus import connections

_HOST = '127.0.0.1'
_PORT = '19530' 
collection_name = 'faces'
_DIM = 512  
_INDEX_FILE_SIZE = 32  
id_to_identity = None

connections.connect("default", host=_HOST, port=_PORT)
