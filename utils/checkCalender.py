import datetime
import os
import sys
import copy

import requests
from colorama import Fore, Style, init

from utils.displayData import viableOptions
from utils.ratelimit import handleRateLimited
from utils.urls import *

WARNING_BEEP_DURATION = (1000, 2000)

init(convert=True)

DATE_FORMATS = [
    "%d-%m-%y",
    "%-d-%m-%y",
    "%d-%-m-%y",
    "%-d-%-m-%y",
    "%d-%m-%Y",
    "%-d-%m-%Y",
    "%d-%-m-%Y",
    "%-d-%-m-%Y",
    "%d/%m/%y",
    "%-d/%m/%y",
    "%d/%-m/%y",
    "%-d/%-m/%y",
    "%d/%m/%Y",
    "%-d/%m/%Y",
    "%d/%-m/%Y",
    "%-d/%-m/%Y",
]

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


def rotate_date_format(start_date):
    global rotation_counter
    date = datetime.datetime.strptime(start_date, "%d-%m-%Y")
    strftime = date.strftime(DATE_FORMATS[rotation_counter])
    rotation_counter += 1
    if rotation_counter >= len(DATE_FORMATS):
        rotation_counter = 0
    return strftime

def correct_schema(sessions):
    centers = {}
    if "sessions" in sessions and len(sessions["sessions"]) > 0:
        for session in sessions["sessions"]:
            center_id = session["center_id"]
            if center_id not in centers:
                centers[center_id] = copy.deepcopy(session)
                del centers[center_id]["session_id"]
                del centers[center_id]["date"]
                del centers[center_id]["available_capacity"]
                del centers[center_id]["available_capacity_dose1"]
                del centers[center_id]["available_capacity_dose2"]
                del centers[center_id]["min_age_limit"]
                del centers[center_id]["vaccine"]
                del centers[center_id]["slots"]
                centers[center_id]["sessions"] = []
            centers[center_id]["sessions"].append(
                {
                    "session_id": session["session_id"],
                    "date": session["date"],
                    "available_capacity": session["available_capacity"],
                    "available_capacity_dose1": session["available_capacity_dose1"],
                    "available_capacity_dose2": session["available_capacity_dose2"],
                    "min_age_limit": session["min_age_limit"],
                    "vaccine": session["vaccine"],
                    "slots": session["slots"],
                }
            )
    return {"centers": list(centers.values())}

def checkCalenderByDistrict(
    api_type,
    find_option,
    base_request_header,
    token_service,
    vaccine_type,
    location_dtls,
    start_date,
    minimum_slots,
    min_age_booking,
    fee_type,
    dose,
):
    """
    This function
        1. Takes details required to check vaccination calendar
        2. Filters result by minimum number of slots available
        3. Returns False if token is invalid
        4. Returns list of vaccination centers & slots if available
    """
    try:
        print(f"{Fore.RESET}", end="")
        print(
            "==================================================================================="
        )
        today = datetime.datetime.today()
        if api_type == "public" and find_option == 1:
            base_url = CALENDAR_URL_DISTRICT_PUB
        elif api_type == "public" and find_option == 2:
            base_url = FIND_URL_DISTRICT_PUB
        elif api_type == "protected" and find_option == 1:
            base_url = CALENDAR_URL_DISTRICT_PRO
        else:
            base_url = FIND_URL_DISTRICT_PRO

        request_header = copy.deepcopy(base_request_header)
        if api_type == "protected":
            token = token_service.get_token()
            request_header["Authorization"] = f"Bearer {token}"
            if vaccine_type:
                base_url += f"&vaccine={vaccine_type}"

        options = []

        for location in location_dtls:
            resp = requests.get(
                base_url.format(location["district_id"], rotate_date_format(start_date) if find_option == 1 else start_date),
                headers=request_header,
            )

            if resp.status_code == 403 or resp.status_code == 429:
                handleRateLimited()
                return False

            elif resp.status_code == 401:
                print(f"{Fore.RED}", end="")
                print("TOKEN is INVALID!")
                print(f"{Fore.RESET}", end="")
                return False

            elif resp.status_code == 200:
                resp = resp.json()
            
                if find_option == 2:
                    resp = correct_schema(resp)

                resp = filterCenterbyAge(
                    resp, min_age_booking
                )  # Filters the centers by age

                if "centers" in resp:
                    print(f"{Fore.YELLOW}", end="")
                    print(
                        f"Centres available in {location['district_name']} from {start_date} as of {today.strftime('%Y-%m-%d %H:%M:%S')}: {len(resp['centers'])}"
                    )
                    print(f"{Fore.RESET}", end="")
                    options += viableOptions(
                        resp, minimum_slots, min_age_booking, fee_type, dose
                    )

            else:
                pass

        for location in location_dtls:
            if location["district_name"] in [option["district"] for option in options]:
                for _ in range(2):
                    beep(location["alert_freq"], 150)
        return options

    except Exception as e:
        print(f"{Fore.RED}", end="")
        print(str(e))
        print(f"{Fore.RESET}", end="")
        beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])


