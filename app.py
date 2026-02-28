from flask import Flask, request, jsonify
from flask_cors import CORS
from db import conn, cur
from dotenv import load_dotenv
import os
from google import genai

# Load environment variables
load_dotenv()

# Initialize Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

app = Flask(__name__)
CORS(app)
@app.route("/chat", methods=["POST"])
def chat():
    print("DEBUG: Request received") # If you don't see this, the issue is your React URL
    
    data = request.json
    user_message = data.get("message", "")
    mood = data.get("mood", "")
    bot_reply = "I'm here for you 💙"

    # 1. Gemini API Call
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", # Removed 'models/' prefix - sometimes causes issues
            contents=f"Mood: {mood}. User says: {user_message}. Be empathetic."
        )
        if response.text:
            bot_reply = response.text
    except Exception as e:
        print(f"Gemini Error: {e}")

    # 2. Database Insert (Only if connection exists)
    if conn and cur:
        try:
            cur.execute(
                "INSERT INTO messages (user_id, sender_type, text) VALUES (%s, %s, %s)",
                ("057D", "user", user_message)
            )
            cur.execute(
                "INSERT INTO messages (user_id, sender_type, text) VALUES (%s, %s, %s)",
                ("057D", "bot", bot_reply)
            )
            conn.commit()
            print("DB Update Successful")
        except Exception as db_error:
            print(f"Database Error: {db_error}")
            conn.rollback()
    else:
        print("Skipping DB: No connection available.")

    return jsonify({"reply": bot_reply})
@app.route("/api/journal/complete", methods=["POST"])
def complete_journal():
    # We do NOT request the message text here for privacy.
    try:
        cur.execute(
            "INSERT INTO messages (user_id, sender_type, text) VALUES (%s, %s, %s)",
            ("057D", "system", "Burn Journal Session Completed")
        )
        conn.commit()
        return jsonify({"message": "Thought successfully released."}), 200
    except Exception as e:
        print(f"Error logging journal: {e}")
        return jsonify({"error": "Failed to log session"}), 500
if __name__ == "_main_":
    app.run(debug=True)