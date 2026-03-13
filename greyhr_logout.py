import json
import time
import datetime
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = "https://healthfirsttech.greythr.com/"

# read credentials
with open("credentials.json") as f:
    creds = json.load(f)

USERNAME = creds["uname"]
PASSWORD = creds["pass"]


# -----------------------------------
# Function to fetch OTP from API
# -----------------------------------
def wait_for_otp():

    print("Waiting for OTP from API...")

    while True:

        try:
            r = requests.get("http://localhost:5000/get_otp")
            data = r.json()

            if data["otp"]:
                print("OTP received:", data["otp"])
                return data["otp"]

        except Exception as e:
            print("OTP API error:", e)

        time.sleep(2)


# -----------------------------------
# Start Browser
# -----------------------------------
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 40)

driver.get(URL)


# -----------------------------------
# Login Fields
# -----------------------------------
username = wait.until(EC.visibility_of_element_located((By.ID, "username")))
password = wait.until(EC.visibility_of_element_located((By.ID, "password")))

username.clear()
password.clear()

username.send_keys(USERNAME)
time.sleep(0.5)
password.send_keys(PASSWORD)

login_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
)

login_button.click()

print("Waiting for OTP page...")


# -----------------------------------
# OTP Screen
# -----------------------------------
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".otp-text-input")))

otp = wait_for_otp()

otp_inputs = driver.find_elements(By.CSS_SELECTOR, ".otp-text-input")

for i in range(min(len(otp), len(otp_inputs))):
    otp_inputs[i].send_keys(otp[i])

verify_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Verify')]"))
)

verify_button.click()

print("OTP submitted")


# -----------------------------------
# Wait for Dashboard
# -----------------------------------
wait.until(EC.url_contains("/v3/portal/ess/home"))

print("Dashboard loaded")


# -----------------------------------
# Read Dashboard Clock
# -----------------------------------
clock = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "gt-now"))
)

dashboard_time = clock.text.strip()

print("Dashboard time:", dashboard_time)

if not dashboard_time:
    print("Could not read dashboard time. Exiting for safety.")
    driver.quit()
    exit()


# -----------------------------------
# Parse Time
# -----------------------------------
current_time = datetime.datetime.strptime(
    dashboard_time, "%H : %M : %S"
).time()

logout_time = datetime.time(20, 0, 0)


if current_time < logout_time:
    print("Before 8 PM → exiting without logout")
    driver.quit()
    exit()


print("After 8 PM → logging out")


# -----------------------------------
# Logout
# -----------------------------------
signout_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign Out')]"))
)

signout_button.click()

print("Signed out successfully")

time.sleep(5)

driver.quit()

print("Browser closed")