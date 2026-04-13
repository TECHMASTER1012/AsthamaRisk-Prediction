from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load Environment Variables from .env file
load_dotenv()

from database import engine, Base
from routers import auth, sensor, dashboard

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Asthma Risk Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(sensor.router, prefix="/api", tags=["IoT Sensors"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])

@app.get("/")
def read_root():
    return {"message": "Asthma Risk API is running."}
