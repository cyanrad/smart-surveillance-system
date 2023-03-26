# Just to amplify intention 
# .env for variables that are expected to be overloaded depending on environment
# this file is for unchanging global constants that are used in multiple files

# file structure is explained more in readme

SAVED_PROCESSING_FOLDER = './processed_data/'
IMG_INDEX_TO_CLASS_FILE = SAVED_PROCESSING_FOLDER + 'img_index_to_class'
ENCODED_SAVE_FILE = SAVED_PROCESSING_FOLDER + 'encoded_save.npy'
IDENTITY_SAVE_FILE = SAVED_PROCESSING_FOLDER + 'identity_save.npy'