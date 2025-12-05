from fastapi import FastAPI
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import models
from schemas import VehicleCreate, VehicleUpdate, VehicleRead

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, World!"}

@app.get("/vehicles/", response_model=list[VehicleRead])
def list_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).all()
    return vehicles

@app.post("/vehicles/", response_model=VehicleRead, status_code=status.GTTP_201_CREATED)
def 