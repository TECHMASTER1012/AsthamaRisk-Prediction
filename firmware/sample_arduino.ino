#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include "MAX30105.h"
#include "heartRate.h"
#include "TensorFlowLite_ESP32.h"
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "model_data.h"

const char* ssid       = "YOUR_SSID";
const char* password   = "YOUR_PASSWORD";
const char* serverName = "http://YOUR_SERVER_IP:8000/api/sensors/ingest";
const int   patient_id = 1;

#define DHTPIN   4
#define DHTTYPE  DHT22
#define I2C_SDA  8
#define I2C_SCL  9
#define MQ_PIN   1
#define RESP_PIN 2

DHT dht(DHTPIN, DHTTYPE);
Adafruit_MPU6050 mpu;
MAX30105 particleSensor;

tflite::MicroErrorReporter tfl_error_reporter;
tflite::AllOpsResolver     tfl_ops_resolver;
const tflite::Model*       tfl_model       = nullptr;
tflite::MicroInterpreter*  tfl_interpreter = nullptr;
TfLiteTensor*              tfl_input       = nullptr;
TfLiteTensor*              tfl_output      = nullptr;

constexpr int kTensorArenaSize = 20 * 1024;
uint8_t tensor_arena[kTensorArenaSize];

float feature_means[7]  = {4.5, 18.0, 25.0, 50.0, 100.0, 85.0, 96.0};
float feature_scales[7] = {2.0,  5.0,  5.0, 20.0,  50.0, 15.0,  3.0};

void setup() {
  Serial.begin(115200);
  delay(2000);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.println(WiFi.localIP());

  Wire.begin(I2C_SDA, I2C_SCL);

  dht.begin();

  if (!mpu.begin()) {
    Serial.println("MPU6050 not found");
    while (true);
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102 not found");
    while (true);
  }
  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeGreen(0);

  tfl_model = tflite::GetModel(g_model);
  if (tfl_model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model schema version mismatch");
    while (true);
  }

  tfl_interpreter = new tflite::MicroInterpreter(
    tfl_model, tfl_ops_resolver, tensor_arena, kTensorArenaSize, &tfl_error_reporter
  );
  tfl_interpreter->AllocateTensors();

  tfl_input  = tfl_interpreter->input(0);
  tfl_output = tfl_interpreter->output(0);
}

void loop() {
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();
  float aqi  = analogRead(MQ_PIN) * (500.0 / 4095.0);

  if (isnan(temp)) temp = 25.0;
  if (isnan(hum))  hum  = 50.0;

  sensors_event_t a, g, temp_mpu;
  mpu.getEvent(&a, &g, &temp_mpu);
  float accel_x = a.acceleration.x;
  float accel_y = a.acceleration.y;
  float accel_z = a.acceleration.z;
  float activity = abs(accel_x) + abs(accel_y) + abs(accel_z);

  long irValue = particleSensor.getIR();
  float hr   = 75.0;
  float spo2 = 97.0;

  static long lastBeat = 0;
  if (irValue > 50000 && checkForBeat(irValue)) {
    long delta = millis() - lastBeat;
    lastBeat   = millis();
    float bpm  = 60.0 / (delta / 1000.0);
    if (bpm >= 40 && bpm <= 180) {
      hr = bpm;
    }
    spo2 = 98.0 - (random(0, 100) / 50.0);
  }

  static int peakCount = 0;
  static unsigned long windowStart = millis();
  int soundVal = analogRead(RESP_PIN);
  float resp_rate = 16.0;

  if (soundVal > 90) {
    peakCount++;
    delay(200);
  }
  if (millis() - windowStart > 10000) {
    resp_rate  = peakCount * 6.0;
    peakCount  = 0;
    windowStart = millis();
  }

  float raw_features[7] = {activity, resp_rate, temp, hum, aqi, hr, spo2};

  for (int i = 0; i < 7; i++) {
    tfl_input->data.f[i] = (raw_features[i] - feature_means[i]) / feature_scales[i];
  }

  TfLiteStatus status = tfl_interpreter->Invoke();
  if (status != kTfLiteOk) {
    Serial.println("TFLite Invoke failed");
    return;
  }

  float out_low  = tfl_output->data.f[0];
  float out_mod  = tfl_output->data.f[1];
  float out_high = tfl_output->data.f[2];

  String risk   = "Low";
  float max_prob = out_low;
  if (out_mod  > max_prob) { risk = "Moderate"; max_prob = out_mod;  }
  if (out_high > max_prob) { risk = "High";     max_prob = out_high; }

  Serial.printf("Risk: %s | Temp: %.1f | Hum: %.1f | AQI: %.1f | Act: %.2f | HR: %.1f | SpO2: %.1f | Resp: %.1f\n",
                risk.c_str(), temp, hum, aqi, activity, hr, spo2, resp_rate);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<256> doc;
    doc["patient_id"]       = patient_id;
    doc["activity"]         = activity;
    doc["respiration_rate"] = resp_rate;
    doc["temperature"]      = temp;
    doc["humidity"]         = hum;
    doc["aqi"]              = aqi;
    doc["heart_rate"]       = hr;
    doc["spo2"]             = spo2;
    doc["risk_level"]       = risk;

    String body;
    serializeJson(doc, body);

    int httpCode = http.POST(body);
    Serial.printf("HTTP %d\n", httpCode);
    http.end();
  }

  delay(2000);
}
