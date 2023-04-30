# Just to amplify intention
# .env for variables that are expected to be overloaded depending on environment
# this file is for unchanging global constants that are used in multiple files

# file structure is explained more in readme
# NOTE: all files indicated by the const import are generated if not exist

SAVED_PROCESSING_FOLDER = './processed_data/'
IMG_INDEX_TO_CLASS_FILE = SAVED_PROCESSING_FOLDER + 'img_index_to_class'
ENCODED_SAVE_FILE = SAVED_PROCESSING_FOLDER + 'encoded_save.npy'
CLASS_SAVE_FILE = SAVED_PROCESSING_FOLDER + 'class_save.npy'
