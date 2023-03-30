import torch
import os
import numpy as np

from PIL import ImageDraw
from facenet_pytorch import MTCNN, InceptionResnetV1
from torchvision import datasets

import const


# Selecting the device GPU/CPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'


# -- Initializng models (detection & recognition)
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
    # -- Lists to save processed data
    # for each `embeddeding` in `face_embedding_list`
    # it's class is stored in the corresponding index in `detected_classes`
    embeddings_list = []
    embeddings_class = []

    count = len(dataset)
    for img, id in dataset:
        normalized_face = mtcnn(img)

        if normalized_face is None:
            print(f"dropping {id}: {img}, no face detected")
            continue

        if (len(normalized_face) > 1):
            print(f"dropping {id}: {img}, more than one face detected")
            continue

        # -- face encoding
        # converting normalized face to CUDA complient tensor
        # detaching gradient from tensor, then moving data into cpu for conversion, since we use CUDA/GPU
        embeddings = resnet(normalized_face.cuda()).detach().cpu()
        embeddings = embeddings.numpy()  # converting to numpy for compatibility

        # -- saving results
        embeddings_list.append(embeddings)
        embeddings_class.append(dataset.idx_to_class[id])

        # -- print progress
        if count % 100 == 0:
            print(count, "remaining")
        count -= 1

    # -- convert python lists to np.ndarray for compatibility
    embeddings_list = np.concatenate(embeddings_list)
    embeddings_class = np.array(embeddings_class)

    np.save(const.ENCODED_SAVE_FILE, embeddings_list)
    np.save(const.CLASS_SAVE_FILE, embeddings_class)


def encode_faces(img):
    normalized_faces = mtcnn(img)

    if normalized_faces is None:
        return []

    embeddings = []
    embedding = resnet(normalized_faces.cuda()).detach().cpu().numpy()
    embeddings.append(embedding)

    return embeddings


def draw_box_on_face(img, faces_location):
    # index of x,y,w,h in result array
    FACE_BOX_DATA = 0

    draw = ImageDraw.Draw(img)
    for i, box in enumerate(faces_location[FACE_BOX_DATA]):
        draw.rectangle(box.tolist(), outline=(255, 0, 0))
        draw.text((box.tolist()[0] + 2, box.tolist()[1]),
                  "Face-" + str(i), fill=(255, 0, 0))

    return img
