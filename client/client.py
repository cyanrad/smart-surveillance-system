import envImport  # this has to be first
import os
import ai
import authentication
import asyncio

from faker import Faker
fake = Faker()


async def main():
    owner = authentication.createOwner(fake.name())
    cam1 = authentication.createCamera(owner["ID"])
    cam2 = authentication.createCamera(owner["ID"])
    print(cam1)
    print(cam2)
    personName = "Radwan"
    person = authentication.createPerson(fake.random_number(
        digits=7), owner["ID"], personName)
    print(person)

    # allowing the person on camera 1
    authentication.createAccess(cam1["ID"], person["ID"])

    # adding classes to db
    # for face in os.listdir("./faces"):
    #     for img in os.listdir("./faces/" + face):
    #         ai.addFace("./faces/" + face + "/" + img, personName +
    #                    "_" + str(person["ID"]), "0")

    await asyncio.gather(ai.sendVideo(cam1, "ex.mp4"), ai.sendVideo(cam2, "ex.mp4"))

if __name__ == "__main__":
    asyncio.run(main())
