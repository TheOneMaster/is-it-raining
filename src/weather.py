import openmeteo_requests
import requests
import requests_cache
from retry_requests import retry

from dataclasses import dataclass

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
THIRTY_MINUTES = 60 * 30

cache_session = requests_cache.CachedSession('.cache', expire_after=THIRTY_MINUTES)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

@dataclass
class Coords:
    latitude: int
    longitude: int

@dataclass
class Weather:
    weather_code: int
    precipitation: int




def getCityCoords(city: str) -> Coords:
    params = {
        "name": city,
        "count": 1
    }
    response = cache_session.get(GEOCODING_URL, params)
    json = response.json()

    results = json['results']
    result = results[0]
    coords = Coords(result['latitude'], result['longitude'])

    return coords

def getWeather(coords: Coords) -> Weather:
    params = {
        'latitude': coords.latitude,
        'longitude': coords.longitude,
        'current': ['precipitation', 'weather_code']
    }

    responses = openmeteo.weather_api(FORECAST_URL, params)
    
    response = responses[0]
    current_weather = response.Current()
    precip = current_weather.Variables(0).Value()
    weather_code = current_weather.Variables(1).Value()

    weather = Weather(weather_code, precip)

    return weather

def main():
    coords = getCityCoords("Hamburg")
    raining = getWeather(coords, openmeteo)
    print(raining)

if __name__ == "__main__":
    main()


