import requests

# 🔑 Hardcoded token (from your Render environment / portal)
TOKEN = "a0JhdSstSkhFZHA2NXliaWJVTGh4SUpWNkJpbkNDWmtiZlVvR2JMTmR0TzFDdVFhMk9tcVpTdWIxeG1FT1ZkQkJpdE5BZ2dzTzhHd3d1NFRwTElOKy1pdDJVVkFG…nR4S3daV3ZGRFdIUDVndVlySVJ4dDJZd2Q4eEwrLWp3WGl2dmVENXB2Q2czRkFicHNYdjdJWkxPUistWFhHT1l4SEJma1dGMHhRSE9NUWhwTVErQUQwQVBRLQ=="

# 🌐 AirIQ Test API URL
BASE_URL = "http://airiqnewapi.mywebcheck.in/TravelAPI.svc"   # replace with correct base URL from docs

# Agent / user details
AGENT_ID = "AQAG059771"      # replace with your Agent ID
USERNAME = "9864851451"      # replace with your Username

# ✈️ Availability request payload (DEL → BOM)
payload = {
    "AgentInfo": {
        "AgentId": AGENT_ID,
        "UserName": USERNAME,
        "AppType": "API",
        "Version": 2.0
    },
    "TripType": "O",
    "AvailInfo": [
        {
            "DepartureStation": "DEL",
            "ArrivalStation": "BOM",
            "FlightDate": "20251015",  # must be future date in YYYYMMDD
            "FarecabinOption": "E",
            "FareType": "N",
            "OnlyDirectFlight": False
        }
    ],
    "PassengersInfo": {
        "AdultCount": 1,
        "ChildCount": 0,
        "InfantCount": 0
    }
}

# 🔐 Authorization header
headers = {"Authorization": TOKEN}

# 🚀 Make API call
try:
    r = requests.post(f"{BASE_URL}/Availability", json=payload, headers=headers, timeout=20)
    print("Status:", r.status_code)
    print("Response JSON:")
    print(r.json())
except Exception as e:
    print("Error:", str(e))
