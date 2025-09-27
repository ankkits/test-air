import requests
import base64
import json
from datetime import datetime, timedelta
import time

class TravelAPIClient:
    def __init__(self, agent_id, username, password, base_url):
        """
        Initialize the Travel API client
        
        Args:
            agent_id (str): Your agent ID
            username (str): Your username
            password (str): Your password
            base_url (str): Base URL of the API
        """
        self.agent_id = agent_id
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.token_expiry = None
        self.session = requests.Session()
    
    def _create_basic_auth_string(self):
        """
        Create Base64 encoded authentication string
        Format: AgentID*Username:Password
        """
        auth_string = f"{self.agent_id}*{self.username}:{self.password}"
        encoded_bytes = base64.b64encode(auth_string.encode('utf-8'))
        return encoded_bytes.decode('utf-8')
    
    def authenticate(self):
        """
        Authenticate with the API and get token
        """
        try:
            # Create the Basic Auth header
            auth_header = self._create_basic_auth_string()
            
            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Assuming login endpoint - you may need to adjust this
            login_url = f"{self.base_url}/Login"
            
            print(f"Authenticating with URL: {login_url}")
            print(f"Using Auth Header: Basic {auth_header}")
            
            response = self.session.post(login_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract token from response - adjust based on actual API response structure
                if 'Token' in data:
                    self.token = data['Token']
                    # Set token expiry (assuming 1 hour if not provided)
                    self.token_expiry = datetime.now() + timedelta(hours=1)
                    print("Authentication successful!")
                    print(f"Token: {self.token}")
                    return True
                else:
                    print("Authentication response received but no token found")
                    print(f"Response: {data}")
                    return False
            else:
                print(f"Authentication failed. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Request error during authentication: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during authentication: {e}")
            return False
    
    def is_token_valid(self):
        """
        Check if current token is valid and not expired
        """
        if not self.token:
            return False
        
        if self.token_expiry and datetime.now() >= self.token_expiry:
            return False
        
        return True
    
    def ensure_authenticated(self):
        """
        Ensure we have a valid token, authenticate if needed
        """
        if not self.is_token_valid():
            print("Token invalid or expired, re-authenticating...")
            return self.authenticate()
        return True
    
    def make_authenticated_request(self, endpoint, method='GET', data=None, params=None):
        """
        Make an authenticated request to the API
        
        Args:
            endpoint (str): API endpoint (e.g., '/GetFlights')
            method (str): HTTP method ('GET', 'POST', etc.)
            data (dict): Request body data for POST requests
            params (dict): Query parameters for GET requests
        """
        if not self.ensure_authenticated():
            return None
        
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            'Authorization': f'Bearer {self.token}',  # or however the API expects the token
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code == 401:
                # Token might have expired, try to re-authenticate
                print("Received 401, attempting re-authentication...")
                if self.authenticate():
                    headers['Authorization'] = f'Bearer {self.token}'
                    if method.upper() == 'GET':
                        response = self.session.get(url, headers=headers, params=params)
                    elif method.upper() == 'POST':
                        response = self.session.post(url, headers=headers, json=data)
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
    
    def get_data(self, endpoint, params=None):
        """
        Convenience method for GET requests
        """
        response = self.make_authenticated_request(endpoint, 'GET', params=params)
        if response and response.status_code == 200:
            return response.json()
        elif response:
            print(f"Request failed with status {response.status_code}: {response.text}")
        return None
    
    def post_data(self, endpoint, data):
        """
        Convenience method for POST requests
        """
        response = self.make_authenticated_request(endpoint, 'POST', data=data)
        if response and response.status_code == 200:
            return response.json()
        elif response:
            print(f"Request failed with status {response.status_code}: {response.text}")
        return None
    
    def search_availability(self, departure_station, arrival_station, flight_date, 
                          trip_type="O", airline_id="", cabin="E", fare_type="N", 
                          direct_only=False, adult_count=1, child_count=0, infant_count=0):
        """
        Search flight availability
        
        Args:
            departure_station (str): 3-letter IATA departure airport code (e.g., "IXB")
            arrival_station (str): 3-letter IATA arrival airport code (e.g., "DEL") 
            flight_date (str): Flight date in YYYYMMDD format (e.g., "20241010")
            trip_type (str): O-Oneway, R-Roundtrip, Y-Roundtrip Special
            airline_id (str): Two-letter airline code (empty for all airlines)
            cabin (str): E-Economy, P-Premium Economy, B-Business, F-First
            fare_type (str): N-Normal, C-Corporate, R-Retail
            direct_only (bool): True for direct flights only
            adult_count (int): Number of adults (1-9)
            child_count (int): Number of children
            infant_count (int): Number of infants (1-4)
        """
        
        # Prepare the request payload according to API documentation
        payload = {
            "AgentInfo": {
                "AgentId": self.agent_id,
                "UserName": self.username,
                "AppType": "API",
                "Version": "2.0"
            },
            "TripType": trip_type,
            "AirlineID": airline_id,
            "AvailInfo": [
                {
                    "DepartureStation": departure_station.upper(),
                    "ArrivalStation": arrival_station.upper(),
                    "FlightDate": flight_date,
                    "FarecabinOption": cabin.upper(),
                    "FareType": fare_type.upper(),
                    "OnlyDirectFlight": direct_only
                }
            ],
            "PassengersInfo": {
                "AdultCount": str(adult_count),
                "ChildCount": str(child_count),
                "InfantCount": str(infant_count)
            }
        }
        
        print(f"🔍 Searching flights: {departure_station} → {arrival_station} on {flight_date}")
        print(f"📋 Request payload: {json.dumps(payload, indent=2)}")
        
        # Make the API call
        response = self.post_data('/Availability', payload)
        return response

def main():
    """
    Main function that runs the Travel API client
    """
    # Your credentials - hardcoded, no env variables needed
    AGENT_ID = "AQAG059771"
    USERNAME = "9864851451"
    PASSWORD = "9864851451"
    BASE_URL = "http://airiqnewapi.mywebcheck.in/TravelAPI.svc"
    
    print("🚀 Starting Travel API Client...")
    print(f"📡 Connecting to: {BASE_URL}")
    print(f"🔑 Agent ID: {AGENT_ID}")
    
    # Create client instance
    client = TravelAPIClient(AGENT_ID, USERNAME, PASSWORD, BASE_URL)
    
    # Authenticate
    if client.authenticate():
        print("✅ Authentication successful!")
        
        # Keep the script running and ready for API calls
        print("\n🔄 Client is running and authenticated!")
        print("📋 Available methods:")
        print("   - client.get_data('/endpoint')")
        print("   - client.post_data('/endpoint', data)")
        print("   - client.search_availability(from, to, date)")
        
        # Test the availability search for October 10th
        try:
            print("\n🧪 Testing Availability API with sample search...")
            print("🔍 Searching: IXB → DEL on 2024-10-10")
            
            # Call the availability API
            results = client.search_availability(
                departure_station="IXB",    # Bagdogra
                arrival_station="DEL",      # Delhi  
                flight_date="20241010",     # October 10, 2024
                adult_count=1,
                cabin="E",                  # Economy
                direct_only=False
            )
            
            if results:
                print("✅ Availability search successful!")
                print(f"📊 Results: {json.dumps(results, indent=2)}")
            else:
                print("⚠️ No results returned from availability search")
                
        except Exception as e:
            print(f"⚠️ Availability test error: {e}")
        
        print("\n✅ Script completed successfully!")
        return client
        
    else:
        print("❌ Authentication failed!")
        return None

# For continuous running (useful for web services on Render)
def run_as_web_service():
    """
    Function to run as a simple web service on Render
    """
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    import urllib.parse
    from datetime import datetime
    
    # Initialize the API client globally
    client = main()
    
    class APIHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                status = "✅ Connected" if client and client.is_token_valid() else "❌ Not Connected"
                
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Travel API Client</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        .status {{ padding: 20px; background: #f0f8ff; border-radius: 8px; }}
                        .search-form {{ margin-top: 30px; padding: 20px; background: #f9f9f9; border-radius: 8px; }}
                        input, select {{ padding: 8px; margin: 5px; }}
                        button {{ padding: 10px 20px; background: #007cba; color: white; border: none; border-radius: 4px; cursor: pointer; }}
                        button:hover {{ background: #005a87; }}
                        .results {{ margin-top: 20px; padding: 20px; background: #fff; border: 1px solid #ddd; border-radius: 8px; }}
                        pre {{ background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto; }}
                    </style>
                </head>
                <body>
                    <h1>🛫 Travel API Client</h1>
                    
                    <div class="status">
                        <h2>Status</h2>
                        <p><strong>Connection:</strong> {status}</p>
                        <p><strong>Agent ID:</strong> AQAG059771</p>
                        <p><strong>Base URL:</strong> http://airiqnewapi.mywebcheck.in/TravelAPI.svc</p>
                        <p><strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <div class="search-form">
                        <h2>🔍 Search Flights</h2>
                        <form action="/search" method="get">
                            <div>
                                <label>From (Airport Code):</label>
                                <input type="text" name="from" value="IXB" maxlength="3" required>
                                
                                <label>To (Airport Code):</label>
                                <input type="text" name="to" value="DEL" maxlength="3" required>
                            </div>
                            
                            <div>
                                <label>Date (YYYY-MM-DD):</label>
                                <input type="date" name="date" value="2024-10-10" required>
                                
                                <label>Adults:</label>
                                <select name="adults">
                                    <option value="1">1</option>
                                    <option value="2">2</option>
                                    <option value="3">3</option>
                                    <option value="4">4</option>
                                </select>
                            </div>
                            
                            <div>
                                <label>Cabin Class:</label>
                                <select name="cabin">
                                    <option value="E">Economy</option>
                                    <option value="P">Premium Economy</option>
                                    <option value="B">Business</option>
                                    <option value="F">First</option>
                                </select>
                                
                                <label>
                                    <input type="checkbox" name="direct" value="true"> Direct flights only
                                </label>
                            </div>
                            
                            <button type="submit">🔍 Search Flights</button>
                        </form>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            
            elif self.path.startswith('/search'):
                # Parse query parameters
                parsed_url = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed_url.query)
                
                # Extract parameters
                from_airport = params.get('from', ['IXB'])[0].upper()
                to_airport = params.get('to', ['DEL'])[0].upper()
                date_str = params.get('date', ['2024-10-10'])[0]
                adults = int(params.get('adults', ['1'])[0])
                cabin = params.get('cabin', ['E'])[0]
                direct_only = 'direct' in params
                
                # Convert date format from YYYY-MM-DD to YYYYMMDD
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    flight_date = date_obj.strftime('%Y%m%d')
                except:
                    flight_date = '20241010'  # fallback
                
                # Search flights
                if client and client.is_token_valid():
                    try:
                        results = client.search_availability(
                            departure_station=from_airport,
                            arrival_station=to_airport,
                            flight_date=flight_date,
                            adult_count=adults,
                            cabin=cabin,
                            direct_only=direct_only
                        )
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Flight Search Results</title>
                            <style>
                                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                                .header {{ background: #f0f8ff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                                .results {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; }}
                                pre {{ background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto; font-size: 12px; }}
                                .back-btn {{ display: inline-block; padding: 10px 20px; background: #007cba; color: white; text-decoration: none; border-radius: 4px; margin-bottom: 20px; }}
                                .back-btn:hover {{ background: #005a87; }}
                            </style>
                        </head>
                        <body>
                            <a href="/" class="back-btn">← Back to Search</a>
                            
                            <div class="header">
                                <h1>✈️ Flight Search Results</h1>
                                <p><strong>Route:</strong> {from_airport} → {to_airport}</p>
                                <p><strong>Date:</strong> {date_str} ({flight_date})</p>
                                <p><strong>Passengers:</strong> {adults} Adult(s)</p>
                                <p><strong>Cabin:</strong> {cabin} | <strong>Direct Only:</strong> {direct_only}</p>
                            </div>
                            
                            <div class="results">
                                <h2>API Response:</h2>
                                <pre>{json.dumps(results, indent=2) if results else 'No results returned'}</pre>
                            </div>
                        </body>
                        </html>
                        """
                        self.wfile.write(html.encode())
                        
                    except Exception as e:
                        self.send_response(500)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        error_html = f"""
                        <html><body>
                            <h1>Error</h1>
                            <p>Failed to search flights: {str(e)}</p>
                            <a href="/">← Back</a>
                        </body></html>
                        """
                        self.wfile.write(error_html.encode())
                else:
                    self.send_response(500)
                    self.send_header('Content-type', 'text/html')  
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Error: Not authenticated</h1><a href='/'>Back</a></body></html>")
            
            elif self.path == '/status':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                status = {
                    "connected": client and client.is_token_valid(),
                    "agent_id": "AQAG059771",
                    "base_url": "http://airiqnewapi.mywebcheck.in/TravelAPI.svc",
                    "timestamp": datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(status).encode())
            
            else:
                self.send_response(404)
                self.end_headers()
    
    # Run on port that Render provides
    import os
    port = int(os.environ.get('PORT', 8000))
    
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"🌐 Web service running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    import os
    
    # Check if running on Render (Render sets the PORT environment variable)
    if os.environ.get('PORT'):
        print("🔧 Detected Render environment - starting web service...")
        run_as_web_service()
    else:
        print("💻 Running locally...")
        main()