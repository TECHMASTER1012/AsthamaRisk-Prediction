from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    patients = relationship("Patient", back_populates="owner")

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    phone_number = Column(String) # For SMS alerts
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="patients")
    readings = relationship("SensorReading", back_populates="patient")
    alerts = relationship("Alert", back_populates="patient")

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    activity = Column(Float)
    respiration_rate = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    aqi = Column(Float)
    heart_rate = Column(Float)
    spo2 = Column(Float)
    resp_raw = Column(Float)
    
    risk_level = Column(String) # Low, Moderate, High
    
    patient = relationship("Patient", back_populates="readings")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    message = Column(String)
    status = Column(String, default="Sent")
    
    patient = relationship("Patient", back_populates="alerts")
