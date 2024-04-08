import openmeteo_requests
import requests
import requests_cache
from retry_requests import retry
from enum import StrEnum

import random

from dataclasses import dataclass

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
THIRTY_MINUTES = 60 * 30

cache_session = requests_cache.CachedSession('.cache', expire_after=THIRTY_MINUTES)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

class WeatherType(StrEnum):
    CLEAR = "sun-fill"
    CLOUDY = "clouds-fill"
    DRIZZLE = "cloud-drizzle-fill"
    RAIN = "cloud-rain-fill"
    SNOW = "cloud-snow-fill"
    SHOWER = "cloud-rain-heavy-fill"
    THUNDER = "cloud-lightning-rain-fill"

@dataclass
class Place:
    name: str
    latitude: float
    longitude: float
    exists: bool = False

@dataclass
class Weather:
    weather_code: WeatherType
    precipitation: float

def getPlaceData(city: str) -> Place:
    params = {
        "name": city,
        "count": 1
    }
    response = cache_session.get(GEOCODING_URL, params)
    json = response.json()

    coords = Place("", 0, 0)
    try:
        results = json['results']
        result = results[0]
        name = result["name"]
        lat, long = result['latitude'], result['longitude']
        coords = Place(name, lat, long, True)
    except:
        pass

    return coords

def getWeather(coords: Place) -> Weather:
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

    weatherType: WeatherType = None

    if weather_code == 0:
        weatherType = WeatherType.CLEAR
    elif weather_code in [1, 2, 3]:
        weatherType = WeatherType.CLOUDY
    elif weather_code in [51, 53, 55, 56, 57]:
        weatherType = WeatherType.DRIZZLE
    elif weather_code in [61, 63, 65, 66, 67]:
        weatherType = WeatherType.RAIN
    elif weather_code in [71, 73, 75, 77]:
        weatherType = WeatherType.SNOW
    elif weather_code in [80, 81, 82, 85, 86]:
        weatherType = WeatherType.SHOWER
    elif weather_code in [95, 96, 99]:
        weatherType = WeatherType.THUNDER

    weather = Weather(weatherType, precip)

    return weather

def getRandomCity() -> str:
    city_list = ['New-Delhi', 'New-York', 'London', 'Berlin', 'Amsterdam', 'Ottawa', 'Sydney', 'Tokyo', 'Beijing']
    return random.choice(city_list)
