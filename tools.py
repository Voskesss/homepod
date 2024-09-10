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
        done = assist.TTS(response)
    else:
        # Voor alle andere commando's, stuur het direct naar de assistent
        response = assist.ask_question_memory(command)
        done = assist.TTS(response)

    # ... andere commando's ...

def search(query):
    google_Crawler = GoogleImageCrawler(storage = {"root_dir": r'./images'})
    google_Crawler.crawl(keyword = query, max_num = 1)


def run_voice_assistant(circles, screen, background, draw_event, idle_event):
    recorder = AudioToTextRecorder(spinner=False, model="large", language="en", post_speech_silence_duration=0.1, silero_sensitivity=0.6)
    hot_words = ["happy", "alexa"]
    stop_words = ["stop", "end"]
    print("Say something...")
    
    while True:
        current_text = recorder.text()
        print(f"Current text: {current_text}")
        
        if any(hot_word in current_text.lower() for hot_word in hot_words):
            print(f"Hot word detected: {current_text}")
            
            # Say "Hello Jos"
            greeting = "Hello Jos"
            print(greeting)
            assist.TTS(greeting)
            
            while True:
                print("Assistant is listening... Say 'stop' to end.")
                
                recorder.stop()
                recorder.start()
                user_question = ""
                start_time = time.time()
                while not user_question and time.time() - start_time < 10:  # Wait max 10 seconds
                    user_question = recorder.text()
                    print(f"Detected text: {user_question}")  # Debug print
                    time.sleep(0.1)
                
                if not user_question or user_question == "***":
                    print("No valid question detected within 10 seconds.")
                    continue  # Instead of breaking, we continue listening
                
                print(f"User question: {user_question}")
                
                if any(stop_word in user_question.lower() for stop_word in stop_words):
                    print("Assistant stopped.")
                    break
                
                try:
                    response = tools.parse_command(user_question)
                    print(f"Assistant's response: {response}")
                    
                    if response and isinstance(response, str):
                        assist.TTS(response)
                    else:
                        print("No valid response to speak.")
                except Exception as e:
                    print(f"Error processing command: {e}")
                    assist.TTS("Sorry, there was an error processing your request.")
                
                recorder.stop()
                recorder.start()
        
        time.sleep(0.1)
        

    

        