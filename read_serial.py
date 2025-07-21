import serial
import json
import requests
import time

# --- Configuration ---
SERIAL_PORT = 'COM3'  # Change to your ESP8266's serial port
BAUD_RATE = 115200
API_ENDPOINT = 'http://127.0.0.1:8000/api/data-stream'

def read_and_stream_data():
    """
    Connects to the serial port, reads JSON data, and sends it to the FastAPI server.
    """
    while True:
        try:
            print(f"Attempting to connect to {SERIAL_PORT}...")
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
                print(f"Successfully connected to {SERIAL_PORT}.")
                ser.flushInput()
                
                while True:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8').strip()
                        if not line:
                            continue
                        
                        try:
                            data_dict = json.loads(line)
                            print(f"Received data: {data_dict}")
                            
                            # Send data to the FastAPI server
                            try:
                                response = requests.post(API_ENDPOINT, json=data_dict, timeout=1)
                                if response.status_code == 200:
                                    print(f"Data sent successfully. Prediction: {response.json().get('prediction')}")
                                else:
                                    print(f"Error sending data: {response.status_code} {response.text}")
                            except requests.exceptions.RequestException as e:
                                print(f"API connection error: {e}")

                        except json.JSONDecodeError:
                            print(f"Skipping malformed line: {line}")
                        except Exception as e:
                            print(f"An unexpected error occurred: {e}")

        except serial.SerialException as e:
            print(f"Serial connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("Stopping script.")
            break

if __name__ == "__main__":
    read_and_stream_data()