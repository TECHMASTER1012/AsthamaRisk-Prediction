from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Patient, SensorReading, Base
import os

engine = create_engine("sqlite:///asthma_predict.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("--- Patients and Reading Counts ---")
patients = db.query(Patient).all()
for p in patients:
    count = db.query(SensorReading).filter(SensorReading.patient_id == p.id).count()
    print(f"ID: {p.id}, Name: {p.name}, Total Readings: {count}")
    if count > 0:
        latest = db.query(SensorReading).filter(SensorReading.patient_id == p.id).order_by(SensorReading.timestamp.desc()).first()
        print(f"  Latest Reading: {latest.timestamp} (SpO2: {latest.spo2})")

db.close()
