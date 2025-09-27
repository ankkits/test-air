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
        
        # Example test call (uncomment when you know the actual endpoints)
        try:
            # Test if we can make a basic request
            print("\n🧪 Testing connection...")
            # You can add actual API endpoints here when you know them
            
        except Exception as e:
            print(f"⚠️ Test request error: {e}")
        
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
                <html>
                <body>
                    <h1>Travel API Client Status</h1>
                    <p>Status: {status}</p>
                    <p>Agent ID: AQAG059771</p>
                    <p>Base URL: http://airiqnewapi.mywebcheck.in/TravelAPI.svc</p>
                    <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            
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