from flask import Flask, render_template, request, jsonify
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import os
from utils.aqi_utils import (get_category, get_aqi_status, get_status_color, get_recommendation, get_advice, get_precautions)
from models import db, AQIReading, init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aqi_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)
def create_session_with_retries():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

session = create_session_with_retries()

# Sample AQI data for demonstration
MOCK_AQI_DATA = {
    'delhi': {'location': 'Delhi, India', 'aqi': 156, 'status': 'UNHEALTHY', 'pm25': 92, 'pm10': 148, 'no2': 45, 'co': 1.2},
    'mumbai': {'location': 'Mumbai, India', 'aqi': 89, 'status': 'MODERATE', 'pm25': 45, 'pm10': 78, 'no2': 32, 'co': 0.8},
    'new york': {'location': 'New York, USA', 'aqi': 52, 'status': 'MODERATE', 'pm25': 25, 'pm10': 40, 'no2': 28, 'co': 0.5},
    'london': {'location': 'London, UK', 'aqi': 45, 'status': 'GOOD', 'pm25': 20, 'pm10': 35, 'no2': 24, 'co': 0.4},
}

def save_aqi_reading(location, aqi, status, pm25, pm10, no2, co, recommendation):
    """Save AQI reading to database"""
    try:
        reading = AQIReading(
            location=location,
            aqi=aqi,
            status=status,
            pm25=pm25,
            pm10=pm10,
            no2=no2,
            co=co,
            recommendation=recommendation
        )
        db.session.add(reading)
        db.session.commit()
        logger.info(f"Saved AQI reading for {location} to database")
        return True
    except Exception as e:
        logger.error(f"Error saving AQI reading: {str(e)}")
        db.session.rollback()
        return False

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/aqi")
def aqi():
    try:
        latest_reading = AQIReading.query.order_by(
            AQIReading.timestamp.desc()
        ).first()

        if latest_reading:
            return render_template(
                "dashboard.html",
                reading=latest_reading
            )

        return render_template(
            "dashboard.html",
            reading=None
        )

    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return render_template(
            "dashboard.html",
            reading=None
        )

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/search", methods=['POST'])
def search():
    try:
        data = request.get_json()
        city = data.get('city', '').strip().lower()
        
        if not city:
            logger.warning("Empty city input received")
            return jsonify({
                'success': False,
                'message': 'Please enter a valid city name'
            }), 400
        
        # Try to get data from mock data first (for demo purposes)
        if city in MOCK_AQI_DATA:
            logger.info(f"Using mock data for city: {city}")
            aqi_data = MOCK_AQI_DATA[city]
            recommendation = get_recommendation(aqi_data['aqi'])
            
            # Save to database
            save_aqi_reading(
                aqi_data['location'],
                aqi_data['aqi'],
                aqi_data['status'],
                aqi_data['pm25'],
                aqi_data['pm10'],
                aqi_data['no2'],
                aqi_data['co'],
                recommendation
            )
            
            return jsonify({
                'success': True,
                'location': aqi_data['location'],
                'aqi': aqi_data['aqi'],
                'status': aqi_data['status'],
                'pm25': aqi_data['pm25'],
                'pm10': aqi_data['pm10'],
                'no2': aqi_data['no2'],
                'co': aqi_data['co'],
                'recommendation': recommendation
            })
        
        # Try to fetch from real API
        logger.info(f"Fetching API data for city: {city}")
        aqi_data = fetch_from_api(city)
        
        if aqi_data:
            recommendation = get_recommendation(aqi_data['aqi'])
            
            # Save to database
            save_aqi_reading(
                aqi_data['location'],
                aqi_data['aqi'],
                aqi_data['status'],
                aqi_data['pm25'],
                aqi_data['pm10'],
                aqi_data['no2'],
                aqi_data['co'],
                recommendation
            )
            
            return jsonify({
                'success': True,
                'location': aqi_data['location'],
                'aqi': aqi_data['aqi'],
                'status': aqi_data['status'],
                'pm25': aqi_data['pm25'],
                'pm10': aqi_data['pm10'],
                'no2': aqi_data['no2'],
                'co': aqi_data['co'],
                'recommendation': recommendation
            })
        else:
            logger.warning(f"No data found for city: {city}")
            return jsonify({
                'success': False,
                'message': f'City not found: {city}. Try another location.'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while fetching AQI data. Please try again.'
        }), 500

def fetch_from_api(city):
    """
    Fetch AQI data from World Air Quality Index API
    
    Args:
        city (str): City name to search
        
    Returns:
        dict: AQI data or None if request fails
    """
    try:
        api_url = f'https://api.waqi.info/feed/{city}/?token=demo'
        
        # Make request with timeout
        response = session.get(api_url, timeout=5)
        response.raise_for_status()  # Raise exception for bad status codes
        
        api_data = response.json()
        
        # Check if API returned successful response
        if api_data.get('status') != 'ok':
            logger.warning(f"API returned non-ok status: {api_data.get('status')}")
            return None
        
        # Extract AQI value
        aqi_value = api_data['data'].get('aqi')
        if aqi_value is None:
            logger.warning(f"No AQI value in response for {city}")
            return None
        
        # Extract pollutant data
        pollutants = api_data['data'].get('iaqi', {})
        pm25 = pollutants.get('pm25', {}).get('v', 'N/A')
        pm10 = pollutants.get('pm10', {}).get('v', 'N/A')
        no2 = pollutants.get('no2', {}).get('v', 'N/A')
        co = pollutants.get('co', {}).get('v', 'N/A')
        
        # Extract location name
        location_name = api_data['data'].get('city', {}).get('name', city)
        
        logger.info(f"Successfully fetched AQI data for {location_name}: {aqi_value}")
        
        return {
            'location': location_name,
            'aqi': aqi_value,
            'status': get_aqi_status(aqi_value),
            'pm25': pm25,
            'pm10': pm10,
            'no2': no2,
            'co': co
        }
        
    except requests.exceptions.Timeout:
        logger.error(f"API request timed out for city: {city}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while fetching data for city: {city}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code} for city: {city}")
        return None
    except ValueError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching API data: {str(e)}")
        return None

@app.route("/results")
def results():
    # Get parameters from URL query string
    location = request.args.get('city', 'Unknown Location')
    aqi = request.args.get('aqi', 'N/A')
    status = request.args.get('status', 'UNKNOWN')
    pm25 = request.args.get('pm25', 'N/A')
    pm10 = request.args.get('pm10', 'N/A')
    no2 = request.args.get('no2', 'N/A')
    co = request.args.get('co', 'N/A')
    recommendation = request.args.get('recommendation', 'No recommendation available')
    
    # Determine color based on status using utility function
    status_color = get_status_color(status)
    
    return render_template("results.html", 
                          location=location,
                          aqi=aqi,
                          status=status,
                          status_color=status_color,
                          pm25=pm25,
                          pm10=pm10,
                          no2=no2,
                          co=co,
                          recommendation=recommendation)

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/api/history")
def get_history():
    """API endpoint to get search history"""
    try:
        # Get all readings sorted by timestamp (newest first)
        readings = AQIReading.query.order_by(AQIReading.timestamp.desc()).all()
        
        if not readings:
            return jsonify({
                'success': True,
                'readings': [],
                'message': 'No search history yet'
            })
        
        readings_data = [reading.to_dict() for reading in readings]
        return jsonify({
            'success': True,
            'readings': readings_data
        })
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error retrieving history'
        }), 500

if __name__=="__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

