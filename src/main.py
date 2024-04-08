from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from . import weather

app = FastAPI()

app.mount("/static", StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='src/templates')


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):

    context = {
        'placeholder': weather.getRandomCity()
    }

    return templates.TemplateResponse(
        request=request, name='index.html', context=context
    )

@app.get("/{city}", response_class=HTMLResponse)
async def showCity(request: Request, city: str):
    city = city.replace("-", " ")
    place = weather.getPlaceData(city)

    if not place.exists:

        context = {
            "city": place.name
        }

        return templates.TemplateResponse(
            request=request, name='notFound.html', context=context
        )

    city_weather = weather.getWeather(place)
    placeholder = weather.getRandomCity()
    icon = weather.getWeatherIcon(city_weather.weather_code)

    context = {
        "city": place.name,
        "raining": city_weather.precipitation > 0,
        "rain_level": city_weather.precipitation,
        "weather_code": icon,
        "placeholder": placeholder
    }

    return templates.TemplateResponse(
        request=request, name='city.html', context=context
    )
