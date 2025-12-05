from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    
    # uniquely identified VIN
    vin = Column(String(32), unique=True, index=True, nullable=False)

    manuName = Column(String, index = True)
    description = Column(String, index = True)
    horsePower = Column(Integer, index = True)
    modelName = Column(String, index = True)
    purchasePrice = Column(Float, index = True)
    fuelType = Column(String, index = True)