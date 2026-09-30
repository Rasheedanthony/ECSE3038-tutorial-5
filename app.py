import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool


# Your handlers go below this line.


@app.get("/devices")
def get_devices():
    return list(devices.find({}, {"_id": 0}))


@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0})
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device



@app.post("/devices", status_code=201)
def create_device(device: Device):
    existing = devices.find_one({"name": device.name})

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="A device with that name already exists"
        )

    new_device = device.model_dump()
    devices.insert_one(new_device)
    new_device.pop("_id", None)

    return new_device



@app.put("/devices/{name}")
def put_device(name: str, device: Device, response: Response):
    data = device.model_dump()
    data["name"] = name
    result = devices.replace_one({"name": name}, data.copy(), upsert=True)
    if result.matched_count == 0:
        response.status_code = 201
        response.headers["Location"] = f"/devices/{name}"
    return data