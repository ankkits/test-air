import base64, requests, datetime
from config import Config

class AirIQClient:
    def __init__(self):
        self.base_url = Config.API_BASE_URL.rstrip("/")
        self.agent_id = Config.AGENT_ID
        self.username = Config.API_USERNAME
        self.password = Config.API_PASSWORD

    def _login(self):
        raw = f"{self.agent_id}*{self.username}:{self.password}"
        b64 = base64.b64encode(raw.encode()).decode()
        headers = {"Authorization": b64}

        resp = requests.post(f"{self.base_url}/Login", headers=headers, timeout=10)
        resp.raise_for_status()
        j = resp.json()

        token = j.get("Token")
        if not token:
            raise Exception(f"Login failed: {j}")
        return token

    def availability(self, origin, destination, date, adults=1):
        # Always get a fresh token
        token = self._login()

        payload = {
            "AgentInfo": {
                "AgentId": self.agent_id,
                "UserName": self.username,
                "AppType": "API",
                "Version": 2.0,
            },
            "TripType": "O",
            "AvailInfo": [
                {
                    "DepartureStation": origin,
                    "ArrivalStation": destination,
                    "FlightDate": date.strftime("%Y%m%d"),
                    "FarecabinOption": "E",
                    "FareType": "N",
                    "OnlyDirectFlight": False,
                }
            ],
            "PassengersInfo": {
                "AdultCount": adults,
                "ChildCount": 0,
                "InfantCount": 0,
            },
        }
        headers = {"Authorization": token}
        r = requests.post(f"{self.base_url}/Availability", json=payload, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()

    def pricing(self, flight_payload):
        token = self._login()
        headers = {"Authorization": token}
        r = requests.post(f"{self.base_url}/Pricing", json=flight_payload, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()

    def book(self, booking_payload):
        token = self._login()
        headers = {"Authorization": token}
        r = requests.post(f"{self.base_url}/Book", json=booking_payload, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()
