import envImport  # this has to be first
import os
import ai
import authentication
import asyncio
import resetDB

from faker import Faker
fake = Faker()


async def main():
    owner = authentication.createOwner(fake.name())
    cam_h = create_camera_and_person("hussain", owner["ID"])
    cam_p = create_camera_and_person("prime", owner["ID"])
    cam_t = create_camera_and_person("theo", owner["ID"])
    cam_v = create_camera_and_person("veritasium", owner["ID"])

    await asyncio.gather(
        ai.sendVideo(cam_h, "./videos/devs.mp4")
    )
    # ai.sendVideo(cam1, 0),
    # ai.sendVideo(cam2, "http://192.168.0.126:81/stream"))


def create_camera_and_person(name: str, owner_id: int):
    cam = authentication.createCamera(owner_id)
    person = authentication.createPerson(
        fake.random_number(digits=7), owner_id, name)

    for img in os.listdir("./faces/" + name):
        ai.addFace("./faces/" + name + "/" + img, name +
                   "_" + str(person["ID"]), str(owner_id))

    return cam


if __name__ == "__main__":
    asyncio.run(main())
