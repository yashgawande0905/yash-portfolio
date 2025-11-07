# app.py
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Load environment variables
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")


# ✅ Serve homepage
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


# ✅ API route for contact form (POST only)
@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()

    if not (name and email and message):
        return jsonify({"error": "Missing required fields"}), 400

    mail = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject=f"[Portfolio Contact] {subject or 'No subject'}",
        html_content=f"""
        <h2>New message from your Portfolio Website</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Message:</strong><br>{message.replace('\n', '<br>')}</p>
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(mail)

        if response.status_code in (200, 202):
            print(f"✅ Email sent successfully from {email}")
            return jsonify({"ok": True, "message": "Email sent successfully"})
        else:
            print(f"⚠️ SendGrid error {response.status_code}")
            return jsonify({"error": f"SendGrid error {response.status_code}"}), 500

    except Exception as e:
        print("❌ Exception:", e)
        return jsonify({"error": str(e)}), 500


# ✅ Serve static files (after API routes so they don't get overridden)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)


if __name__ == "__main__":
    print("🚀 Flask running at: http://127.0.0.1:5000")
    print("📦 SendGrid key loaded:", bool(SENDGRID_API_KEY))
    app.run(debug=True, port=5000)
