from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json
import os
import random
import threading
import time

app = Flask(__name__)

# File to store collected call log data
CALL_LOG_FILE = "call_log_data.json"

# Ensure the data file exists
if not os.path.exists(CALL_LOG_FILE):
    with open(CALL_LOG_FILE, "w") as f:
        json.dump([], f)

# List of dummy senders and call types
DUMMY_SENDERS = ["Sarah", "Tom", "David", "Emma", "John", "Alice"]
CALL_TYPES = ["incoming", "outgoing"]

def generate_dummy_call_log():
    """
    Function to generate dummy call log data and save it to the file.
    """
    while True:
        # Generate a random datetime within the last 7 days
        current_time = datetime.now()
        random_time = current_time - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )

        # Create a dummy call log entry
        call_log_entry = {
            "datetime": random_time.strftime("%Y-%m-%d %H:%M:%S"),
            "sender": random.choice(DUMMY_SENDERS),
            "log_type": random.choice(CALL_TYPES)
        }

        # Load existing data
        with open(CALL_LOG_FILE, "r") as f:
            call_log_data = json.load(f)

        # Append new call log data
        call_log_data.append(call_log_entry)

        # Save updated data
        with open(CALL_LOG_FILE, "w") as f:
            json.dump(call_log_data, f, indent=4)

        # Wait for a random interval before generating the next call log (e.g., 1 to 10 seconds)
        time.sleep(random.randint(1, 10))

@app.route('/collect_call_log', methods=['POST'])
def collect_call_log():
    """
    Endpoint to collect call log data.
    Expected JSON payload:
    {
        "datetime": "YYYY-MM-DD HH:MM:SS",
        "sender": "Sender Name",
        "log_type": "incoming/outgoing"
    }
    """
    try:
        # Get JSON data from the request
        data = request.json

        # Validate required fields
        if not all(key in data for key in ["datetime", "sender", "log_type"]):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        # Validate log_type
        if data["log_type"] not in ["incoming", "outgoing"]:
            return jsonify({"status": "error", "message": "Invalid log_type. Must be 'incoming' or 'outgoing'"}), 400

        # Parse datetime
        try:
            datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid datetime format. Use 'YYYY-MM-DD HH:MM:SS'"}), 400

        # Load existing data
        with open(CALL_LOG_FILE, "r") as f:
            call_log_data = json.load(f)

        # Append new call log data
        call_log_data.append(data)

        # Save updated data
        with open(CALL_LOG_FILE, "w") as f:
            json.dump(call_log_data, f, indent=4)

        return jsonify({"status": "success", "message": "Call log data collected successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_call_logs', methods=['GET'])
def get_call_logs():
    """
    Endpoint to retrieve all collected call log data.
    """
    try:
        with open(CALL_LOG_FILE, "r") as f:
            call_log_data = json.load(f)
        return jsonify({"status": "success", "data": call_log_data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/analyze_call_logs', methods=['GET'])
def analyze_call_logs():
    """
    Endpoint to analyze call logs and provide insights.
    """
    try:
        with open(CALL_LOG_FILE, "r") as f:
            call_log_data = json.load(f)

        # Get the current time
        current_time = datetime.now()

        # Dictionary to store the last call time for each sender
        last_call_times = {}

        # Analyze call logs
        for log in call_log_data:
            sender = log["sender"]
            log_time = datetime.strptime(log["datetime"], "%Y-%m-%d %H:%M:%S")

            # Update the last call time for the sender
            if sender not in last_call_times or log_time > last_call_times[sender]:
                last_call_times[sender] = log_time

        # Generate insights
        insights = []
        for sender, last_call in last_call_times.items():
            time_since_last_call = current_time - last_call
            if time_since_last_call > timedelta(days=7):  # If no call in the last 7 days
                insights.append(f"{sender} hasn't called in a while. Check on them!")

        return jsonify({"status": "success", "insights": insights}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Start the dummy data generation thread
    dummy_data_thread = threading.Thread(target=generate_dummy_call_log)
    dummy_data_thread.daemon = True  # Daemonize thread to stop it when the main program exits
    dummy_data_thread.start()

    # Run the Flask app
    app.run(debug=True)
