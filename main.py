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

def validateVin(vin: str) -> str:
    if vin is None:
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"vin": ["VIN cannot be null"]}
        )
    
    vinNorm = normalizeVin(vin)

    if len(vinNorm) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"vin: [VIN cannot be empty]"},
        )

    # based on the rules set in the United States
    # must be exactly 17 characters
    if len(vinNorm) != 17:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"vin": ["VIN must be exactly 17 characters"]},
        )

    # illegal char: I, O, Q
    illegal_chars = {"I", "O", "Q"}
    if any(ch in illegal_chars for ch in vinNorm):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"vin": ["VIN cannot contain the letters I, O, or Q"]},
        )

    # VIN must be alphanumeric (letters + numbers only)
    if not vinNorm.isalnum():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"vin": ["VIN must contain only A-Z and 0-9 characters"]},
        )

    return vinNorm

def get_vehicle_or_404(vin: str, db: Session):
    """
    Validate + normalize VIN, then retrieve the vehicle or return 404.
    """
    vinNorm = validateVin(vin)

    vehicle = (
        db.query(models.Vehicle)
        .filter(models.Vehicle.vin == vinNorm)
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with VIN {vinNorm} not found",
        )
    
    return vehicle

# ROUTES

@app.get("/")
def root():
    return {"message": "Hello, World!"}


@app.get("/vehicle/", response_model=list[VehicleRead])
def list_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).all()
    return vehicles


@app.post("/vehicle/", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle_in: VehicleCreate, db: Session = Depends(get_db)):
    vinNorm = validateVin(vehicle_in.vin)

    # no duplicate VIN
    existing = db.query(models.Vehicle).filter(models.Vehicle.vin == vinNorm).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
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

@app.get("/vehicle/{vin}", response_model=VehicleRead)
def get_vehicle(vin: str, db: Session = Depends(get_db)):
    return get_vehicle_or_404(vin, db)

@app.put("/vehicle/{vin}", response_model=VehicleRead)
def update_vehicle(vin: str, vehicle_in: VehicleUpdate, db: Session = Depends(get_db)):
    vehicle = get_vehicle_or_404(vin, db)

    # Body VIN must match URL VIN
    bodyVin = validateVin(vehicle_in.vin)
    urlVin = validateVin(vin)
    if bodyVin != urlVin:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"vin": ["VIN in body must match VIN in URL"]},
        )

    # update fields in db
    vehicle.manuName = vehicle_in.manuName
    vehicle.description = vehicle_in.description
    vehicle.horsePower = vehicle_in.horsePower
    vehicle.modelName = vehicle_in.modelName
    vehicle.modelYear = vehicle_in.modelYear
    vehicle.purchasePrice = vehicle_in.purchasePrice
    vehicle.fuelType = vehicle_in.fuelType

    db.commit()
    db.refresh(vehicle)

    return vehicle

@app.delete("/vehicle/{vin}", status_code = status.HTTP_204_NO_CONTENT)
def delete_vehicle(vin: str, db: Session = Depends(get_db)):
    vehicle = get_vehicle_or_404(vin, db)
    
    db.delete(vehicle)
    db.commit()

    return None