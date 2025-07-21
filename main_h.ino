/*******************************************************************
 * MPU6050  +  MAX30100  +  ESP8266 HTTP Client
 * Reads sensor data, formats it as JSON, and POSTs it to a server
 *******************************************************************/

#include <Wire.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h> // For creating JSON objects
#include <MAX30100_PulseOximeter.h>

/* ---------- Wi-Fi & Server Configuration ---------- */
const char* ssid     = "yourssid";
const char* password = "yourpassword";

// !!! IMPORTANT: Replace with your computer's local IP address !!!
const char* server_ip = "yourcomputerip"; 
const int   server_port = 8000;
const char* api_path = "/api/data-stream"; 

/* ---------- MPU6050 ---------- */
#define MPU_ADDR 0x68
float ax_sm = 0, ay_sm = 0, az_sm = 0;
float gx_sm = 0, gy_sm = 0, gz_sm = 0;
const float alpha = 0.2;

/* ---------- MAX30100 ---------- */
#define REPORTING_PERIOD_MS 1000
PulseOximeter pox;
uint32_t tsLastReport = 0;
float lastHR  = 0;
float lastSpO2 = 0;

/* ---------- Setup ---------- */
void setup() {
  Serial.begin(115200);
  delay(100);

  /* Wi-Fi Connection */
  Serial.print("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print('.');
  }
  Serial.println("\nWiFi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Will send data to: http://");
  Serial.print(server_ip);
  Serial.print(":");
  Serial.print(server_port);
  Serial.println(api_path);

  /* I²C bus */
  Wire.begin(4, 5);

  /* MPU6050 wake-up */
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission();

  /* MAX30100 Initialization */
  Serial.println("Initializing MAX30100...");
  if (pox.begin()) {
    Serial.println("MAX30100 OK");
    pox.setIRLedCurrent(MAX30100_LED_CURR_7_6MA);
  } else {
    Serial.println("FAILED – check wiring!");
    while (1) delay(1000);
  }
}

/* ---------- Loop ---------- */
void loop() {
  /* ---- MPU6050 read ---- */
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)MPU_ADDR, (size_t)14, (bool)true);

  if (Wire.available() == 14) {
    int16_t ax = Wire.read() << 8 | Wire.read();
    int16_t ay = Wire.read() << 8 | Wire.read();
    int16_t az = Wire.read() << 8 | Wire.read();
    Wire.read(); Wire.read();
    int16_t gx = Wire.read() << 8 | Wire.read();
    int16_t gy = Wire.read() << 8 | Wire.read();
    int16_t gz = Wire.read() << 8 | Wire.read();

    ax_sm = alpha * (ax / 16384.0) + (1 - alpha) * ax_sm;
    ay_sm = alpha * (ay / 16384.0) + (1 - alpha) * ay_sm;
    az_sm = alpha * (az / 16384.0) + (1 - alpha) * az_sm;
    gx_sm = alpha * (gx / 131.0)   + (1 - alpha) * gx_sm;
    gy_sm = alpha * (gy / 131.0)   + (1 - alpha) * gy_sm;
    gz_sm = alpha * (gz / 131.0)   + (1 - alpha) * gz_sm;
  }

  /* ---- MAX30100 read ---- */
  pox.update();
  
  if (millis() - tsLastReport >= REPORTING_PERIOD_MS) {
    lastHR  = pox.getHeartRate();
    lastSpO2 = pox.getSpO2();
    tsLastReport = millis();

    StaticJsonDocument<256> jsonDoc;
    jsonDoc["acc_x"] = ax_sm;
    jsonDoc["acc_y"] = ay_sm;
    jsonDoc["acc_z"] = az_sm;
    jsonDoc["gyro_x"] = gx_sm;
    jsonDoc["gyro_y"] = gy_sm;
    jsonDoc["gyro_z"] = gz_sm;
    jsonDoc["heart_rate"] = lastHR;
    jsonDoc["spo2"] = lastSpO2;

    String jsonString;
    serializeJson(jsonDoc, jsonString);

    if (WiFi.status() == WL_CONNECTED) {
      WiFiClient client; // Create a WiFiClient object
      HTTPClient http;
      String serverPath = "http://" + String(server_ip) + ":" + String(server_port) + String(api_path);
      
      // Use the new begin() method with the WiFiClient
      if (http.begin(client, serverPath)) { 
        http.addHeader("Content-Type", "application/json");
        
        int httpResponseCode = http.POST(jsonString);
        
        Serial.print("Sending -> ");
        Serial.println(jsonString);
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);
        
        http.end();
      } else {
        Serial.println("HTTP connection failed");
      }
    } else {
      Serial.println("WiFi Disconnected");
    }
  }
}