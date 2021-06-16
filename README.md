
## Introduction:

BooKie is a automated python script which lets you book vaccination slots and download appointment slips for the same.

## Features

1. Search for vaccination availability
2. Validate OTP manually or automatically 
3. Filter the search by 
   1. Pincode
   2. District
   3. District with pincodes (users can input the pincodes to be searched under a specific district)
3. Search for a week & search for single day
4. Search by vaccine preference
5. Search by fee type
6. Public API & Protected API search
7. Set refresh frequency between each search
8. Automatically sets dose2 due date for partially vaccinated
9. Auto-book option which selects random centre and slots for fast booking
10. Saves a json configuration file of all the user preferences 
11. Downloads appointment slip
12. Search without login(SWL): It searches for the slots according to the json config file without logging in and only on detecting a slot it will trigger a OTP       (auto-OTP) and books the slots(if auto-book option is enabled)
	

## Guide
### Pre-requisites
1. [Setup on Windows/Linux/MacOS](https://github.com/Nakul93/BooKie/wiki/Setup) (Required)
2. [KVDB Bucket](https://github.com/Nakul93/BooKie/wiki/KVDB) for automatic OTP validation
3. Phone Setup
	1. Android
	   1. [CoWIN OTP Retriever](https://github.com/Nakul93/BooKie/wiki/CoWIN-OTP-Retriever) (Recommended)
	   2. [IFTTT](https://github.com/bombardier-gif/covid-vaccine-booking/wiki/IFTTT)
	2. [iPhone](https://github.com/Nakul93/BooKie/wiki/Shortcuts-for-iOS)
	
### Usage

#### For Mac
` python3 src/covid-vaccine-slot-booking.py [--mobile <mobile_no>] [--token <token>] [--kvdb-bucket <kvdb_bucket_key] [--config <path_to_config] [--no-tty]`

#### For Windows
` python src/covid-vaccine-slot-booking.py [--mobile <mobile_no>] [--token <token>] [--kvdb-bucket <kvdb_bucket_key] [--config <path_to_config] [--no-tty]`

This very basic CLI based script can be used to automate covid vaccination slot booking on Co-WIN Platform.

*Note: All parameters are optional.*

Parameter | Description
------------ | -------------
--mobile | Registered mobile on CoWIN
--token | Token of the user
--kvdb-bucket | kvdb.io bucket key
--config | Path to store the configuration file
--no-tty | Do not ask any terminal inputs. Proceed with smart choices

Environment Variable | Description
------------ | -------------
KVDB_BUCKET | kvdb.io bucket key

### Pro-Tip
Always use single-day search option to avoid getting rate-limited
#### Protected API Search
Using this option would require user to login. So make sure the slot opening times are known (refer to Telegram alerts history). 
NOTE:Do not run this for hours or else your account might get blocked

#### Public API Search (used for SWL)
This option can be used when the slot opening times are random/unknown. Since this option doesn't require login it can be run for a long time



## Contents
  - [Before you start](#before-you-start)
  - [COVID-19 Vaccination Slot Booking Script](#covid-19-vaccination-slot-booking-script)
    - [Important](#important)
    - [Steps](#steps)
  - [Troubleshooting common problems](#troubleshooting-common-problems)


## Before you start
1. If you face any issues please refer to the [troubleshooting section](#troubleshooting-common-problems) at the end of this doc
2. If you are still facing errors and want to run this script on windows using exe, please see the section below [How to run on windows](#how-to-run-on-windows)
3. Instructions for iOS have also been added. See the [Setup Guide for iOS](#setup-guide-for-ios) for details. Please note that its not possible to automate the OTP auto read on iOS completely, however its possible to make it a 1 tap process, which is far better than seeing and entering the OTP manually.

## COVID-19 Vaccination Slot Booking Script

This very basic CLI based script can be used to automate covid vaccination slot booking on Co-WIN Platform. 

### Important: 
- POC project. **Use at your own risk**.
- Do NOT use unless all beneficiaries selected are supposed to get the same vaccine and dose. 
- No option to register new user or add beneficiaries. This can be used only after beneficiary has been added through the official app/site
- If you accidentally book a slot, don't worry. You can always login to the official portal and cancel that.
- API Details: https://apisetu.gov.in/public/marketplace/api/cowin/cowinapi-v2
- And finally, I know code quality probably isn't great. Suggestions are welcome.

## Steps:
1. Run script:
	```python src\covid-vaccine-slot-booking.py```
2. Select Beneficiaries. Read the important notes. You can select multiple beneficiaries by providing comma-separated index values such as ```1,2```:
	```
	Enter the registered mobile number: ██████████
	Requesting OTP with mobile number ██████████..  
	Enter OTP: 999999  
	Validating OTP..  
	Token Generated: █████████████████████████████████████████████████████████████  
	Fetching registered beneficiaries..  
	+-------+----------------------------+---------------------------+------------+  
	| idx   | beneficiary_reference_id   | name                      | vaccine    |  
	+=======+============================+===========================+============+  
	| 1     | ██████████████             | █████████████████████████ | COVISHIELD |  
	+-------+----------------------------+---------------------------+------------+  
	| 2     | ██████████████             | █████████████████         |            |  
	+-------+----------------------------+---------------------------+------------+  
	  
	################# IMPORTANT NOTES #################  
	# 1. While selecting beneficiaries, make sure that selected beneficiaries are all taking the same dose: either first OR second.  
	# Please do no try to club together booking for first dose for one beneficiary and second dose for another beneficiary.  
	#  
	# 2. While selecting beneficiaries, also make sure that beneficiaries selected for second dose are all taking the same vaccine: COVISHIELD OR COVAXIN.  
	# Please do no try to club together booking for beneficiary taking COVISHIELD with beneficiary taking COVAXIN.  
	###################################################  
	  
	Enter comma separated index numbers of beneficiaries to book for : 2
	```


3. Ensure correct beneficiaries are getting selected:
	```
	Selected beneficiaries:  
	+-------+----------------------------+-----------+  
	| idx   | beneficiary_reference_id   | vaccine   |  
	+=======+============================+===========+  
	| 1     | ██████████████             |           |  
	+-------+----------------------------+-----------+
	```

4. Select a state
	```
	+-------+-----------------------------+  
	| idx   | state                       |  
	+=======+=============================+  
	| 1     | Andaman and Nicobar Islands |  
	+-------+-----------------------------+  
	| 2     | Andhra Pradesh              |  
	+-------+-----------------------------+
	+-------+-----------------------------+
	+-------+-----------------------------+  
	| 35    | Uttar Pradesh               |  
	+-------+-----------------------------+  
	| 36    | Uttarakhand                 |  
	+-------+-----------------------------+  
	| 37    | West Bengal                 |  
	+-------+-----------------------------+
	```
	```
	Enter State index: 18
	```
5. Select districts you are interested in. Multiple districts can be selected by providing comma-separated index values
	```
	+-------+--------------------+  
	| idx   | district           |  
	+=======+====================+  
	| 1     | Alappuzha          |  
	+-------+--------------------+  
	| 2     | Ernakulam          |  
	+-------+--------------------+  
	| 3     | Idukki             |  
	+-------+--------------------+
	+-------+--------------------+
	+-------+--------------------+  
	| 13    | Thrissur           |  
	+-------+--------------------+  
	| 14    | Wayanad            |  
	+-------+--------------------+
	```
	```
	Enter comma separated index numbers of districts to monitor : 2,13
	```
6. Ensure correct districts are getting selected.
	```
	Selected districts:  
	+-------+---------------+-----------------+-----------------------+  
	| idx   | district_id   | district_name   | district_alert_freq   |  
	+=======+===============+=================+=======================+  
	| 1     | 307           | Ernakulam       | 660                   |  
	+-------+---------------+-----------------+-----------------------+  
	| 2     | 303           | Thrissur        | 3080                  |  
	+-------+---------------+-----------------+-----------------------+
	```
7. Enter the minimum number of slots to be available at the center:
	```
	Filter out centers with availability less than: 5
	```
8. Script will now start to monitor slots in these districts every 15 seconds. `Note`: It will ask you monitor frequency `ProTip`: Do not select less than 5 seconds it will bombard cowin server and will get your request blocked, create issues in OTP generation for your number. #85
	```
	===================================================================================  
	Centers available in Ernakulam from 01-05-2021 as of 2021-04-30 15:13:44: 0  
	Centers available in Thrissur from 01-05-2021 as of 2021-04-30 15:13:44: 0  
	No viable options. Waiting for next update in 15s.
	===================================================================================  
	Centers available in Ernakulam from 01-05-2021 as of 2021-04-30 15:13:59: 0  
	Centers available in Thrissur from 01-05-2021 as of 2021-04-30 15:13:59: 0  
	No viable options. Waiting for next update in 15s.
	```
9. If at any stage your token becomes invalid, the script will make a beep and prompt for ```y``` or ```n```. If you'd like to continue, provide ```y``` and proceed to allow using same mobile number
	```
	Token is INVALID.  
	Try for a new Token? (y/n): y
	Try for OTP with mobile number ███████████? (y/n) : y
	Enter OTP: 888888
	```
11. When a center with more than minimum number of slots is available, the script will make a beep sound - different frequency for different district. It will then display the available options as table:
	```
	===================================================================================  
	Centers available in Ernakulam from 01-05-2021 as of 2021-04-30 15:34:19: 1  
	Centers available in Thrissur from 01-05-2021 as of 2021-04-30 15:34:19: 0  
	+-------+----------------+------------+-------------+------------+------------------------------------------------------------------------------+  
	| idx   | name           | district   | available   | date       | slots                                                                        |  
	+=======+================+============+=============+============+==============================================================================+  
	| 1     | Ayyampilly PHC | Ernakulam  | 30          | 01-05-2021 | ['09:00AM-10:00AM', '10:00AM-11:00AM', '11:00AM-12:00PM', '12:00PM-02:00PM'] |  
	+-------+----------------+------------+-------------+------------+------------------------------------------------------------------------------+  
	---------->  Wait 10 seconds for updated options OR  
	---------->  Enter a choice e.g: 1.4 for (1st center 4th slot): 1.3
	```
12. Before the next update, you'll have 10 seconds to provide a choice in the format ```centerIndex.slotIndex``` eg: The input```1.4``` will select the vaccination center in second row and its fourth slot.
13. After successful slot booking, the appointment slip will be downloaded in your current working directory in the format `mobile_appointmentno`.

<br>

## Working Screenshots:

1. Generating OTP and Token...

![SS1](https://github.com/dhhruv/Vac-Cowin/blob/master/assets/ss1.png)

2.  Fetching Registered Beneficiaries...

![SS2](https://github.com/dhhruv/Vac-Cowin/blob/master/assets/ss2.png)

3.  Selecting Beneficiaries...

![SS3](https://github.com/dhhruv/Vac-Cowin/blob/master/assets/ss3.png)

4.  Additional Information to be entered for Slot Booking...

![SS4](https://github.com/dhhruv/Vac-Cowin/blob/master/assets/ss4.png)

5.  Auto-Booking Function...

![SS5](https://github.com/dhhruv/Vac-Cowin/blob/master/assets/ss5.png)

6.  Save Information as JSON File...

![SS6](https://github.com/dhhruv/Vac-Cowin/blob/master/assets/ss6.png)

7.  Displaying Available Vaccination Centers and Booking Slots (Auto-Booking ON)...

![SS7](https://github.com/dhhruv/Vac-Cowin/blob/master/assets/ss7.png)

8.  Successfully Booking a Slot **(If and only if you enter the Captcha correctly and in the mean time, all the slots are not booked)**

![SS8](https://github.com/dhhruv/Vac-Cowin/blob/master/assets/ss8.png)

<!-- CONTRIBUTING -->
## Contributing

Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



