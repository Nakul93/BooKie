import re
import sys
import threading
from datetime import datetime
import time
from threading import Thread

import jwt
import requests
from hashlib import sha256

VALIDATE_MOBILE_OTP = "https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp"

OTP_PUBLIC_URL = "https://cdn-api.co-vin.in/api/v2/auth/public/generateOTP"
OTP_PRO_URL = "https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP"

SMS_REGEX = r"(?<!\d)\d{6}(?!\d)"


class TokenException(Exception):
    """Base class for exceptions in this module."""
    pass


class TokenService:

    def __init__(self, mobile: str, base_request_headers: dict):
        self.token = None
        self.token_expires = 0
        self.token_issued_at = 0
        self.mobile = mobile
        self.base_request_headers = base_request_headers
        self._lock = threading.Lock()
        if not mobile:
            raise Exception("Mobile number cannot be empty")

    def get_token(self):
        pass

    def set_token(self, token):
        with self._lock:
            payload = jwt.decode(token, options={"verify_signature": False})
            self.token_expires = payload["exp"]
            self.token_issued_at = payload["iat"]
            self.token = token

    def collect_inputs(self, **kwargs):
        pass

    def is_token_valid(self) -> bool:
        with self._lock:
            is_token_valid = self._is_token_valid()
            if not is_token_valid:
                self.token_issued_at = 0
                self.token_expires = 0
                self.token = None
            return is_token_valid

    def validate_otp(self, txn_id, otp) -> str:
        try:
            data = {
                "otp": sha256(str(otp).encode("utf-8")).hexdigest(),
                "txnId": txn_id,
            }
            print(f"Validating OTP..")

            token = requests.post(
                url=VALIDATE_MOBILE_OTP,
                json=data,
                headers=self.base_request_headers,
            )
            if token.status_code == 200:
                self.set_token(token.json()["token"])
                print(f"Token Generated: {self.token}")
                return self.token
            else:
                print(f"Response: {token.text}")
                if token.status_code == 403 or token.status_code == 429:
                    # TODO: Handle
                    # handle_rate_limited()
                    pass
                raise TokenException('Unable to Validate OTP')
        except Exception as e:
            print(str(e))
            raise TokenException(e)

    def initiate_otp(self) -> str:
        try:
            data = {
                "mobile": self.mobile,
                "secret": "U2FsdGVkX1+z/4Nr9nta+2DrVJSv7KS6VoQUSQ1ZXYDx/CJUkWxFYG6P3iM/VW+6jLQ9RDQVzp/RcZ8kbT41xw==",
            }
            txn_id_req = requests.post(url=OTP_PRO_URL, json=data, headers=self.base_request_headers)

            if txn_id_req.status_code == 200:
                print(
                    f"Successfully requested OTP for mobile number {self.mobile} at {datetime.today()}.."
                )
                return txn_id_req.json()["txnId"]
            else:
                print(txn_id_req.status_code, txn_id_req.text)
                if txn_id_req.status_code == 403 or txn_id_req.status_code == 429:
                    # TODO: Handle
                    # handle_rate_limited()
                    pass
                raise TokenException('Unable to Generate OTP')
        except Exception as e:
            print(str(e))
            raise TokenException(e)

    def _is_token_valid(self) -> bool:
        pass


class ManualTokenService(TokenService):

    def _is_token_valid(self) -> bool:
        remaining_seconds = self.token_expires - int(time.time())
        if remaining_seconds <= 1 * 30:  # 30 secs early before expiry for clock issues
            return False
        if remaining_seconds <= 60:
            print("Token is about to expire in next 1 min ...")
        return True

    def get_token(self):
        valid_token = self.is_token_valid()
        while not valid_token:
            try:
                txn_id = self.initiate_otp()
                otp = input(
                    "Enter OTP (If this takes more than 2 minutes, press Enter to retry): "
                )
                if otp:
                    return self.validate_otp(txn_id, otp)
            except TokenException as e:
                print(str(e))
                retry = input(f"Retry with {self.mobile} ? (y/n Default y): ")
                retry = retry if retry else "y"
                if retry == "y":
                    pass
                else:
                    sys.exit()
        return self.token


