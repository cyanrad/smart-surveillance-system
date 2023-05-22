from typing import Optional
import os
import requests
import json

AUTH_URI: str
temp = os.getenv("AUTH_URI")
if temp is not None:
    AUTH_URI = temp
else:
    exit(1)


def createOwner(name: str) -> dict:
    return json.loads(requests.post(
        AUTH_URI + "/createOwner",
        json={"name": name}
    ).text)


def createCamera(owner_id: str, is_black_list=False) -> dict:
    return json.loads(requests.post(
        AUTH_URI + "/createCamera",
        json={"is_black_list": is_black_list, "ownerid": owner_id}
    ).text)


def createPerson(ID: int, owner_id: str, className: str) -> dict:
    return json.loads(requests.post(
        AUTH_URI + "/createPerson",
        json={"class": className, "ownerid": owner_id,
              "ID": ID}
    ).text)


def createAccess(camera_id: str, person_id: str) -> dict:
    return json.loads(requests.post(
        AUTH_URI + "/createAccess",
        json={"cameraid": camera_id, "personid": person_id}
    ).text)


def getAccess(camera_id: int, person_id: str) -> Optional[dict]:
    data = requests.get(
        AUTH_URI + "/readAccess/" +
        str(camera_id) + "/" + person_id,
    ).text

    if data == "Failed":
        return None
    return json.loads(data)
