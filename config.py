import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret")
    API_BASE_URL = os.environ.get("API_BASE_URL")
    AGENT_ID = os.environ.get("AGENT_ID")
    API_USERNAME = os.environ.get("API_USERNAME")
    API_PASSWORD = os.environ.get("API_PASSWORD")
