import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Phidata imports
from phi.agent import Agent
from phi.model.google import Gemini

class TravelScheduler:
    """Simplified Travel Scheduler without custom tools to avoid issues"""
    
    def __init__(self, gemini_api_key: str, weather_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.weather_api_key = weather_api_key
        
        # Initialize Gemini model with specific version
        self.model = Gemini(
            api_key=gemini_api_key,
            id="gemini-1.5-flash",  # Specify model version
            temperature=0.7
        )
        
        # Initialize agents
        self.setup_agents()
    
    def setup_agents(self):
        """Setup specialized travel agents"""
        
        # Itinerary Planning Agent
        self.itinerary_agent = Agent(
            name="TravelItineraryPlanner",
            model=self.model,
            description="Expert travel itinerary planner",
            instructions="""
            You are an expert travel itinerary planner specializing in creating detailed travel schedules.
            
            Your capabilities:
            1. Create detailed day-by-day travel schedules
            2. Suggest activities based on destination, budget, and interests
            3. Optimize travel routes and timing
            4. Provide backup plans for different weather conditions
            5. Include practical travel information
            
            Always:
            - Create specific day-by-day itineraries
            - Consider travel logistics and timing
            - Provide specific recommendations with locations
            - Include estimated costs and duration
            - Format responses clearly with proper sections
            """,
            show_tool_calls=False,
            markdown=True
        )
        
        # Travel Advisor Agent
        self.advisor_agent = Agent(
            name="TravelAdvisor",
            model=self.model,
            description="Knowledgeable travel advisor and destination expert",
            instructions="""
            You are a knowledgeable travel advisor with extensive travel knowledge and expertise.
            
            Your expertise includes:
            1. Destination recommendations based on preferences
            2. Cultural tips and local customs
            3. Safety and health advice
            4. Transportation guidance
            5. Accommodation suggestions
            6. Local cuisine recommendations
            7. Hidden gems and off-the-beaten-path experiences
            
            Always:
            - Provide practical, actionable advice
            - Consider safety, budget, and cultural factors
            - Suggest authentic local experiences
            - Include specific details like names, addresses, costs
            """,
            show_tool_calls=False,
            markdown=True
        )
    
    def get_weather_info(self, destination: str) -> str:
        """Get weather information using direct API call"""
        try:
            # Current weather
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": destination,
                "appid": self.weather_api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current_weather = f"""Current Weather in {data['name']}, {data['sys']['country']}:
Temperature: {data['main']['temp']}°C (feels like {data['main']['feels_like']}°C)
Condition: {data['weather'][0]['description'].title()}
Humidity: {data['main']['humidity']}%
Wind Speed: {data['wind']['speed']} m/s"""
            
            # Forecast
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast"
            forecast_params = {
                "q": destination,
                "appid": self.weather_api_key,
                "units": "metric",
                "cnt": 24  # 3 days worth of 3-hour forecasts
            }
            
            forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            forecast_text = f"\n\nWeather Forecast for {forecast_data['city']['name']}:\n"
            
            current_date = None
            for item in forecast_data["list"][:8]:  # First 24 hours
                forecast_date = item["dt_txt"][:10]
                forecast_time = item["dt_txt"][11:16]
                
                if forecast_date != current_date:
                    forecast_text += f"\n📅 {forecast_date}:\n"
                    current_date = forecast_date
                
                forecast_text += f"  {forecast_time}: {item['main']['temp']}°C, {item['weather'][0]['description']}\n"
            
            return current_weather + forecast_text
            
        except Exception as e:
            return f"Weather information unavailable for {destination}. Error: {str(e)}"
    
    def plan_complete_trip(self, destination: str, start_date: str, end_date: str, 
                          preferences: str = "", budget: str = "moderate") -> str:
        """Plan a complete trip using the itinerary agent"""
        
        # Get weather information
        weather_info = self.get_weather_info(destination)
        
        prompt = f"""
        Plan a comprehensive travel itinerary with these details:
        
        🏙️ **Destination:** {destination}
        📅 **Travel Dates:** {start_date} to {end_date}
        ❤️ **Preferences:** {preferences}
        💰 **Budget:** {budget}
        
        **Current Weather Information:**
        {weather_info}
        
        Create a detailed plan that includes:
        
        1. **Day-by-day itinerary** with specific activities and timings
        2. **Weather-appropriate suggestions** based on the current conditions
        3. **Restaurant and dining recommendations** with price ranges
        4. **Transportation guide** (airports, local transport, routes)
        5. **Accommodation suggestions** for the budget range
        6. **Budget breakdown** with estimated costs
        7. **Cultural tips and local customs** to be aware of
        8. **Packing recommendations** based on weather and activities
        9. **Emergency information** and important contacts
        
        Make it detailed and practical for easy implementation.
        """
        
        try:
            response = self.itinerary_agent.run(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Error creating itinerary: {str(e)}"
    
    def get_destination_recommendations(self, preferences: str, season: str = "", 
                                     budget: str = "moderate", duration: str = "1 week") -> str:
        """Get destination recommendations from the advisor agent"""
        
        prompt = f"""
        Based on the following travel profile, recommend the best destinations:
        
        🎯 **Preferences:** {preferences}
        🌸 **Season:** {season}
        💰 **Budget:** {budget}
        ⏰ **Duration:** {duration}
        
        Please provide:
        1. **5 detailed destination recommendations** that match the criteria
        2. **Budget estimates** for each destination
        3. **Best timing** to visit each location
        4. **Why each destination fits** the specified preferences
        5. **Unique experiences** available at each destination
        6. **Weather considerations** for the preferred season
        
        Make each recommendation detailed with specific attractions and activities.
        """
        
        try:
            response = self.advisor_agent.run(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Error getting recommendations: {str(e)}"

def check_env_configuration():
    """Check if environment variables are properly configured"""
    print("🔍 Checking Environment Configuration...")
    print("-" * 40)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("❌ .env file not found - creating example...")
        with open('.env.example', 'w') as f:
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
            f.write("OPENWEATHER_API_KEY=your_openweather_api_key_here\n")
        print("📝 Created .env.example - copy to .env and add your keys")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Check Gemini API Key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and len(gemini_key) > 30:
        print(f"✅ GEMINI_API_KEY loaded (length: {len(gemini_key)})")
    else:
        print("❌ GEMINI_API_KEY not found or invalid")
        print("🔗 Get your API key from: https://ai.google.dev/aistudio")
        return False
    
    # Check OpenWeather API Key
    weather_key = os.getenv("OPENWEATHER_API_KEY")
    if weather_key and len(weather_key) == 32:
        print(f"✅ OPENWEATHER_API_KEY loaded (length: {len(weather_key)})")
    else:
        print("❌ OPENWEATHER_API_KEY not found or invalid (should be 32 characters)")
        print("🔗 Get your API key from: https://openweathermap.org/api")
        return False
    
    print("\n✅ Environment configuration check complete!")
    return True

def test_basic_functionality():
    """Test basic functionality with simple calls"""
    print("\n🧪 Testing Basic Functionality...")
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    
    if not all([GEMINI_API_KEY, WEATHER_API_KEY]):
        print("❌ Missing API keys")
        return False
    
    try:
        # Test weather API directly
        print("🌤️ Testing Weather API...")
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {"q": "London", "appid": WEATHER_API_KEY, "units": "metric"}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✅ Weather API working")
        else:
            print(f"❌ Weather API error: {response.status_code}")
            return False
        
        # Test Gemini model
        print("🤖 Testing Gemini Model...")
        model = Gemini(api_key=GEMINI_API_KEY, id="gemini-1.5-flash")
        
        test_agent = Agent(
            name="TestAgent",
            model=model,
            description="Simple test agent"
        )
        
        response = test_agent.run("Say hello in one sentence!")
        if response and (hasattr(response, 'content') or str(response)):
            print("✅ Gemini model working")
            print(f"📝 Response: {response.content if hasattr(response, 'content') else str(response)[:100]}...")
            return True
        else:
            print("❌ Gemini model not responding properly")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Simplified main function with better error handling"""
    
    print("🌍 Phidata Travel Scheduler - Diagnostic Mode")
    print("=" * 50)
    
    # Check environment
    if not check_env_configuration():
        return
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic tests failed. Please check your API keys and internet connection.")
        return
    
    # Initialize scheduler
    try:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
        
        scheduler = TravelScheduler(GEMINI_API_KEY, WEATHER_API_KEY)
        print("\n✅ Travel Scheduler initialized successfully!")
        
        # Simple test run
        print("\n🧪 Running simple travel recommendation test...")
        test_result = scheduler.get_destination_recommendations(
            preferences="beaches and culture",
            season="summer",
            budget="moderate"
        )
        
        if test_result and not test_result.startswith("Error"):
            print("✅ Travel scheduler working!")
            print(f"📝 Sample output: {test_result[:200]}...")
            
            # Now run interactive mode
            interactive_mode(scheduler)
        else:
            print(f"❌ Travel scheduler test failed: {test_result}")
            
    except Exception as e:
        print(f"❌ Failed to initialize scheduler: {e}")
        print("\n💡 Common solutions:")
        print("1. Update phidata: pip install --upgrade phidata")
        print("2. Check API keys in .env file")
        print("3. Verify internet connection")

def interactive_mode(scheduler):
    """Simple interactive mode"""
    print("\n🎯 Enter Interactive Mode!")
    print("Type 'quit' to exit, 'help' for commands")
    
    while True:
        try:
            user_input = input("\n👉 What would you like to do? ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("Available commands:")
                print("- 'recommend [preferences]' - Get destination recommendations")
                print("- 'plan [destination] [dates]' - Plan a trip")
                print("- 'weather [city]' - Check weather")
                print("- 'quit' - Exit")
            elif user_input.lower().startswith('recommend'):
                preferences = user_input[9:].strip() or "general travel"
                result = scheduler.get_destination_recommendations(preferences)
                print(f"\n🎯 Recommendations:\n{result}")
            elif user_input.lower().startswith('weather'):
                city = user_input[7:].strip() or "London"
                result = scheduler.get_weather_info(city)
                print(f"\n🌤️ Weather Report:\n{result}")
            elif user_input.lower().startswith('plan'):
                parts = user_input[4:].strip().split()
                destination = parts[0] if parts else "Paris"
                result = scheduler.plan_complete_trip(
                    destination=destination,
                    start_date="2025-06-01",
                    end_date="2025-06-07",
                    preferences="sightseeing and culture"
                )
                print(f"\n🗓️ Travel Plan:\n{result}")
            else:
                # General query to advisor agent
                result = scheduler.advisor_agent.run(user_input)
                response_text = result.content if hasattr(result, 'content') else str(result)
                print(f"\n🤖 Response:\n{response_text}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()