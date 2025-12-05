from pydantic import BaseModel, Field, constr, conint, confloat

class VehicleBase(BaseModel):
    vin: constr(strip_whitespace=True, min_length=1, max_length=32)
    
    manuName: constr(strip_whitespace=True, min_length=1)
    description: str | None = None
    horsePower: conint(ge=0)
    modelName: constr(strip_whitespace=True, min_length=1)
    modelYear: conint(ge=1886, le=2100)
    purchasePrice: confloat(ge=0)
    fuelType: constr(strip_whitespace=True, min_length=1)

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    pass

class VehicleRead(VehicleBase):
    id: int

    class Config:
        from_attribute = True
