import base64, requests, datetime
from config import Config

class AirIQClient:
    def __init__(self):
        self.base_url = Config.API_BASE_URL.rstrip("/")
        self.agent_id = Config.AGENT_ID
        self.username = Config.API_USERNAME
        self.password = Config.API_PASSWORD
        self.token = None
        self.token_expiry = None

    def _login(self):
        raw = f"{self.agent_id}*{self.username}:{self.password}"
        b64 = base64.b64encode(raw.encode()).decode()
        headers = {"Authorization": b64}

        # Debug: show request and response
        print("=== Login Request Debug ===")
        print("Login URL:", f"{self.base_url}/Login")
        print("Authorization header (Base64):", headers["Authorization"])
        print("Decoded format:", raw)
        print("===========================")

        resp = requests.post(f"{self.base_url}/Login", headers=headers, timeout=10)

        print("=== Login Response Debug ===")
        print("Status Code:", resp.status_code)
        try:
            print("Response JSON:", resp.json())
        except Exception:
            print("Response Text:", resp.text)
        print("============================")

        resp.raise_for_status()
        j = resp.json()
        self.token = j.get("Token")
        self.token_expiry = datetime.datetime.combine(
            datetime.date.today(), datetime.time(23, 59, 59)
        )
        return self.token

    def _get_token(self):
        if not self.token or datetime.datetime.now() >= self.token_expiry:
            return self._login()
        return self.token

    def availability(self, origin, destination, date, adults=1):
        token = self._get_token()
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
