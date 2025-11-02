import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# متغيرات البيئة (من Railway)
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS  = os.getenv("SENDER_PASS")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Server is running"}), 200

@app.route("/send_email", methods=["POST"])
def send_email():
    data = request.get_json(silent=True) or {}
    to_email = data.get("to")
    subject  = data.get("subject", "تذكير بالدواء")
    message  = data.get("message", "")

    if not to_email:
        return jsonify({"ok": False, "error": "Email 'to' is required"}), 400
    if not SENDER_EMAIL or not SENDER_PASS:
        return jsonify({"ok": False, "error": "SENDER_EMAIL/PASS not set"}), 500

    try:
        # إعداد رسالة
        msg = MIMEText(message, _charset="utf-8")
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email

        # إرسال عبر Gmail SMTP (TLS)
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.sendmail(SENDER_EMAIL, [to_email], msg.as_string())

        return jsonify({"ok": True}), 200

    except Exception as e:
        # ارجع الخطأ للواجهة حتى نعرف شنو المشكلة
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/test", methods=["GET"])
def test():
    # اختبار سريع يرسل لنفس صاحب الطلب إذا مرر بريد بالـ query
    to_email = request.args.get("to", SENDER_EMAIL)
    if not to_email:
        return "Set ?to=email@example.com or SENDER_EMAIL", 400
    try:
        msg = MIMEText("اختبار من سيرفر التذكير", _charset="utf-8")
        msg["Subject"] = "Email Test"
        msg["From"] = SENDER_EMAIL or "unknown@example.com"
        msg["To"] = to_email

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.sendmail(SENDER_EMAIL, [to_email], msg.as_string())

        return "✅ Email test sent successfully", 200
    except Exception as e:
        return f"❌ Error: {e}", 500

if __name__ == "__main__":
    # IMPORTANT: Railway يعين PORT عبر متغير بيئة
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
