from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json
import os
import random

app = Flask(__name__)

# File to store collected SMS data
SMS_FILE = "sms_data.json"

# Ensure the data file exists
if not os.path.exists(SMS_FILE):
    with open(SMS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)

# List of 150 unique names
NAMES = [
    "John Doe", "Jane Smith", "Alice Johnson", "Bob Brown", "Charlie Davis", "Eve Wilson", "Frank Moore", "Grace Taylor",
    "Hank Anderson", "Ivy Thomas", "Jack White", "Karen Harris", "Leo Martin", "Mia Thompson", "Nina Garcia", "Oscar Martinez",
    "Paul Robinson", "Quinn Clark", "Rachel Rodriguez", "Steve Lewis", "Tina Lee", "Uma Walker", "Victor Hall", "Wendy Allen",
    "Xander Young", "Yara Hernandez", "Zack King", "Aaron Wright", "Bella Lopez", "Caleb Hill", "Daisy Scott", "Eli Green",
    "Fiona Adams", "Gabe Baker", "Hazel Gonzalez", "Ian Nelson", "Jade Carter", "Kai Mitchell", "Luna Perez", "Mason Roberts",
    "Nora Turner", "Owen Phillips", "Penny Campbell", "Quincy Parker", "Riley Evans", "Sofia Edwards", "Theo Collins",
    "Ursula Stewart", "Violet Sanchez", "Wyatt Morris", "Xena Rogers", "Yvonne Reed", "Zane Cook", "Ava Morgan", "Blake Bell",
    "Cora Murphy", "Dexter Bailey", "Eva Rivera", "Felix Cooper", "Gwen Richardson", "Hugo Cox", "Isla Howard", "Jake Ward",
    "Kira Torres", "Liam Peterson", "Maya Gray", "Nolan Ramirez", "Olive James", "Peyton Watson", "Quinn Brooks",
    "Rory Kelly", "Sadie Sanders", "Tobias Price", "Uma Bennett", "Vera Wood", "Wade Barnes", "Xyla Ross", "Yara Henderson",
    "Zeke Coleman", "Aria Jenkins", "Brett Perry", "Clara Powell", "Dante Long", "Eliza Patterson", "Finn Hughes",
    "Gia Flores", "Hank Washington", "Ivy Butler", "Jett Simmons", "Kara Foster", "Luca Gonzales", "Mila Bryant",
    "Nash Alexander", "Ophelia Russell", "Parker Griffin", "Quinn Diaz", "Remy Hayes", "Sienna Myers", "Tucker Ford",
    "Uma Chavez", "Violet Murray", "Wes Ortiz", "Xander Vargas", "Yara Simpson", "Zeke Crawford", "Avery Black",
    "Brielle Holmes", "Cruz Stone", "Dahlia Meyer", "Emmett Boyd", "Freya Mills", "Gunner Warren", "Harlow Fox",
    "Ira Rose", "Jax Lane", "Kira Rice", "Luca Moreno", "Maren Schmidt", "Nash Patel", "Olive Ferguson", "Peyton Nichols",
    "Quinn Herrera", "Rory Medina", "Sadie Ryan", "Tobias Fernandez", "Uma Weber", "Vera Castillo", "Wade Harvey",
    "Xyla Hoffman", "Yara Elliott", "Zeke Cunningham", "Aria Knight", "Brett Bradley", "Clara Carroll", "Dante Hudson",
    "Eliza Duncan", "Finn Armstrong", "Gia Berry", "Hank Andrews", "Ivy Johnston", "Jett Ray", "Kara Lane"
]

# Example SMS content for received messages
RECEIVED_CONTENT = [
    "Hey, I just wanted to check in and see how you're doing. It's been a while since we last talked.",
    "I was thinking about our project deadline. Do you think we can meet it? Let's discuss tomorrow.",
    "Remember that meeting we had last week? I think we should follow up on the action items.",
    "I saw this interesting article and thought you might find it useful. Here's the link: [link]",
    "Can you send me the report by EOD? I need to review it before the meeting tomorrow.",
    "I'm planning a trip next month. Do you have any recommendations for places to visit?",
    "I just finished reading that book you recommended. It was fantastic! Thanks for the suggestion.",
    "I'm having some issues with the new software. Can you help me troubleshoot it?",
    "Let's catch up this weekend. How about we grab a coffee on Saturday?",
    "I just got a notification that your package has been delivered. Did you receive it?"
]

