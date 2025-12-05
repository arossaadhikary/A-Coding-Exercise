from sqlalchemy import Column, Integer, String, Float
from database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    
    # uniquely identified VIN
    vin = Column(String(32), unique=True, index=True, nullable=False)

    manuName = Column(String, index = True)
    description = Column(String, index = True)
    horsePower = Column(Integer, index = True)
    modelName = Column(String, index = True)
    modelYear = Column(Integer, index = True)
    purchasePrice = Column(Float, index = True)
    fuelType = Column(String, index = True)