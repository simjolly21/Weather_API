from flask import Flask, jsonify, request
import requests
import redis
import os
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Setup rate limiter (limit to 100 requests per hour per IP)
limiter = Limiter(app, key_func=get_remote_address, default_limits=["100 per hour"])

# Initialize Redis connection
redis_client = redis.StrictRedis.from_url(os.getenv('REDIS_URL'))

# Visual Crossing API base URL and key
API_BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
API_KEY = os.getenv("API_KEY")

# Cache expiration time (12 hours)
CACHE_EXPIRATION = 43200  # seconds (12 hours)


@app.route('/weather', methods=['GET'])
@limiter.limit("10 per minute")  # Rate limit for this specific endpoint (10 requests/min)
def get_weather():
    # Get the city from the query parameters
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City is required'}), 400

    # Check if data is available in Redis cache
    cached_data = redis_client.get(city)
    if cached_data:
        return jsonify({'source': 'cache', 'data': cached_data.decode('utf-8')})

    # If not in cache, fetch from Visual Crossing API
    api_url = f"{API_BASE_URL}{city}?key={API_KEY}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        weather_data = response.json()
        
        # Cache the result in Redis for 12 hours
        redis_client.setex(city, CACHE_EXPIRATION, str(weather_data))

        return jsonify({'source': 'api', 'data': weather_data})
    except requests.exceptions.RequestException as e:
        # Handle API errors (e.g., network issues, invalid API response)
        return jsonify({'error': str(e)}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'rate limit exceeded'}), 429

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
