import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from airiq_client import AirIQClient
import datetime

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
airiq = AirIQClient()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    origin = request.form.get("origin")
    destination = request.form.get("destination")
    date = datetime.datetime.strptime(request.form.get("date"), "%Y-%m-%d")
    try:
        data = airiq.availability(origin, destination, date)
        flights = data.get("ItineraryFlightList", [])
        return render_template("results.html", flights=flights)
    except Exception as e:
        flash(f"Error: {e}")
        return redirect(url_for("index"))


@app.route("/test-login")
def test_login():
    """Call AirIQ Login and show raw response in browser, plus outbound IP."""
    try:
        # Check outbound IP
        ip = requests.get("https://ifconfig.me", timeout=5).text

        # Try AirIQ login
        token = airiq._login()

        return {
            "status": "success",
            "outbound_ip": ip,
            "token": token
        }
    except Exception as e:
        ip = None
        try:
            ip = requests.get("https://ifconfig.me", timeout=5).text
        except:
            pass
        return {
            "status": "error",
            "outbound_ip": ip,
            "message": str(e)
        }

if __name__ == "__main__":
    app.run(debug=True)
