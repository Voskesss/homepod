import python_weather
import asyncio
import assist
from icrawler.builtin import GoogleImageCrawler
import os
import spot


async def get_weather(city_name):
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        weather = await client.get(city_name)
        return weather

def get_weather_info(city_name="Chicago"):
    weather_description = asyncio.run(get_weather(city_name))
    return f"System information: {str(weather_description)}"

def parse_command(command):
    if "weather" in command.lower():
        city = "Chicago"  # Je kunt hier logica toevoegen om de stad uit het commando te halen
        weather_info = get_weather_info(city)
        response = assist.ask_question_memory(weather_info)
        return response
    else:
        # Voor alle andere commando's, stuur het direct naar de assistent
        response = assist.ask_question_memory(command)
        return response

    # ... andere commando's ...

def search(query):
    google_Crawler = GoogleImageCrawler(storage = {"root_dir": r'./images'})
    google_Crawler.crawl(keyword = query, max_num = 1)



        

    

        