# Vehicle Service API - Apollo Engineering Exercise

Description: RESTful Vehicle Service API using **FastAPI**, **SQLite**, and **SQLAlchemy**. Full CRUD operations on vehicle records and includes complete input validation, VIN verification according to U.S. standards, and automated tests using **pytest**.

## Features
## Figma Thought Process
View the project’s design board here:  
[A — Coding Exercise (Figma Board)](https://www.figma.com/board/FLp0cZ9ryuLwTKnk2SH8FW/A---Coding-Exercise?node-id=0-1&p=f&t=z7hNYbwvEazsZ94B-0)

### CRUD Endpoints
- **POST /vehicle** - create a new vehicle 
- **GET /vehicle** – list all vehicles  
- **GET /vehicle/{vin}** – retrieve a vehicle by VIN  
- **PUT /vehicle/{vin}** – update a vehicle  
- **DELETE /vehicle/{vin}** – delete a vehicle  

## Why These Dependencies?
The dependencies listed in `requirements.txt` were chosen to support a clean, testable, and production-style FastAPI application:

- **fastapi** – Core framework used to build the Vehicle Service API. Handles routing, validation, serialization, and HTTP responses.
- **uvicorn** – ASGI server used to run the FastAPI application. Provides hot reload during development and efficient async request handling.
- **sqlalchemy** – ORM used for interacting with the SQLite database. Enables clean model definitions, queries, and session management.
- **pydantic** – Provides schema validation for request and response models. Ensures strict type enforcement and clear error messages.
- **pytest** – Testing framework used to validate all API endpoints, error handling, and VIN validation logic.

### VIN Validation (FMVSS 115)
VINs are validated according to U.S. federal standards:

- Must be **exactly 17 characters**
- Must contain only **A–Z** and **0–9**
- **Cannot** contain **I**, **O**, or **Q**
- Validated and **normalized to uppercase**
  
Invalid VIN → **422 Unprocessable Entity**

### Helper Utilities
- `normalizeVin()` — trims whitespace, uppercases input  
- `validateVin()` — enforces VIN rules  
- `get_vehicle_or_404()` — validates VIN + queries DB + raises 404 automatically  

### Pytest Overview
A complete pytest suite verifies:

- Successful creation  
- Duplicate VIN logic  
- VIN normalization  
- Listing of vehicles  
- Updating vehicles  
- Deleting vehicles  
- Invalid VIN inputs
  
## Manual Testing (Postman)
In addition to automated tests, all endpoints were manually tested using Postman to verify:

- Successful vehicle creation (201)
- Input validation errors (422)
- VIN normalization on POST/PUT
- Retrieval by VIN (200)
- Update flow with matching VINs (200)
- Proper deletion behavior (204)

Postman was used to confirm that responses matched expected schemas and error formats.

## Running the Application 
```
# 1. Create & activate virtual environment
bash
python -m venv venv

# For Windows
venv\Scripts\activate
# For macOS/Linux
source venv/bin/activate

# 2. Install dependencies 
pip install -r requirements.txt

# 3. Start server 
python -m uvicorn main:app --reload

# 4. API Avaliable at http://127.0.0.1:8000
```

## Example Vehicle JSON
Request Body (POST / PUT)
```
{
  "vin": "1HGCM82633A004352",
  "manuName": "Toyota",
  "description": "Reliable sedan",
  "horsePower": 150,
  "modelName": "Corolla",
  "modelYear": 2020,
  "purchasePrice": 20000,
  "fuelType": "Gasoline"
}
```

Successful Response (201 Created)
```
{
  "id": 1,
  "vin": "1HGCM82633A004352",
  "manuName": "Toyota",
  "description": "Reliable sedan",
  "horsePower": 150,
  "modelName": "Corolla",
  "modelYear": 2020,
  "purchasePrice": 20000,
  "fuelType": "Gasoline"
}
```
