import datetime
import os
import sys
import time
import re
from hashlib import sha256

import requests
from colorama import Fore, Style, init

from utils.ratelimit import handleRateLimited
from utils.urls import *

init(convert=True)

WARNING_BEEP_DURATION = (1000, 2000)
SMS_REGEX = r"(?<!\d)\d{6}(?!\d)"

try:
    import winsound

except ImportError:
    import os

    if sys.platform == "darwin":

        def beep(freq, duration):
            # brew install SoX --> install SOund eXchange universal sound sample translator on mac
            os.system(f"play -n synth {duration/1000} sin {freq} >/dev/null 2>&1")

    else:

        def beep(freq, duration):
            # apt-get install beep  --> install beep package on linux distros before running
            os.system("beep -f %s -l %s" % (freq, duration))


else:

    def beep(freq, duration):
        winsound.Beep(freq, duration)


def generateTokenOTP(mobile, request_header, kvdb_bucket):
    """
    This function generate OTP and returns a new token
    """
    storage_url = "https://kvdb.io/" + kvdb_bucket + "/" + mobile

    txnId = clear_bucket_and_send_OTP(storage_url, mobile, request_header)
    
    if txnId is None:
        return txnId

    time.sleep(10)
    t_end = time.time() + 60 * 3  # try to read OTP for atmost 3 minutes
    while time.time() < t_end:
        response = requests.get(storage_url)
        if response.status_code == 200:
            print("OTP SMS is:" + response.text)
            print("OTP SMS len is:" + str(len(response.text)))
            OTP = extract_from_regex(response.text, SMS_REGEX)
            if not OTP:
                time.sleep(5)
                continue
            break
        else:
            # Hope it won't 500 a little later
            print("error fetching OTP API:" + response.text)
            time.sleep(5)

    if not OTP:
        return None

    print("Parsed OTP:" + OTP)

    data = {"otp": sha256(str(OTP.strip()).encode("utf-8")).hexdigest(), "txnId": txnId}
    print(f"Validating OTP..")

    token = requests.post(
        url="https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp",
        json=data,
        headers=request_header,
    )
    if token.status_code == 200:
        token = token.json()["token"]
    else:
        print("Unable to Validate OTP")
        print(token.text)
        return None

    print(f"Token Generated: {token}")
    return token

def clear_bucket_and_send_OTP(storage_url, mobile, request_header):
    print("clearing OTP bucket: " + storage_url)
    response = requests.put(storage_url, data={})
    data = {
        "mobile": mobile,
        "secret": "U2FsdGVkX1+z/4Nr9nta+2DrVJSv7KS6VoQUSQ1ZXYDx/CJUkWxFYG6P3iM/VW+6jLQ9RDQVzp/RcZ8kbT41xw==",
    }
    print(f"Requesting OTP with mobile number {mobile}..")
    txnId = requests.post(
        url="https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP",
        json=data,
        headers=request_header,
    )

    if txnId.status_code == 200:
        txnId = txnId.json()["txnId"]
    else:
        print("Unable to Create OTP")
        print(txnId.text)
        if txnId.status_code == 403 or txnId.status_code == 429:
            handle_rate_limited()
        time.sleep(5)  # Saftey net against rate limit
        txnId = None

    return txnId
    
    
def extract_from_regex(text, pattern):
    """
    This function extracts all particular string with help of regex pattern from given text
    """
    matches = re.findall(pattern, text, re.MULTILINE)
    if len(matches) > 0:
        return matches[0]
    else:
        return None
        
def generate_token_OTP_manual(mobile, request_header):
    """
    This function generate OTP and returns a new token
    """

    if not mobile:
        print("Mobile number cannot be empty")
        os.system("pause")
        sys.exit()

    valid_token = False
    while not valid_token:
        try:
            data = {
                "mobile": mobile,
                "secret": "U2FsdGVkX1+z/4Nr9nta+2DrVJSv7KS6VoQUSQ1ZXYDx/CJUkWxFYG6P3iM/VW+6jLQ9RDQVzp/RcZ8kbT41xw==",
            }
            txnId = requests.post(url=OTP_PRO_URL, json=data, headers=request_header)

            if txnId.status_code == 200:
                print(
                    f"Successfully requested OTP for mobile number {mobile} at {datetime.datetime.today()}.."
                )
                txnId = txnId.json()["txnId"]

                OTP = input(
                    "Enter OTP (If this takes more than 2 minutes, press Enter to retry): "
                )
                if OTP:
                    data = {
                        "otp": sha256(str(OTP).encode("utf-8")).hexdigest(),
                        "txnId": txnId,
                    }
                    print(f"Validating OTP..")

                    token = requests.post(
                        url="https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp",
                        json=data,
                        headers=request_header,
                    )
                    if token.status_code == 200:
                        token = token.json()["token"]
                        print(f"Token Generated: {token}")
                        valid_token = True
                        return token

                    else:
                        print("Unable to Validate OTP")
                        print(f"Response: {token.text}")

                        retry = input(f"Retry with {mobile} ? (y/n Default y): ")
                        retry = retry if retry else "y"
                        if retry == "y":
                            pass
                        else:
                            sys.exit()

            else:
                print("Unable to Generate OTP")
                print(txnId.status_code, txnId.text)
                if txnId.status_code == 403 or txnId.status_code == 429:
                    handle_rate_limited()

                retry = input(f"Retry with {mobile} ? (y/n Default y): ")
                retry = retry if retry else "y"
                if retry == "y":
                    pass
                else:
                    sys.exit()

        except Exception as e:
            print(str(e))
