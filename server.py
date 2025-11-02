# server.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
# اسمح مؤقتًا لكل المصادر أثناء التطوير
CORS(app)

# متغيرات البيئة
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS  = os.getenv("SENDER_PASS")  # Gmail App Password

@app.route("/", methods=["GET"])
def home():
    return {"status": "Server is running"}, 200

@app.route("/send_email", methods=["POST"])
def send_email():
    data = request.get_json(silent=True) or {}
    to_email = data.get("to")
    subject  = data.get("subject", "تذكير بالدواء")
    message  = data.get("message", "حان وقت الدواء")

    if not to_email:
        return jsonify({"ok": False, "error": "Email not provided"}), 400
    if not (SENDER_EMAIL and SENDER_PASS):
        return jsonify({"ok": False, "error": "Missing SENDER_EMAIL/SENDER_PASS env vars"}), 500

    try:
        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"]    = SENDER_EMAIL
        msg["To"]      = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASS)
            server.send_message(msg)

        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    # تشغيل محليًا
    app.run(host="0.0.0.0", port=5000, debug=True)
