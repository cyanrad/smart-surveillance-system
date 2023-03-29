import torch
import os
import numpy as np

from PIL import ImageDraw
from facenet_pytorch import MTCNN, InceptionResnetV1
from torchvision import datasets

import const


# Selecting the device GPU/CPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'


# Initializng models (detection & recognition)
mtcnn = MTCNN(device=device, keep_all=True, factor=0.6, margin=14)
resnet = InceptionResnetV1(pretrained='vggface2', device=device).eval()


def preprocess_faces():
    # -- loading face images
    # Each image is associated with a class.
    # Class is determined by subdirecotry.
    # Each class has an ID.
    dataset = datasets.ImageFolder(os.getenv('DATA_FOLDER'))
    dataset.idx_to_class = {id: c for c, id in dataset.class_to_idx.items()}

    # NOTE: check if we can convert this to a list of tuples
    # Used so that we don't have to recompute face detection and encoding
    # for each `embeddeding` in `face_embedding_list`
    # it's class is stored in the corresponding index in `detected_classes`
    embeddings_list = []
    embeddings_class = []

    count = len(dataset)
    for img, id in dataset:
        # -- face detection
        try:
            # converting them to CUDA complient floats for GPU usage
            normalized_face = mtcnn(img).cuda()
        except:
            print(f"dropping {id}: {img}, no face detected")
            continue

        if (len(normalized_face) > 1):
            print(f"dropping {id}: {img}, more than one face detected")
            continue

        # -- face encoding
        # detaching gradient from tensor, then moving data into cpu for conversion, since we use CUDA/GPU
        embeddings = resnet(normalized_face).detach().cpu()
        embeddings = embeddings.numpy()

        # -- saving results
        embeddings_list.append(embeddings)
        embeddings_class.append(dataset.idx_to_class[id])

        # -- print progress
        if count % 100 == 0:
            print(count, "remaining")
        count -= 1

    # convert python lists to np.ndarray for compatibility
    # NOTE: no clue why concatenate is the only one that works
    embeddings_list = np.concatenate(embeddings_list)
    embeddings_class = np.array(embeddings_class)

    np.save(const.ENCODED_SAVE_FILE, embeddings_list)
    np.save(const.CLASS_SAVE_FILE, embeddings_class)


# index of x,y,w,h in result array
FACE_BOX_DATA = 0

# TODO: should be changed so that image load/save handling is not here


def encode_faces(img):
    faces_location = mtcnn.detect(img)

    embeddings = []
    if (faces_location is not None):
        face_cropped = mtcnn.extract(
            img=img, batch_boxes=faces_location[FACE_BOX_DATA], save_path=None)
        if face_cropped is not None:
            face_cropped = face_cropped.cuda()
            embedding = resnet(face_cropped).detach().cpu()
            embedding = embedding.numpy()
            embeddings.append(embedding)

    return embeddings, faces_location


def draw_box_on_face(img, faces_location):
    draw = ImageDraw.Draw(img)
    for i, box in enumerate(faces_location[FACE_BOX_DATA]):
        draw.rectangle(box.tolist(), outline=(255, 0, 0))
        draw.text((box.tolist()[0] + 2, box.tolist()[1]),
                  "Face-" + str(i), fill=(255, 0, 0))

    return img
