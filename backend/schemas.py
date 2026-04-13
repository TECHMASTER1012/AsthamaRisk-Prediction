from pydantic import BaseModel, ConfigDict, Field, AliasChoices
from typing import List, Optional
from datetime import datetime

# --- Base Schemas ---

class PatientBase(BaseModel):
    name: str
    age: int
    phone_number: str

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patients: List[Patient] = []

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- IoT Sensor Schemas ---

class SensorReadingBase(BaseModel):
    respiration_rate: float = Field(..., validation_alias=AliasChoices('respiration_rate', 'respirationRate'))
    aqi: float
    heart_rate: float = Field(..., validation_alias=AliasChoices('heart_rate', 'heartRate'))
    spo2: float
    risk_level: str = Field(..., validation_alias=AliasChoices('risk_level', 'riskLevel'))
    activity: Optional[float] = Field(0.0, validation_alias=AliasChoices('activity', 'activity')) # Just in case
    temperature: Optional[float] = Field(0.0, validation_alias=AliasChoices('temperature', 'temp', 'temperature'))
    humidity: Optional[float] = Field(0.0, validation_alias=AliasChoices('humidity', 'humidity'))
    resp_raw: Optional[float] = Field(0.0, validation_alias=AliasChoices('resp_raw', 'respRaw', 'respraw', 'RespRaw', 'Respraw'))

    model_config = ConfigDict(populate_by_name=True)

class SensorReadingCreate(SensorReadingBase):
    patient_id: int = Field(..., validation_alias=AliasChoices('patient_id', 'patientId'))

class SensorReading(SensorReadingBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    patient_id: int
    timestamp: datetime

class Alert(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    timestamp: datetime
    message: str
    status: str