# Example SMS content for sent messages (replies)
SENT_CONTENT = [
    "Hey! I'm doing well, thanks for checking in. How about you?",
    "Yes, I think we can meet the deadline. Let's discuss the details tomorrow.",
    "I agree. I'll send a follow-up email to the team today.",
    "Thanks for sharing! I'll check it out later.",
    "Sure, I'll send the report by EOD.",
    "How about visiting the mountains? I heard it's beautiful this time of year.",
    "I'm glad you liked it! Let me know if you want more recommendations.",
    "Sure, I can help. What issues are you facing?",
    "Sounds great! Let's meet at 10 AM on Saturday.",
    "Yes, I received it. Thanks for letting me know!"
]

def generate_sms_data():
    """
    Function to generate pre-defined SMS data with two-way conversations and save it to the file.
    """
    sms_data = []
    current_time = datetime.now()

    for _ in range(250):  # Generate 250 conversations (500 messages in total)
        # Randomly select a sender
        sender = random.choice(NAMES)

        # Generate a random datetime within the last 7 days for the first message
        first_message_time = current_time - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )

        # Create the first message (received)
        sms_data.append({
            "datetime": first_message_time.strftime("%Y-%m-%d %H:%M:%S"),
            "sender": sender,
            "type": "received",
            "content": random.choice(RECEIVED_CONTENT)
        })

        # Generate a reply (sent) within a few minutes to an hour
        reply_time = first_message_time + timedelta(
            minutes=random.randint(1, 60),
            seconds=random.randint(0, 59)
        )

        # Create the reply message (sent)
        sms_data.append({
            "datetime": reply_time.strftime("%Y-%m-%d %H:%M:%S"),
            "sender": "Me",  # The user is the sender of the reply
            "type": "sent",
            "content": random.choice(SENT_CONTENT)
        })

    # Save the generated data
    with open(SMS_FILE, "w", encoding="utf-8") as f:
        json.dump(sms_data, f, indent=4, ensure_ascii=False)

@app.route('/collect_sms', methods=['POST'])
def collect_sms():
    """
    Endpoint to collect SMS data.
    Expected JSON payload:
    {
        "datetime": "YYYY-MM-DD HH:MM:SS",
        "sender": "Sender Name",
        "type": "received" or "sent",
        "content": "SMS content"
    }
    """
    try:
        # Get JSON data from the request
        data = request.json

        # Validate required fields
        if not all(key in data for key in ["datetime", "sender", "type", "content"]):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        # Parse datetime
        try:
            datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid datetime format. Use 'YYYY-MM-DD HH:MM:SS'"}), 400

        # Load existing data
        with open(SMS_FILE, "r", encoding="utf-8") as f:
            sms_data = json.load(f)

        # Append new SMS data
        sms_data.append(data)

        # Save updated data
        with open(SMS_FILE, "w", encoding="utf-8") as f:
            json.dump(sms_data, f, indent=4, ensure_ascii=False)

        return jsonify({"status": "success", "message": "SMS data collected successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_sms_data', methods=['GET'])
def get_sms_data():
    """
    Endpoint to retrieve all collected SMS data.
    """
    try:
        with open(SMS_FILE, "r", encoding="utf-8") as f:
            sms_data = json.load(f)
        return jsonify({"status": "success", "data": sms_data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/analyze_sms', methods=['GET'])
def analyze_sms():
    """
    Endpoint to analyze SMS data and provide insights.
    """
    try:
        with open(SMS_FILE, "r", encoding="utf-8") as f:
            sms_data = json.load(f)

        # Get the current time
        current_time = datetime.now()

        # Dictionary to store the last SMS time for each sender
        last_sms_times = {}

        # Analyze SMS data
        for sms in sms_data:
            sender = sms["sender"]
            sms_time = datetime.strptime(sms["datetime"], "%Y-%m-%d %H:%M:%S")

            # Update the last SMS time for the sender
            if sender not in last_sms_times or sms_time > last_sms_times[sender]:
                last_sms_times[sender] = sms_time

        # Generate insights
        insights = []
        for sender, last_sms in last_sms_times.items():
            time_since_last_sms = current_time - last_sms
            if time_since_last_sms > timedelta(days=7):  # If no SMS in the last 7 days
                insights.append(f"{sender} hasn't texted in a while. Check on them!")

        return jsonify({"status": "success", "insights": insights}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Generate the SMS data once at the start
    generate_sms_data()

    # Run the Flask app
    app.run(debug=True)
