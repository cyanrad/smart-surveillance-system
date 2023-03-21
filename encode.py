import torch
import os
import numpy as np

from PIL import Image, ImageDraw
from facenet_pytorch import MTCNN, InceptionResnetV1
from torchvision import datasets
from torch.utils.data import DataLoader
from  matplotlib import pyplot as plt


# Selecting the device CPU/GPU 
workers = 0 if os.name == 'nt' else 4
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {} 💻️'.format(device))
from facenet_pytorch import MTCNN, InceptionResnetV1

# Initializng models (detection & recognition)
mtcnn = MTCNN(device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval()


def preprocess_images():
    # Each image is associated with a class. 
    # class is determined by subdirecotry, each class has an id
    dataset = datasets.ImageFolder('./data')
    dataset.idx_to_class = {i:c for c, i in dataset.class_to_idx.items()}

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
            # when i removed the below the code worked, if the code break this is why
            # normalized_face = normalized_face.to(device)
            embeddings = resnet(normalized_face.unsqueeze(0)).detach().cpu() #NOTE: no clue what detach().cpu() does 
            embeddings = embeddings.numpy()
            face_embeddings_list.append(embeddings)

            # adding detected classes
            for unused in range(embeddings.shape[0]):
                detected_classes.append(dataset.idx_to_class[id])

            # print progress
            if count%100 == 0:
                print(count, "remaining")
            count -= 1
           
    # Array Manipulations
    # convert python lists to np.ndarray for compatibility
    face_embeddings_list = np.concatenate(face_embeddings_list)
    face_embeddings_list = np.squeeze(face_embeddings_list) #TODO: seems useless
    detected_classes = np.array(detected_classes)


    print("Saving...")
    # don't know why it reloads though
    np.save("identity_save.npy", detected_classes)
    np.save("encoded_save.npy", face_embeddings_list)
    face_embeddings_list = np.load("encoded_save.npy")
    detected_classes = np.load("identity_save.npy")
    print("Saved")


def detect_and_encode_face(img):
    faces_location = mtcnn.detect(img)
    embeddings = None

    if (faces_location is not None):
        face_cropped = mtcnn.extract(img, faces_location, None)
        embeddings = resnet(face_cropped).detach().cpu()
        embeddings = embeddings.numpy()

    return faces_location, embeddings 

def draw_box_on_face(img, faces_location):
    draw = ImageDraw.Draw(img)
    for i, box in enumerate(faces_location):
        draw.rectangle(box.tolist(), outline=(255,0,0))
        draw.text((box.tolist()[0] + 2,box.tolist()[1]), "Face-" + str(i), fill=(255,0,0))
    return img