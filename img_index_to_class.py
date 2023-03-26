import os
import pickle

import const

#NOTE: this file acts as a singleton
#NOTE: I hate how i implemented this, but i'm not skilled enough to figure something better

# each image has a unique integer index
# each image has a class (the identity of the person in the img)
# this is a map between them
_data = {}

def save():
    _asset_data_is_not_empty()
    with open(const.IMG_INDEX_TO_CLASS_FILE, 'wb') as fp:
        pickle.dump(_data, fp)
    print("Image index to class data saved")

def load_from_save():
    global _data
    _asset_data_is_empty()
    with open(const.IMG_INDEX_TO_CLASS_FILE, 'rb') as fp:
        _data = pickle.load(fp)

def load_from_data(indexing, identity): 
    # TODO: write args comment
    global _data
    _asset_data_is_empty()
    for i in range(len(indexing)):
        _data[indexing[i]] = identity[i]

def get_class(result_index):
    _asset_data_is_not_empty()
    return _data[result_index]

def saved():
    os.path.isfile(const.IMG_INDEX_TO_CLASS_FILE)



def _asset_data_is_empty():
    assert len(_data) == 0

def _asset_data_is_not_empty():
    assert len(_data) != 0