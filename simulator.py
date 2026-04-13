import time
import random
import requests
import argparse

# Usage: python simulator.py --patient 1 --server http://127.0.0.1:8000
# Defaults to patient ID 1

def simulate_esp32_sensor_data(patient_id, server_url):
    print(f"Starting ESP32 Simulation for Patient {patient_id} targeting {server_url}")
    
    # We will simulate cycles of normal, slightly worse, and asthma attacks
    cycle = 0
    while True:
        cycle += 1
        
        if cycle % 20 < 10:
            # Normal State (Low Risk)
            activity = random.uniform(1.0, 5.0)
            respiration = random.uniform(14.0, 18.0)
            temp = random.uniform(22.0, 24.0)
            humidity = random.uniform(40.0, 50.0)
            aqi = random.uniform(20.0, 40.0)
            heart_rate = random.uniform(65.0, 85.0)
            spo2 = random.uniform(97.0, 100.0)
            risk = "Low"
            
        elif cycle % 20 < 15:
            # Borderline (Moderate Risk)
            activity = random.uniform(5.0, 8.0)
            respiration = random.uniform(20.0, 25.0)
            temp = random.uniform(26.0, 30.0)
            humidity = random.uniform(55.0, 70.0)
            aqi = random.uniform(80.0, 120.0)
            heart_rate = random.uniform(90.0, 105.0)
            spo2 = random.uniform(94.0, 96.0)
            risk = "Moderate"
            
        else:
            # Trigger Asthma Attack (High Risk)
            activity = random.uniform(0.0, 2.0)
            respiration = random.uniform(30.0, 35.0) # Hyperventilating
            temp = random.uniform(32.0, 38.0)
            humidity = random.uniform(75.0, 90.0)
            aqi = random.uniform(160.0, 250.0)
            heart_rate = random.uniform(115.0, 140.0)
            spo2 = random.uniform(85.0, 91.0)
            risk = "High"
            
        # Simulate RespRaw (a simple sine wave + noise for demonstration)
        resp_raw = 512 + 200 * (0.5 * (1 + (time.time() % 4) / 4)) # Dummy fluctuating value
        resp_raw += random.uniform(-10, 10)

        payload = {
            "patient_id": patient_id,
            "activity": round(activity, 2),
            "respiration_rate": round(respiration, 2),
            "temperature": round(temp, 2),
            "humidity": round(humidity, 2),
            "aqi": round(aqi, 2),
            "heart_rate": round(heart_rate, 2),
            "spo2": round(spo2, 2),
            "resp_raw": round(resp_raw, 2),
            "risk_level": risk
        }
        
        try:
            resp = requests.post(f"{server_url}/api/sensors/ingest", json=payload)
            if resp.status_code == 200:
                print(f"[SUCCESS] Pushed Data: {risk} Risk to {server_url}/api/sensors/ingest")
            else:
                print(f"[FAIL] HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"[ERROR] Failed to push data: {str(e)}")
            
        time.sleep(3) # Push every 3 seconds for active simulation demonstration

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--patient", type=int, default=1, help="Patient ID to simulate")
    parser.add_argument("--server", type=str, default="http://127.0.0.1:8000", help="FastAPI Server URL")
    args = parser.parse_args()
    
    simulate_esp32_sensor_data(args.patient, args.server)
