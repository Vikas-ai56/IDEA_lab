# Tennis Swing Analysis System

This is a real-time sports analytics platform developed for the **IDEA LAB SEE**. It leverages a wearable sensor device to capture accelerometer, gyroscope, heart rate, and SpO2 data, which is then processed by a sophisticated machine learning model to classify tennis strokes instantly.

The core of our prediction engine is a **Stacking Classifier**, an advanced ensemble method that combines the strengths of several different models (K-Nearest Neighbors, Logistic Regression, Random Forest, and SVC) to achieve higher accuracy and robustness.

## Hardware Components

The wearable device is built using the following components:
- **ESP8266:** A low-cost Wi-Fi microchip with a full TCP/IP stack and microcontroller capability.
- **MPU6050:** A 6-axis motion tracking device that combines a 3-axis gyroscope and a 3-axis accelerometer.
- **MAX30100:** An integrated pulse oximetry and heart-rate monitor sensor.

## Technology Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Machine Learning:** Scikit-learn, Pandas, NumPy
- **Hardware Programming:** C++ (Arduino)

## Project Structure

```
.
├── data/
│   ├── complete_data.csv     # Full dataset for training
│   ├── real_time_data.csv    # Logged data from live sessions
│   └── test_data.csv         # Test dataset generated from training script
│
├── read_serial.py            # (Legacy) Script to read data from serial port
├── README.md                 # This file
│
└── src/
    ├── endpoint.py           # Pydantic data models
    ├── logic.py              # Script to train the ML model and scaler
    ├── main.py               # Main FastAPI application server
    ├── request.py            # Test script for sending sample requests
    │
    ├── model/
    │   ├── scaler.pkl
    │   └── tennis_stroke_classifier.pkl
    │
    ├── static/
    │   ├── css/style.css
    │   └── js/script.js
    │
    └── templates/
        └── index.html
```

## How to Run

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Vikas-ai56/IDEA_lab.git -b master
    cd <repository-folder>
    ```

2.  **Install Python Dependencies:**
    Create a `requirements.txt` file with the following content and run `pip install -r requirements.txt`:
    ```
    fastapi
    uvicorn[standard]
    pandas
    numpy
    scikit-learn
    requests
    ```

3.  **Set up Hardware:**
    - Open the Arduino sketch for the ESP8266.
    - Install the required libraries: `MAX30100lib`, `ArduinoJson`, `ESP8266HTTPClient`.
    - Update the sketch with your Wi-Fi credentials and your computer's local IP address.
    - Upload the sketch to the ESP8266.

4.  **Run the Server:**
    Navigate to the `src` directory and run the FastAPI server.
    ```bash
    cd src
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    *Note: On Windows, you may need to create a firewall rule to allow incoming connections on port 8000.*

5.  **Start the System:**
    - Power on the ESP8266 device.
    - Open a web browser and navigate to `http://localhost:8000`.

## Project Team

This project was proudly developed by:
- Dev Sisodia (1RV24CS071)
- K Vikas (1RV24CS116)
- Kartik Satish Chandra (1RV24CS123)
- Kavin Krishnan C (1RV24CS126)