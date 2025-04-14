
import requests
import json
import schedule
import time
import threading
from flask import Flask, request, jsonify

# Tago.io Configuration
device_token = '<DEVICE_TOKEN>'  # Replace with your Tago.io device token
url = "https://api.tago.io/data"  # Tago.io API URL for posting data

# Thresholds for conditions
VOC_THRESHOLD = 1000
CO2_EQ_THRESHOLD = 400
BATTERY_LOW_THRESHOLD = 3.5

# Global variable to store dynamic input data
ttn_data = {
    "latitude": None,
    "longitude": None,
    "VOC": None,
    "CO2_eq": None,
    "distance": None,
    "movement_detected": 0,
    "battery": None
}

# Flask web app initialization
app = Flask(__name__)

# Homepage route - displays current TTN data
@app.route('/')
def homepage():
    return "Homepage"

# API route to update TTN data dynamically via POST request
@app.route('/update_ttn_data', methods=['POST'])
def update_data():
    global ttn_data
    new_data = request.json
    if not isinstance(new_data, dict):
        return jsonify({"error": "Invalid data format, must be JSON"}), 400

    # Update the global ttn_data with new values
    ttn_data.update(new_data)
    print(f"TTN data updated: {ttn_data}")
    return jsonify({"message": "TTN data updated", "updated_data": ttn_data}), 200

# Function to handle incoming TTN webhook data
@app.route('/ttn_webhook', methods=['POST'])
def ttn_webhook():
    global ttn_data

    # Get the incoming TTN payload
    ttn_payload = request.json
    print("Received TTN Data:", json.dumps(ttn_payload, indent=2))
    
    # Extract relevant data from the TTN payload
    try:
        latitude = ttn_payload.get("uplink_message", {}).get("decoded_payload", {}).get("latitude")
        longitude = ttn_payload.get("uplink_message", {}).get("decoded_payload", {}).get("longitude")
        VOC = ttn_payload.get("uplink_message", {}).get("decoded_payload", {}).get("VOC")
        CO2_eq = ttn_payload.get("uplink_message", {}).get("decoded_payload", {}).get("CO2_eq")
        distance = ttn_payload.get("uplink_message", {}).get("decoded_payload", {}).get("distance")
        movement_detected = ttn_payload.get("uplink_message", {}).get("decoded_payload", {}).get("movement_detected")
        battery = ttn_payload.get("uplink_message", {}).get("decoded_payload", {}).get("battery")

        # Update global ttn_data
        ttn_data = {
            "latitude": latitude,
            "longitude": longitude,
            "VOC": VOC,
            "CO2_eq": CO2_eq,
            "distance": distance,
            "movement_detected": movement_detected,
            "battery": battery
        }

        
        return jsonify({"message": "TTN data received and processed"}), 200

    except Exception as e:
        print(f"Error processing TTN payload: {e}")
        return jsonify({"error": "Error processing TTN payload"}), 500

# Function to process TTN data and send to Tago.io
def process_ttn_data():
    global ttn_data
    if not ttn_data:
        print("No data available to process.")
        return

    latitude = ttn_data.get("latitude")
    longitude = ttn_data.get("longitude")
    VOC = ttn_data.get("VOC")
    CO2_eq = ttn_data.get("CO2_eq")
    distance = ttn_data.get("distance")
    movement_detected = ttn_data.get("movement_detected")
    battery = ttn_data.get("battery")

    if latitude is None or longitude is None:
        print("GPS location data is missing; no message will be sent.")
        return

    # Prepare data to send to Tago.io
    data_to_send = []

    # Add location data
    data_to_send.append({"variable": "latitude", "value": latitude, "unit": "°", "device": "673eeb0626eae70009103ba9"})
    data_to_send.append({"variable": "longitude", "value": longitude, "unit": "°", "device": "673eeb0626eae70009103ba9"})

    if VOC is not None:
        if VOC > VOC_THRESHOLD:
            print(f"Warning: VOC level is high ({VOC} ppb). Sending alert.")
        data_to_send.append({"variable": "VOC", "value": VOC, "unit": "ppb", "device": "673eeb0626eae70009103ba9"})

    if CO2_eq is not None:
        if CO2_eq > CO2_EQ_THRESHOLD:
            print(f"Warning: CO2_eq level is high ({CO2_eq} ppm). Sending alert.")
        data_to_send.append({"variable": "CO2_eq", "value": CO2_eq, "unit": "ppm", "device": "673eeb0626eae70009103ba9"})

    if battery is not None: 
        if battery < BATTERY_LOW_THRESHOLD:
            print(f"Warning: Battery is low ({battery} V). Sending alert.")
        data_to_send.append({"variable": "battery", "value": battery, "unit": "V", "device": "673eeb0626eae70009103ba9"})

    if movement_detected:
        print("Movement detected! Sending alert.")
        data_to_send.append({"variable": "movement_detected", "value": movement_detected, "unit": "", "device": "673eeb0626eae70009103ba9"})

    if distance is not None:
        data_to_send.append({"variable": "distance", "value": distance, "unit": "meters", "device": "673eeb0626eae70009103ba9"})

    if data_to_send:
        send_data_to_tago(data_to_send)
    else:
        print("No data met the conditions to send to Tago.io.")

# Function to send data to Tago.io
def send_data_to_tago(payload):
    headers = {'Content-Type': 'application/json', 'Device-Token': device_token}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
   

    print("Response Code:", response.status_code)
    print("Response Text:", response.text)

    if response.status_code == 202:
        print("Data successfully sent to Tago.io!")
    else:
        print(f"Failed to send data: {response.status_code} - {response.text}")

# Schedule the script to run every 2 minutes
def run_scheduled_job():
    print("\nRunning scheduled job...")
    process_ttn_data()

schedule.every(2).minutes.do(run_scheduled_job)

# Function to run the Flask API server in a separate thread
def run_api():
    app.run(host='0.0.0.0', port=9000)

# Start the Flask API server in a separate thread
threading.Thread(target=run_api, daemon=True).start()

# Main loop for the scheduler
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
