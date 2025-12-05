from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from database import Base, engine, get_db
import models
from schemas import VehicleCreate, VehicleUpdate, VehicleRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

# HELPER FUNCTIONS

def normalizeVin(vin: str) -> str:
    return vin.strip().upper()

# ROUTES

@app.get("/")
def root():
    return {"message": "Hello, World!"}


@app.get("/vehicles/", response_model=list[VehicleRead])
def list_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).all()
    return vehicles


@app.post("/vehicles/", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle_in: VehicleCreate, db: Session = Depends(get_db)):
    vinNorm = normalizeVin(vehicle_in.vin)

    # no duplicate VIN
    existing = db.query(models.Vehicle).filter(models.Vehicle.vin == vinNorm).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"vin": ["VIN already exists"]},
        )

    vehicle = models.Vehicle(
        vin=vinNorm,
        manuName=vehicle_in.manuName,
        description=vehicle_in.description,
        horsePower=vehicle_in.horsePower,
        modelName=vehicle_in.modelName,
        modelYear=vehicle_in.modelYear,
        purchasePrice=vehicle_in.purchasePrice,
        fuelType=vehicle_in.fuelType,
    )

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle
