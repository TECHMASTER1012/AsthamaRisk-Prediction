from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import models, schemas, database
from routers.auth import get_current_user

router = APIRouter()

@router.post("/patients", response_model=schemas.Patient)
def create_patient(patient_in: schemas.PatientCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    db_patient = models.Patient(**patient_in.dict(), owner_id=current_user.id)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/patients", response_model=List[schemas.Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    patients = db.query(models.Patient).filter(models.Patient.owner_id == current_user.id).offset(skip).limit(limit).all()
    return patients

@router.get("/patients/{patient_id}/history", response_model=List[schemas.SensorReading])
def read_patient_history(patient_id: int, hours: int = 24, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id, models.Patient.owner_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or unassigned")
    
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    readings = db.query(models.SensorReading).filter(
        models.SensorReading.patient_id == patient_id,
        models.SensorReading.timestamp >= time_threshold
    ).order_by(models.SensorReading.timestamp.asc()).all()
    return readings

@router.get("/patients/{patient_id}/alerts", response_model=List[schemas.Alert])
def read_patient_alerts(patient_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id, models.Patient.owner_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or unassigned")
    
    alerts = db.query(models.Alert).filter(models.Alert.patient_id == patient_id).order_by(models.Alert.timestamp.desc()).all()
    return alerts
