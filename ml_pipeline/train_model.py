import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
from tflite_converter import convert_to_tflite_c_array

# Set random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

def generate_synthetic_data(num_samples=5000):
    """
    Generates synthetic dataset simulating physiological and environmental
    sensors for asthma risk prediction.
    Features: activity, respiration_rate, temperature, humidity, aqi, heart_rate, spo2
    Output: risk_level (0: Low, 1: Moderate, 2: High)
    """
    print(f"Generating {num_samples} synthetic samples...")
    data = []
    
    for _ in range(num_samples):
        # 0: Low Risk (Normal healthy individual)
        # 1: Moderate Risk (Slightly compromised environment or vitals)
        # 2: High Risk (Asthma attack symptoms)
        risk_level = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
        
        if risk_level == 0:
            activity = np.random.uniform(0.5, 8.0) # Normal daily activity
            resp_rate = np.random.uniform(12.0, 20.0) # Normal breathing
            temp = np.random.uniform(20.0, 26.0) # Comfortable room temp
            humidity = np.random.uniform(30.0, 50.0) # Comfortable humidity
            aqi = np.random.uniform(10.0, 50.0) # Good air quality
            hr = np.random.uniform(60.0, 100.0) # Normal heart rate
            spo2 = np.random.uniform(95.0, 100.0) # Healthy SpO2
            
        elif risk_level == 1:
            activity = np.random.uniform(3.0, 9.0) # Moderate activity
            resp_rate = np.random.uniform(20.0, 25.0) # Slightly elevated
            temp = np.random.choice([np.random.uniform(10.0, 18.0), np.random.uniform(28.0, 35.0)]) # Cold or Hot
            humidity = np.random.choice([np.random.uniform(10.0, 25.0), np.random.uniform(60.0, 85.0)]) # Very dry or very humid
            aqi = np.random.uniform(51.0, 150.0) # Moderate to Unhealthy for Sensitive Groups
            hr = np.random.uniform(90.0, 115.0) # Elevated HR
            spo2 = np.random.uniform(92.0, 96.0) # Borderline SpO2
            
        else: # High Risk
            activity = np.random.uniform(0.0, 4.0) # Low activity (struggling)
            resp_rate = np.random.choice([np.random.uniform(25.0, 40.0), np.random.uniform(5.0, 10.0)]) # Hyperventilation or severe distress
            temp = np.random.uniform(5.0, 40.0) # Extreme temps can trigger
            humidity = np.random.uniform(5.0, 95.0) # Any humidity combo
            aqi = np.random.uniform(151.0, 500.0) # Unhealthy to Hazardous
            hr = np.random.uniform(110.0, 160.0) # Tachycardia
            spo2 = np.random.uniform(80.0, 92.0) # Hypoxia
            
        # Add some noise to realism
        data.append([
            activity + np.random.normal(0, 0.5),
            resp_rate + np.random.normal(0, 1.0),
            temp + np.random.normal(0, 1.0),
            humidity + np.random.normal(0, 2.0),
            aqi + np.random.normal(0, 5.0),
            hr + np.random.normal(0, 3.0),
            spo2 + np.random.normal(0, 1.0),
            risk_level
        ])

    columns = ['activity', 'respiration_rate', 'temperature', 'humidity', 'aqi', 'heart_rate', 'spo2', 'risk_level']
    df = pd.DataFrame(data, columns=columns)
    
    # Clip values to realistic bounds just in case noise pushed them out
    df['spo2'] = df['spo2'].clip(0, 100)
    df['humidity'] = df['humidity'].clip(0, 100)
    df['aqi'] = df['aqi'].clip(0, 500)
    df['activity'] = df['activity'].clip(0, 10)
    
    return df

def build_model(input_shape):
    """
    Builds a lightweight neural network suitable for TinyML / ESP32.
    """
    model = Sequential([
        Dense(16, activation='relu', input_shape=(input_shape,)),
        Dense(8, activation='relu'),
        Dense(3, activation='softmax') # 3 classes: Low, Moderate, High
    ])
    
    model.compile(optimizer='adam', 
                  loss='sparse_categorical_crossentropy', 
                  metrics=['accuracy'])
    return model

def main():
    df = generate_synthetic_data(10000)
    
    # Save dataset to CSV for reference
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/asthma_sensor_dataset.csv', index=False)
    print("Saved synthetic dataset to data/asthma_sensor_dataset.csv")
    
    X = df.drop('risk_level', axis=1).values
    y = df['risk_level'].values
    
    # Scale features
    # Since this will run on microcontrollers, we need to export the scaler constants as well
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Save scaler mean and variance for C++ implementation
    np.savetxt("data/scaler_mean.csv", scaler.mean_, delimiter=",")
    np.savetxt("data/scaler_scale.csv", scaler.scale_, delimiter=",")
    print(f"Scaler Means: {scaler.mean_}")
    print(f"Scaler Scales: {scaler.scale_}")
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    model = build_model(X_train.shape[1])
    
    print("\nTraining Model...")
    history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=1)
    
    loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nTest Accuracy: {accuracy*100:.2f}%")
    
    # Save standard Keras model
    model.save('data/asthma_model.keras')
    print("Saved Keras model to data/asthma_model.keras")
    
    # Convert to TFLite and C Array
    convert_to_tflite_c_array(model, X_train)

if __name__ == "__main__":
    main()
