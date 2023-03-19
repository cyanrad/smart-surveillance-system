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

    def collate_fn(x):
        return x[0]

    dataset = datasets.ImageFolder('./celeb_reorganized')
    dataset.idx_to_class = {i:c for c, i in dataset.class_to_idx.items()}
    loader = DataLoader(dataset, collate_fn=collate_fn, num_workers=workers)


    encoded = []
    identity = []
    count = len(loader)

    for x, y in loader:
        try:
            x_aligned, prob = mtcnn(x, return_prob=True)
        except:
            print(x)
            plt.imshow(x)
            plt.show()
        if x_aligned is not None:
            x_aligned = x_aligned.to(device)
            embeddings = resnet(x_aligned).detach().cpu()
            embeddings = embeddings.numpy()
            encoded.append(embeddings)
            for x in range(embeddings.shape[0]):
                identity.append(dataset.idx_to_class[y])
            if count %1000 == 0:
                print(count, x_aligned.shape, dataset.idx_to_class[y])
            count -= 1
           
    encoded = np.concatenate(encoded, 0)
    encoded = np.squeeze(encoded)
    print(encoded.shape)
    identity = np.array(identity)
    np.save("identity_save.npy", identity)
    np.save("encoded_save.npy", encoded)
    encoded = np.load("encoded_save.npy")
    identity = np.load("identity_save.npy")
    print(encoded.shape, identity.shape)

# Gets embeddings for all the faces in the image. 
def get_image_vectors(file_loc):
    img = Image.open(file_loc)
    bbx, prob = mtcnn.detect(img)
    embeddings = None
    if (bbx is not None):
        face_cropped = mtcnn.extract(img,bbx,None).to(device)
        embeddings = resnet(face_cropped).detach().cpu()
        embeddings = embeddings.numpy()
        draw = ImageDraw.Draw(img)
        for i, box in enumerate(bbx):
            draw.rectangle(box.tolist(), outline=(255,0,0))
            draw.text((box.tolist()[0] + 2,box.tolist()[1]), "Face-" + str(i), fill=(255,0,0))

    return embeddings, img
