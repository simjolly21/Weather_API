# Weather_API

This is the project link: https://roadmap.sh/projects/weather-api-wrapper-service

## Running the project:

1. Create the `.env` file with your API key and Redis URL.
2. Run the Flask app:
    `python Weather_API.py`
3. Make a request to your API:
    `curl httm://127.0.0.1:5000/weather?city=Singapore`

## Additional Improvements

- Testing; Write unit tests to test the API logic, especially for caching and error handling.
- Dockerization: Use Docker to containerize the application for easy deployment.
- Monitoring: Set up logging and monitoring for your API to track usage and potential issues.
