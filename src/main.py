from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

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

@app.get("/me", response_class=RedirectResponse)
async def showCurrentLocation(request: Request):
    current_city = weather.getCurrentCity(request.client.host)
    encoded_city = current_city.replace(" ", "-")

    return RedirectResponse(f"/{encoded_city}", status_code=302)

@app.get("/{city}", response_class=HTMLResponse)
async def showCity(request: Request, city: str):
    city = city.replace("-", " ")
    place = weather.getPlaceData(city)
    placeholder = weather.getRandomCity()

    if not place.exists:
        context = {
            "city": place.name,
            "placeholder": placeholder
        }

        return templates.TemplateResponse(
            request=request, name='notFound.html', context=context
        )

    city_weather = weather.getWeather(place)

    context = {
        "city": place.name,
        "placeholder": placeholder,
        "raining": city_weather.precipitation > 0,
        "rain_level": city_weather.precipitation,
        "weather_code": city_weather.weather_code
    }

    return templates.TemplateResponse(
        request=request, name='city.html', context=context
    )