class JustInTimeAutoTokenService(TokenService):

    def __init__(self, mobile: str, base_request_headers: dict):
        super().__init__(mobile, base_request_headers)
        self.stopped = False
        self.kvdb_bucket = None
        self.storage_url = None
        self.token = None

    def collect_inputs(self, **kwargs):
        self.kvdb_bucket = kwargs['kvdb_bucket']
        if not self.kvdb_bucket:
            self.kvdb_bucket = input(
                "Please refer KVDB setup in ReadMe to setup your own KVDB bucket. "
                "Please enter your KVDB bucket value here: "
            )
        if not self.kvdb_bucket:
            print(
                "Sorry, having your private KVDB bucket is mandatory. "
                "Please refer ReadMe and create your own private KVBD bucket."
            )
            sys.exit()
        else:
            self.storage_url = "https://kvdb.io/" + self.kvdb_bucket + "/" + self.mobile
            print(
                "\n### Note ### Please make sure the URL configured in the IFTTT/Shortcuts app on your phone is: "
                + self.storage_url
                + "\n"
            )

    def _clear_bucket(self):
        print("clearing OTP bucket: " + self.storage_url)
        requests.put(self.storage_url, data={})

    def _is_token_valid(self) -> bool:
        remaining_seconds = self.token_expires - int(time.time())
        if remaining_seconds <= 5:
            return False
        if remaining_seconds <= 60:
            print("Token is about to expire in next 1 min ...")
        return True

    def get_token(self):
        if self.is_token_valid():
            return self.token
        else:
            return self._get_token()

    def _get_token(self) -> None:
        valid_token = False
        while not valid_token:
            try:
                self._clear_bucket()
                txn_id = self.initiate_otp()
                otp = self._get_otp()
                if otp:
                    token = self.validate_otp(txn_id, otp)
                    if token:
                        valid_token = True
                        return token
            except TokenException as e:
                print(str(e))
                print("OTP Retrying in 5 seconds")
                time.sleep(5)

    def _get_otp(self) -> str:
        time.sleep(10)
        t_end = time.time() + 60 * 3  # try to read OTP for atmost 3 minutes
        while time.time() < t_end:
            response = requests.get(self.storage_url)
            if response.status_code == 200:
                print("OTP SMS is:" + response.text)
                print("OTP SMS len is:" + str(len(response.text)))
                otp = extract_from_regex(response.text, SMS_REGEX)
                if not otp:
                    time.sleep(5)
                    continue
                return otp
            else:
                # Hope it won't 500 a little later
                print("error fetching OTP API:" + response.text)
                time.sleep(5)


class AutoTokenService(JustInTimeAutoTokenService, Thread):
    def __init__(self, mobile: str, base_request_headers: dict):
        super().__init__(mobile, base_request_headers)
        Thread.__init__(self)

    def get_token(self):
        if not self.is_alive():
            self.start()
        self.is_token_valid()
        while self.token is None:
            time.sleep(1)
        return self.token

    def run(self) -> None:
        while True:
            for i in range(0, int((self.token_expires - int(time.time()) - 120) / 10)):
                if not self.stopped:
                    time.sleep(10)
                else:
                    return
            valid_token = False
            while not valid_token:
                try:
                    self._clear_bucket()
                    txn_id = self.initiate_otp()
                    otp = self._get_otp()
                    if otp:
                        remaining_time = self.token_expires - int(time.time())
                        if remaining_time >= 3:
                            wait_time = remaining_time - 2
                            print(f'OTP has been received, waiting {wait_time} seconds...')
                            time.sleep(wait_time)
                        token = self.validate_otp(txn_id, otp)
                        if token:
                            valid_token = True
                except TokenException as e:
                    print(str(e))
                    print("OTP Retrying in 5 seconds")
                    time.sleep(5)


def extract_from_regex(text, pattern):
    """
    This function extracts all particular string with help of regex pattern from given text
    """
    matches = re.findall(pattern, text, re.MULTILINE)
    if len(matches) > 0:
        return matches[0]
    else:
        return None
