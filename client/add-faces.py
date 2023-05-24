
import envImport  # this has to be first
import os
import ai
import authentication
import asyncio

for img in os.listdir("./faces/" + "Radwan"):
    ai.addFace("./faces/" + "Radwan" + "/" + img, "Radwan" +
               "_" + str(9966383), str(2))
