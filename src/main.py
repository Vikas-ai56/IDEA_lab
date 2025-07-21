'''Check whether the data buffer should store the dict(feature_name and value) or only 
values as an array and convert it into a dataframe'''

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pickle
import numpy as np
import pandas as pd 
from pathlib import Path
from endpoint import StrokeData
import random

FEATURE_NAMES = ['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']
DATA_LOG_DIR = Path("E:/IDEA_LAB/data")
# Correctly define DATA_LOG_FILE as a Path object
DATA_LOG_FILE = DATA_LOG_DIR / "real_time_data.csv"



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


try:
    with open("model/tennis_stroke_classifier.pkl", "rb") as f:
        model = pickle.load(f)
    with open("model/scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
except FileNotFoundError:
    model = None
    scaler = None

# ======================================= NEW LOGIC STARTS HERE ===============================

# --- Global State for Logging ---
data_buffer = []
is_logging = False

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- Helper Functions ---
def save_buffer_to_csv():
    """Saves the content of the data_buffer to a CSV file."""
    global data_buffer
    if not data_buffer:
        print("Data buffer is empty. Nothing to save.")
        return
    df = pd.DataFrame(data_buffer)
    df.to_csv(DATA_LOG_FILE, mode='w', header=True, index=False)
    print(f"Saved {len(data_buffer)} records to {DATA_LOG_FILE}")
    data_buffer = []

# --- HTTP Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/start-logging")
async def start_logging():
    global is_logging, data_buffer
    
    # Clear the previous log file when starting a new session
    if DATA_LOG_FILE.exists():
        try:
            DATA_LOG_FILE.unlink()
            print(f"Cleared previous log file: {DATA_LOG_FILE}")
        except OSError as e:
            print(f"Error clearing log file: {e}")

    is_logging = True
    data_buffer = []
    print("Started data logging.")
    await manager.broadcast('{"status": "Logging Started"}')
    return {"message": "Logging started."}


@app.post("/api/stop-logging")
async def stop_logging():
    global is_logging
    is_logging = False
    save_buffer_to_csv()
    print("Stopped data logging.")
    await manager.broadcast('{"status": "Logging Stopped"}')
    return {"message": "Logging stopped and data saved."}


@app.post("/api/data-stream")
async def data_stream(data: StrokeData):
    """Receives data, predicts, broadcasts, and logs it if enabled."""
    if model is None or scaler is None:
        return JSONResponse(status_code=503, content={"error": "Model or scaler not loaded."})

    row = data.model_dump()
    bpm = random.randint(70,100)
    spo2 = random.randint(95,99)
    row['heart_rate'] = bpm
    row['spo2'] = spo2
    features_df = pd.DataFrame([row])[FEATURE_NAMES]

    features_scaled = scaler.transform(features_df)
    prediction = model.predict(features_scaled)[0]
    
    if is_logging:
        log_entry = {**row, "prediction": prediction}
        data_buffer.append(log_entry)
    
    import json
    payload = {"prediction": prediction, "data":row}
    await manager.broadcast(json.dumps(payload))

    return {"status": "success", "prediction": prediction}

@app.get("/api/analysis-data")
async def get_analysis_data():
    """Serves the logged data for the analysis page."""
    # Check if the file exists AND is not empty
    if not DATA_LOG_FILE.exists() or DATA_LOG_FILE.stat().st_size == 0:
        return []
    df = pd.read_csv(DATA_LOG_FILE)
    return JSONResponse(content=df.to_dict(orient='records'))

# --- WebSocket Endpoint ---
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")



if __name__ == "__main__":
    import uvicorn
    # This is the corrected line
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
# ======================================= NEW LOGIC ENDS HERE =================================

'''@app.get("/",response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict_stroke(data: StrokeData):
    if model is None or scaler is None:
        return {"error": "Model or scaler not loaded."}

    # Create DataFrame from Pydantic model
    features_df = pd.DataFrame(data.model_dump())
    
    # Scale features and predict
    features_scaled = scaler.transform(features_df)
    prediction = model.predict(features_scaled)
    
    return {"prediction": prediction[0]}


@app.get("/test-predict")
async def test_predict():
    """Test endpoint with sample data"""
    if model is None:
        return {"error": "Model not found. Please train the model first."}
    
    # Sample data from your dataset
    features = [-0.351,0.7,0.02,16.6,31.6,-108.0]
    
    features_df = pd.DataFrame([features], columns=FEATURE_NAMES)
    
    # Apply scaling if scaler is available
    if scaler is not None:
        features_scaled = scaler.transform(features_df)
        features_df_scaled = pd.DataFrame(features_scaled, columns=FEATURE_NAMES)
    else:
        features_df_scaled = features_df
    
    # Make prediction
    prediction = model.predict(features_df_scaled)
    return {
        "prediction": prediction[0],
        "sample_data": {
            "acc_x": features[0],
            "acc_y": features[1], 
            "acc_z": features[2],
            "gyro_x": features[3],
            "gyro_y": features[4],
            "gyro_z": features[5]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)'''

