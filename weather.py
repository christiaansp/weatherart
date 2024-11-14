from PIL import Image, ImageDraw
import requests
from datetime import datetime
import time
from zoneinfo import ZoneInfo
import random

class WeatherArt:
    def __init__(self, width=1920, height=1080, block_size=1, modification_percentage=0.3):
        self.width = width
        self.height = height
        self.block_size = block_size
        self.modification_percentage = modification_percentage
        self.image = Image.new('RGB', (width, height), 'white')
        self.draw = ImageDraw.Draw(self.image)

        # OpenWeatherMap settings


        self.api_key = "" # openweather map api key here)
        self.city = "Amsterdam" # Change this to something else for a different city)
        self.country_code = "NL"
        



        self.color_palettes = {
            'clear_day': [
                (135, 206, 235),  # Sky blue
                (173, 216, 230),  # Light blue
                (176, 224, 230),  # Powder blue
                (240, 255, 255),  # Light cyan
                (224, 255, 255),  # Light sky cyan
                (250, 250, 210),  # Light goldenrod
            ],
            'clear_night': [
                (25, 25, 112),  # Midnight blue
                (0, 0, 139),    # Dark blue
                (18, 10, 143),  # Twilight blue
            ],
            'clouds': [
                (169, 169, 169),  # Dark gray clouds
                (190, 190, 190),  # Light gray clouds
                (211, 211, 211),  # Soft cloud gray
            ],
            'rain': [
                (105, 105, 105),  # Stormy dark gray
                (119, 136, 153),  # Rainy day gray
                (47, 79, 79),     # Heavy rain teal
            ],
            'snow': [
                (255, 250, 250),  # Snow white
                (240, 248, 255),  # Fresh snow
                (245, 245, 245),  # Soft snow
            ],
            'mist': [
                (169, 169, 169),  # Dense fog gray
                (128, 128, 128),  # Foggy mist gray
                (220, 220, 220),  # Misty gray
            ],
            'default': [
                (176, 224, 230),  # Powder blue
                (255, 250, 250),  # Snow
                (240, 248, 255),  # Alice blue
                (245, 245, 245),  # White smoke
                (220, 220, 220),  # Gainsboro
            ]
        }

    def get_weather(self):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city},{self.country_code}&appid={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                weather_main = data['weather'][0]['main'].lower()
                weather_desc = data['weather'][0]['description']
                temp = data['main']['temp'] - 273.15
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                feels_like = data['main']['feels_like'] - 273.15
                
                print("\n=== Weather Statistics ===")
                print(f"Location: {self.city}, {self.country_code}")
                print(f"Temperature: {temp:.1f}°C")
                print(f"Feels like: {feels_like:.1f}°C")
                print(f"Weather: {weather_main} ({weather_desc})")
                print(f"Humidity: {humidity}%")
                print(f"Wind Speed: {wind_speed} m/s")
                print("=====================")
                
                return weather_main
            else:
                print(f"Error: {data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None

    def is_night(self):
        now = datetime.now(ZoneInfo("Europe/Amsterdam"))
        return now.hour < 6 or now.hour > 20

    def get_weather_palette(self, weather_desc):
        if weather_desc == 'clear':
            return self.color_palettes['clear_night' if self.is_night() else 'clear_day']
        elif weather_desc in self.color_palettes:
            return self.color_palettes[weather_desc]
        else:
            return self.color_palettes['default']

    def draw_block(self, x, y, color):
        x1 = x * self.block_size
        y1 = y * self.block_size
        x2 = x1 + self.block_size
        y2 = y1 + self.block_size
        self.draw.rectangle([x1, y1, x2, y2], fill=color)

    def save_image(self, filename):
        try:
            self.image.save(filename)
            print(f"Saved image: {filename}")
        except Exception as e:
            print(f"Error saving image: {e}")

    def modify_blocks(self, weather_desc):
        if not weather_desc:
            return

        try:
            palette = self.get_weather_palette(weather_desc)
            
            blocks_x = self.width // self.block_size
            blocks_y = self.height // self.block_size
            num_blocks = int((blocks_x * blocks_y) * self.modification_percentage)

            print(f"Modifying {num_blocks} blocks...")

            pixels = self.image.load()

            for _ in range(num_blocks):
                x = random.randint(0, blocks_x - 1)
                y = random.randint(0, blocks_y - 1)
                
                color = random.choice(palette)
                
                variation = 10
                varied_color = tuple(
                    max(0, min(255, c + random.randint(-variation, variation)))
                    for c in color
                )
                
          
                current_color = pixels[x * self.block_size, y * self.block_size]
                
                blended_color = tuple(
                    int((c1 * 0.3 + c2 * 0.7)) 
                    for c1, c2 in zip(varied_color, current_color)
                )
                
                self.draw_block(x, y, blended_color)

            print("Block modification complete")

        except Exception as e:
            print(f"Error modifying blocks: {e}")

    def run(self, interval_seconds=15):
        try:
            while True:  
                print("\nFetching weather data...")
                
                weather_condition = self.get_weather()
                
                if weather_condition:
                    print(f"Current weather: {weather_condition}")
                    print(f"Modifying {self.modification_percentage * 100}% of pixels")
                    
                    self.modify_blocks(weather_condition)
                    self.save_image("weather_art.png")
                
                print(f"\nWaiting {interval_seconds} seconds until next update...")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\nProgram stopped by user")
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)
            self.run(interval_seconds)  

if __name__ == "__main__":
    print("Starting Weather Art Generator")
    print("Creating artwork based on Zutphen weather conditions")
    
    try:
        pixels_percent = float(input("Enter percentage of pixels to modify (0.1 = 10%, 0.5 = 50%, etc.): "))
        interval = int(input("Enter update interval in seconds: "))
    except ValueError:
        print("Invalid input. Using default values...")
        pixels_percent = 0.3
        interval = 15

    art = WeatherArt(block_size=1, modification_percentage=pixels_percent)
    
    art.run(interval_seconds=interval)
