from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
import models, schemas, database
from services.twilio_service import send_sms_alert

router = APIRouter()

def check_and_trigger_alert(reading: models.SensorReading, patient: models.Patient, db: Session):
    """
    Checks if risk level is High, and if so, sends an SMS alert.
    """
    if reading.risk_level == "High":
        alert_msg = (f"🚨 EMERGENCY: High Asthma Risk detected for {patient.name}!\n"
                     f"📈 Vitals: SpO2 {reading.spo2}%, Resp {reading.respiration_rate}/min, HR {reading.heart_rate}bpm.\n"
                     f"⚠️ Please check the patient immediately.")
        
        # Log alert to database
        db_alert = models.Alert(patient_id=patient.id, message=alert_msg)
        db.add(db_alert)
        db.commit()
        
        # Trigger SMS
        if patient.phone_number:
            success = send_sms_alert(patient.phone_number, alert_msg)
            if not success:
                db_alert.status = "Failed"
                db.commit()
@router.post("/sensors/ingest", response_model=schemas.SensorReading)
def ingest_sensor_data(reading_in: schemas.SensorReadingCreate, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    """
    Endpoint for ESP32 devices to push live sensor telemetry.
    """
    print(f"DEBUG: Ingesting data for patient_id: {reading_in.patient_id}")
    # Verify patient exists
    patient = db.query(models.Patient).filter(models.Patient.id == reading_in.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    db_reading = models.SensorReading(**reading_in.dict())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    
    # Process alerts asynchronously to not block the ESP32
    background_tasks.add_task(check_and_trigger_alert, db_reading, patient, db)
    
    return db_reading

@router.get("/sensors/{patient_id}/latest", response_model=schemas.SensorReading)
def get_latest_reading(patient_id: int, db: Session = Depends(database.get_db)):
    reading = db.query(models.SensorReading).filter(models.SensorReading.patient_id == patient_id).order_by(models.SensorReading.timestamp.desc()).first()
    if not reading:
         raise HTTPException(status_code=404, detail="No readings found for this patient")
    return reading
