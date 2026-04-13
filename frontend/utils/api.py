import requests
import streamlit as st

BASE_URL = "http://localhost:8000"

def get_headers():
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def login(username, password):
    response = requests.post(f"{BASE_URL}/auth/token", data={"username": username, "password": password})
    if response.status_code == 200:
        st.session_state["token"] = response.json()["access_token"]
        st.session_state["username"] = username
        return True
    return False

def register(username, password):
    response = requests.post(f"{BASE_URL}/auth/register", json={"username": username, "password": password})
    return response.status_code == 200

def get_patients():
    headers = get_headers()
    response = requests.get(f"{BASE_URL}/api/patients", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def create_patient(name, age, phone_number):
    headers = get_headers()
    data = {"name": name, "age": age, "phone_number": phone_number}
    response = requests.post(f"{BASE_URL}/api/patients", json=data, headers=headers)
    return response.status_code == 200

def get_patient_history(patient_id, hours=1):
    headers = get_headers()
    response = requests.get(f"{BASE_URL}/api/patients/{patient_id}/history?hours={hours}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def get_patient_alerts(patient_id):
    headers = get_headers()
    response = requests.get(f"{BASE_URL}/api/patients/{patient_id}/alerts", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []
