from fastapi import FastAPI
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import models
from schemas import VehicleCreate, VehicleUpdate, VehicleRead

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, World!"}
