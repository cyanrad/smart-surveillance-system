import torch
import os
from facenet_pytorch import MTCNN, InceptionResnetV1
import cv2 as cv
import milvus
# import encode
from PIL import Image

# def detectAndDisplaySimple(frame):
#     tic = time.time()
#     #-- Detect faces
#     faces_location = mtcnn.detect(frame) 
#     cropped_face = mtcnn(frame)
#     print(faces_location)
#     if not (faces_location[0] is None):
#         for result in faces_location[0]:
#             x1 = int(result[0].item()) 
#             y1 = int(result[1].item()) 
#             x2 = int(result[2].item()) 
#             y2 = int(result[3].item()) 
#             frame = cv.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
    
#     if not (cropped_face is None):
#         resnet(cropped_face.unsqueeze(0))
#     cv.imshow('Capture - Face detection', frame)


# #-- init video stream
# camera_device = 0
# cap = cv.VideoCapture(camera_device)
# if not cap.isOpened:
#     print('--(!)Error opening video capture')
#     exit(0)

# #-- main loop
# while True:
#     ret, frame = cap.read()
#     if frame is None:
#         print('--(!) No captured frame -- Break!')
#         break

#     # do stuff here
#     if cv.waitKey(10) == 27:
#         break


milvus.create_collection()
milvus.import_all_embeddings()