def checkCalenderByPincode(
    api_type,
    find_option,
    base_request_header,
    token_service,
    vaccine_type,
    location_dtls,
    start_date,
    minimum_slots,
    min_age_booking,
    fee_type,
    dose,
):
    """
    This function
        1. Takes details required to check vaccination calendar
        2. Filters result by minimum number of slots available
        3. Returns False if token is invalid
        4. Returns list of vaccination centers & slots if available
    """
    try:
        print(f"{Fore.RESET}", end="")
        print(
            "==================================================================================="
        )
        today = datetime.datetime.today()
        if api_type == "public" and find_option == 1:
            base_url = CALENDAR_URL_PINCODE_PUB
        elif api_type == "public" and find_option == 2:
            base_url = FIND_URL_PINCODE_PUB
        elif api_type == "protected" and find_option == 1:
            base_url = CALENDAR_URL_PINCODE_PRO
        else:
            base_url = FIND_URL_DISTRICT_PRO

        request_header = copy.deepcopy(base_request_header)
        if api_type == "protected":
            token = token_service.get_token()
            request_header["Authorization"] = f"Bearer {token}"
            if vaccine_type:
                base_url += f"&vaccine={vaccine_type}"

        options = []

        for location in location_dtls:
            resp = requests.get(
                base_url.format(location["pincode"], rotate_date_format(start_date) if find_option == 1 else start_date), headers=request_header
            )

            if resp.status_code == 403 or resp.status_code == 429:
                handleRateLimited()
                return False

            elif resp.status_code == 401:
                print(f"{Fore.RED}", end="")
                print("TOKEN is INVALID!")
                print(f"{Fore.RESET}", end="")
                return False

            elif resp.status_code == 200:
                resp = resp.json()
                if find_option == 2:
                    resp = correct_schema(resp)

                resp = filterCenterbyAge(
                    resp, min_age_booking
                )  # Filters the centers by age

                if "centers" in resp:
                    print(f"{Fore.YELLOW}", end="")
                    print(
                        f"Centres available in {location['pincode']} from {start_date} as of {today.strftime('%Y-%m-%d %H:%M:%S')}: {len(resp['centers'])}"
                    )
                    print(f"{Fore.RESET}", end="")
                    options += viableOptions(
                        resp, minimum_slots, min_age_booking, fee_type, dose
                    )

            else:
                pass

        for location in location_dtls:
            if int(location["pincode"]) in [option["pincode"] for option in options]:
                for _ in range(2):
                    beep(location["alert_freq"], 150)

        return options

    except Exception as e:
        print(f"{Fore.RED}", end="")
        print(str(e))
        print(f"{Fore.RESET}", end="")
        beep(WARNING_BEEP_DURATION[0], WARNING_BEEP_DURATION[1])


def filterCenterbyAge(resp, min_age_booking):
    if min_age_booking >= 45:
        center_age_filter = 45
    else:
        center_age_filter = 18

    if "centers" in resp:
        for center in list(resp["centers"]):
            for session in list(center["sessions"]):
                if session["min_age_limit"] != center_age_filter:
                    center["sessions"].remove(session)
                    if len(center["sessions"]) == 0:
                        resp["centers"].remove(center)

    return resp
