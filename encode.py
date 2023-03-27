import torch
import os
import numpy as np

from PIL import Image, ImageDraw
from facenet_pytorch import MTCNN, InceptionResnetV1
from torchvision import datasets
from torch.utils.data import DataLoader
from matplotlib import pyplot as plt

import const


# Selecting the device CPU/GPU
workers = 0 if os.name == 'nt' else 4
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {} 💻️'.format(device))


# Initializng models (detection & recognition)
mtcnn = MTCNN(device=device, keep_all=True)
resnet = InceptionResnetV1(pretrained='vggface2').eval()


def preprocess_faces():
    # Each image is associated with a class.
    # class is determined by subdirecotry, each class has an id
    dataset = datasets.ImageFolder(os.getenv('DATA_FOLDER'))
    dataset.idx_to_class = {i: c for c, i in dataset.class_to_idx.items()}

    # unclear, used for batch processing when using a map for data
    def collate_fn(x):
        return x[0]
    dataIter = DataLoader(dataset, collate_fn=collate_fn, num_workers=workers)

    face_embeddings_list = []
    detected_classes = []
    # for each `embeddeding` in `face_embedding_list`
    # it's class is storred in the corresponding index in `detected_classes`
    count = len(dataIter)

    print("generating face embeddings")
    for img, id in dataIter:
        try:
            normalized_face = mtcnn(img)
        except:
            # if face detection fails
            print(img)
            plt.imshow(img)
            plt.show()

        if normalized_face is not None:
            # NOTE: no clue what detach().cpu() does
            embeddings = resnet(normalized_face).detach().cpu()
            embeddings = embeddings.numpy()
            face_embeddings_list.append(embeddings)

            # adding detected classes
            for unused in range(embeddings.shape[0]):
                detected_classes.append(dataset.idx_to_class[id])

            # print progress
            if count % 100 == 0:
                print(count, "remaining")
            count -= 1

    # convert python lists to np.ndarray for compatibility
    face_embeddings_list = np.concatenate(face_embeddings_list)
    face_embeddings_list = np.squeeze(
        face_embeddings_list)  # TODO: seems useless
    detected_classes = np.array(detected_classes)

    print("Saving...")
    np.save(const.ENCODED_SAVE_FILE, face_embeddings_list)
    np.save(const.IDENTITY_SAVE_FILE, detected_classes)
    face_embeddings_list = np.load(const.ENCODED_SAVE_FILE)
    detected_classes = np.load(const.IDENTITY_SAVE_FILE)
    print("Saved")


# index of x,y,w,h in result array
FACE_BOX_DATA = 0

# TODO: should be changed so that image load/save handling is not here


def encode_faces(img_path):
    img = Image.open(img_path)

    faces_location = mtcnn.detect(img)
    embeddings = []

    if (faces_location is not None):
        face_cropped = mtcnn.extract(
            img=img, batch_boxes=faces_location[FACE_BOX_DATA], save_path=None)
        embedding = resnet(face_cropped).detach().cpu()
        embedding = embedding.numpy()
        embeddings.append(embedding)

    return embeddings


def draw_box_on_face(img_path, save_path=None):
    img = Image.open(img_path)
    face_location = mtcnn.detect(img)

    draw = ImageDraw.Draw(img)
    for i, box in enumerate(face_location[FACE_BOX_DATA]):
        draw.rectangle(box.tolist(), outline=(255, 0, 0))
        draw.text((box.tolist()[0] + 2, box.tolist()[1]),
                  "Face-" + str(i), fill=(255, 0, 0))

    if save_path is not None:
        img.save(save_path)

    return img
