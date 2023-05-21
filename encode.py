import torch
import os
import numpy as np

from PIL import ImageDraw
from facenet_pytorch import MTCNN, InceptionResnetV1, extract_face
from torchvision import datasets

import const


# Selecting the device GPU/CPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(device)


# -- Initializng models (detection & recognition)
mtcnn = MTCNN(device=device, keep_all=True, factor=0.6, margin=14)
resnet = InceptionResnetV1(pretrained='vggface2', device=device).eval()


def encode_faces_from_dataset(dataset_path, save_data=False):
    # TODO: handling invalid dataset_path

    # -- loading face images
    # Each image is associated with a class.
    # Class is determined by subdirecotry.
    # Each class has an ID.
    dataset = datasets.ImageFolder(dataset_path)
    dataset.idx_to_class = {id: c for c, id in dataset.class_to_idx.items()}

    # for each `embeddeding` in `embedding_list`
    # it's class is stored in the corresponding index in `embeddings_class`
    embeddings_list = []
    embeddings_class = []

    count = len(dataset)
    for img, id in dataset:
        embeddings = encode_faces(img, 1, 1)
        if not embeddings:
            continue

        # -- saving results
        # [0] since we expect only one vector
        embeddings_list.append(embeddings[0])
        embeddings_class.append(dataset.idx_to_class[id])

        # -- print progress
        if count % 100 == 0:
            print(count, "remaining")
        count -= 1

    if save_data:
        if not os.path.exists(const.SAVED_PROCESSING_FOLDER):
            os.makedirs(const.SAVED_PROCESSING_FOLDER)

        np.save(const.ENCODED_SAVE_FILE, embeddings_list)
        np.save(const.CLASS_SAVE_FILE, embeddings_class)

    # -- convert python lists to np.ndarray for compatibility
    embeddings_list = np.concatenate(embeddings_list)
    embeddings_class = np.array(embeddings_class)
    return embeddings_list, embeddings_class


# TODO: now i could be a good engineer and modify this so it raises erros
#       but am i????
def encode_faces(img, min_count=0, max_count=20):
    boxes, _, _ = mtcnn.detect(img, landmarks=True)

    # no face is detected
    if boxes is None:
        print("no face detected")
        return []

    unbatched_normalized_faces: list[torch.Tensor] = []
    for box in boxes:
        unbatched_normalized_faces.append(extract_face(img, box))
    normalized_faces = torch.stack(unbatched_normalized_faces, dim=0)

    # limit number of faces (more faces == more processing)
    face_count = len(normalized_faces)
    if (face_count < min_count or face_count > max_count):
        print("bad number of faces detected", face_count)
        return []

    # -- face encoding
    # converting normalized face to CUDA complient tensor
    # detaching gradient from tensor, then moving data into cpu for conversion, since we use CUDA/GPU
    embedding = resnet.forward(normalized_faces.cuda()).detach().cpu().numpy()
    embeddings = [embedding]

    return (embeddings, boxes)


def draw_box_on_face(img, faces_location):
    # index of x,y,w,h in result array
    FACE_BOX_DATA = 0

    draw = ImageDraw.Draw(img)
    for i, box in enumerate(faces_location[FACE_BOX_DATA]):
        draw.rectangle(box.tolist(), outline=(255, 0, 0))
        draw.text((box.tolist()[0] + 2, box.tolist()[1]),
                  "Face-" + str(i), fill=(255, 0, 0))

    return img
