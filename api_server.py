from flask import Flask, request
import subprocess
import re

app = Flask(__name__)

latest_otp = None


# Receive OTP from SMS forwarder
@app.route('/otp', methods=['POST'])
def receive_otp():
    global latest_otp

    data = request.json
    sms = data["message"]

    otp = re.search(r"\d{6}", sms).group()

    latest_otp = otp

    print("OTP received:", otp)

    return {"status": "ok"}


# Provide OTP to automation script
@app.route('/get_otp')
def get_otp():
    return {"otp": latest_otp}


# Trigger GreytHR automation
@app.route('/login')
def login():

    print("GreytHR automation triggered")

    process = subprocess.run(
        ["python", "greythr_login.py"],
        capture_output=True,
        text=True
    )

    return {
        "status": "completed",
        "logs": process.stdout
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)