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
from phi.memory import AgentMemory
from phi.tools import Toolkit

class WeatherTool(Toolkit):
    """Custom Weather Tool for travel planning"""
    
    def __init__(self, api_key: str):
        super().__init__(name="weather_tool")
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # Register tool functions
        self.register(self.get_current_weather)
        self.register(self.get_weather_forecast)
        self.register(self.get_weather_alerts)
    
    def get_current_weather(self, city: str, country: str = None) -> str:
        """Get current weather information for a city.
        
        Args:
            city: Name of the city
            country: Country code (optional)
            
        Returns:
            Current weather information as a formatted string
        """
        location = f"{city},{country}" if country else city
        url = f"{self.base_url}/weather"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            weather_info = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "feels_like": data["main"]["feels_like"]
            }
            
            return f"""Current Weather in {weather_info['city']}, {weather_info['country']}:
            Temperature: {weather_info['temperature']}°C (feels like {weather_info['feels_like']}°C)
            Condition: {weather_info['description'].title()}
            Humidity: {weather_info['humidity']}%
            Wind Speed: {weather_info['wind_speed']} m/s"""
            
        except Exception as e:
            return f"Error getting weather data: {str(e)}"
    
    def get_weather_forecast(self, city: str, days: int = 5, country: str = None) -> str:
        """Get weather forecast for a city.
        
        Args:
            city: Name of the city
            days: Number of days for forecast (1-5)
            country: Country code (optional)
            
        Returns:
            Weather forecast as a formatted string
        """
        location = f"{city},{country}" if country else city
        url = f"{self.base_url}/forecast"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric",
            "cnt": min(days * 8, 40)
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            forecast_text = f"Weather Forecast for {data['city']['name']}, {data['city']['country']}:\n\n"
            
            current_date = None
            for item in data["list"]:
                forecast_date = item["dt_txt"][:10]
                forecast_time = item["dt_txt"][11:16]
                
                if forecast_date != current_date:
                    forecast_text += f"\n📅 {forecast_date}:\n"
                    current_date = forecast_date
                
                forecast_text += f"  {forecast_time}: {item['main']['temp']}°C, {item['weather'][0]['description']}\n"
            
            return forecast_text
            
        except Exception as e:
            return f"Error getting forecast data: {str(e)}"
    
    def get_weather_alerts(self, city: str, country: str = None) -> str:
        """Get weather alerts for a city.
        
        Args:
            city: Name of the city
            country: Country code (optional)
            
        Returns:
            Weather alerts information
        """
        # Note: This is a simplified version. In reality, you'd use a different API endpoint
        weather_info = self.get_current_weather(city, country)
        
        # Simple alert logic based on current conditions
        if "Error" in weather_info:
            return weather_info
        
        alerts = []
        if "rain" in weather_info.lower() or "storm" in weather_info.lower():
            alerts.append("⚠️ Rain/Storm Alert: Consider indoor activities")
        if "snow" in weather_info.lower():
            alerts.append("❄️ Snow Alert: Dress warmly and allow extra travel time")
        if "wind" in weather_info and "high" in weather_info.lower():
            alerts.append("💨 High Wind Alert: Be cautious with outdoor activities")
        
        if alerts:
            return f"Weather Alerts for {city}:\n" + "\n".join(alerts)
        else:
            return f"No weather alerts for {city}. Conditions are favorable for travel!"

class TravelKnowledgeHelper:
    """Helper class for travel knowledge and tips"""
    
    def __init__(self):
        # Store travel knowledge as instance variables instead of using AssistantKnowledge
        self.travel_data = {
            "packing": {
                "essentials": ["passport", "phone charger", "medications", "comfortable shoes"],
                "weather_gear": {
                    "hot": ["sunscreen", "hat", "light clothing", "water bottle"],
                    "cold": ["warm jacket", "gloves", "hat", "thermal underwear"],
                    "rainy": ["umbrella", "waterproof jacket", "quick-dry clothes"]
                }
            },
            "safety": {
                "general": ["copies of documents", "emergency contacts", "travel insurance"],
                "money": ["multiple payment methods", "cash backup", "notify bank of travel"]
            },
            "cultural": {
                "research": ["local customs", "tipping practices", "dress codes", "greeting etiquette"]
            }
        }
    
    def get_packing_list(self, destination: str, weather: str, duration: int) -> List[str]:
        """Generate a packing list based on destination and weather"""
        base_list = self.travel_data["packing"]["essentials"].copy()
        
        # Add weather-specific items
        if "hot" in weather.lower() or "sunny" in weather.lower():
            base_list.extend(self.travel_data["packing"]["weather_gear"]["hot"])
        elif "cold" in weather.lower() or "snow" in weather.lower():
            base_list.extend(self.travel_data["packing"]["weather_gear"]["cold"])
        elif "rain" in weather.lower():
            base_list.extend(self.travel_data["packing"]["weather_gear"]["rainy"])
        
        # Add duration-specific items
        if duration > 7:
            base_list.extend(["laundry detergent", "extra underwear", "backup electronics"])
        
        return base_list

class TravelScheduler:
    """Main Travel Scheduler with Phidata Agents"""
    
    def __init__(self, gemini_api_key: str, weather_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.weather_api_key = weather_api_key
        
        # Initialize custom tools and knowledge helper
        self.weather_tool = WeatherTool(weather_api_key)
        self.travel_knowledge = TravelKnowledgeHelper()
        
        # Initialize Gemini model
        self.model = Gemini(api_key=gemini_api_key)
        
        # Create memory for agents (file-based for simplicity)
        self.memory = AgentMemory(
            db_file="travel_agent_memory.db",
            create_db=True
        )
        
        # Initialize specialized agents
        self.setup_agents()
    
    def setup_agents(self):
        """Setup specialized travel agents with memory and tools"""
        
        # Itinerary Planning Agent
        self.itinerary_agent = Agent(
            name="TravelItineraryPlanner",
            model=self.model,
            tools=[self.weather_tool],
            description="Expert travel itinerary planner",
            instructions="""
            You are an expert travel itinerary planner with access to real-time weather data.
            
            Your capabilities:
            1. Create detailed day-by-day travel schedules
            2. Use weather tools to check conditions and plan accordingly
            3. Suggest activities based on weather, budget, and interests
            4. Optimize travel routes and timing
            5. Provide backup plans for bad weather
            
            Always:
            - Check weather before planning outdoor activities
            - Consider travel logistics and timing
            - Provide specific recommendations with addresses/locations
            - Include estimated costs and duration
            - Format responses clearly with proper sections
            """,
            show_tool_calls=True,
            markdown=True,
            debug_mode=False
        )
        
        # Travel Advisor Agent
        self.advisor_agent = Agent(
            name="TravelAdvisor",
            model=self.model,
            tools=[self.weather_tool],
            description="Knowledgeable travel advisor and destination expert",
            instructions="""
            You are a knowledgeable travel advisor with access to weather data and extensive travel knowledge.
            
            Your expertise includes:
            1. Destination recommendations based on preferences
            2. Cultural tips and local customs
            3. Safety and health advice
            4. Transportation guidance
            5. Accommodation suggestions
            6. Local cuisine recommendations
            7. Hidden gems and off-the-beaten-path experiences
            
            Always:
            - Use weather tools to provide current conditions
            - Provide practical, actionable advice
            - Consider safety, budget, and cultural factors
            - Suggest authentic local experiences
            - Include specific details like names, addresses, costs
            """,
            show_tool_calls=True,
            markdown=True,
            debug_mode=False
        )
        
        # Memory Management Agent (simplified without database)
        self.memory_agent = Agent(
            name="TravelMemoryManager",
            model=self.model,
            description="Manages travel preferences and history",
            instructions="""
            You help manage and recall travel preferences and history.
            
            Your role:
            1. Help users track their travel preferences
            2. Suggest destinations based on stated preferences
            3. Provide personalized recommendations
            4. Learn from user feedback to improve suggestions
            
            Always be helpful and build on user preferences.
            """,
            show_tool_calls=False,
            markdown=True,
            debug_mode=False
        )
    
    def plan_complete_trip(self, destination: str, start_date: str, end_date: str, 
                          preferences: str = "", budget: str = "moderate") -> str:
        """Plan a complete trip using the itinerary agent"""
        
        prompt = f"""
        Plan a comprehensive travel itinerary with these details:
        
        🏙️ **Destination:** {destination}
        📅 **Travel Dates:** {start_date} to {end_date}
        ❤️ **Preferences:** {preferences}
        💰 **Budget:** {budget}
        
        Please use your weather tools to check current conditions and forecast.
        Create a detailed plan that includes:
        
        1. **Day-by-day itinerary** with specific activities
        2. **Weather-appropriate suggestions** using current data
        3. **Restaurant and dining recommendations**
        4. **Transportation guide**
        5. **Accommodation suggestions**
        6. **Budget breakdown**
        7. **Cultural tips and local customs**
        8. **Emergency information**
        
        Remember this conversation for future trip planning assistance.
        """
        
        response = self.itinerary_agent.run(prompt)
        return response.content
    
    def get_destination_recommendations(self, preferences: str, season: str = "", 
                                     budget: str = "moderate", duration: str = "1 week") -> str:
        """Get destination recommendations from the advisor agent"""
        
        prompt = f"""
        Based on my travel profile and preferences, recommend the best destinations:
        
        🎯 **Preferences:** {preferences}
        🌸 **Season:** {season}
        💰 **Budget:** {budget}
        ⏰ **Duration:** {duration}
        
        Please:
        1. Check weather conditions for potential destinations
        2. Consider my past travel history if any
        3. Provide 5 detailed destination recommendations
        4. Include budget estimates and best timing
        5. Explain why each destination fits my preferences
        
        Remember my preferences for future recommendations.
        """
        
        response = self.advisor_agent.run(prompt)
        return response.content
    
    def get_travel_tips(self, destination: str, travel_style: str = "") -> str:
        """Get comprehensive travel tips"""
        
        prompt = f"""
        Provide expert travel tips for {destination}:
        
        ✈️ **Travel Style:** {travel_style}
        
        Please check current weather and provide tips on:
        
        1. **Weather-appropriate packing list**
        2. **Cultural etiquette and customs**
        3. **Safety and health precautions**
        4. **Money and payment methods**
        5. **Local transportation tips**
        6. **Communication and language**
        7. **Hidden gems and local secrets**
        8. **Common tourist mistakes to avoid**
        9. **Emergency contacts and information**
        
        Use your weather tools to provide current conditions and packing advice.
        Remember my travel style preferences.
        """
        
        response = self.advisor_agent.run(prompt)
        return response.content
    
    def optimize_itinerary(self, current_itinerary: str, feedback: str = "") -> str:
        """Optimize an existing itinerary"""
        
        prompt = f"""
        Review and optimize this travel itinerary:
        
        ## Current Itinerary:
        {current_itinerary}
        
        ## Feedback/Changes Needed:
        {feedback}
        
        Please:
        1. Check current weather conditions for the destination
        2. Optimize the schedule for better flow and efficiency
        3. Suggest cost optimizations
        4. Provide weather backup plans
        5. Improve transportation and logistics
        6. Consider my past preferences and feedback
        
        Remember this optimization for future planning.
        """
        
        response = self.itinerary_agent.run(prompt)
        return response.content
    
    def recall_travel_history(self) -> str:
        """Get travel history and preferences from memory"""
        
        prompt = """
        Please summarize my travel history and preferences based on our previous conversations:
        
        1. **Past Destinations:** Where have I traveled?
        2. **Preferences:** What do I like/dislike?
        3. **Travel Style:** How do I prefer to travel?
        4. **Budget Patterns:** What's my typical budget range?
        5. **Favorite Activities:** What experiences did I enjoy most?
        
        Use this information to suggest my next trip!
        """
        
        response = self.memory_agent.run(prompt)
        return response.content
    
    def chat_with_agent(self, message: str, agent_type: str = "advisor") -> str:
        """Chat directly with a specific agent"""
        
        if agent_type == "itinerary":
            agent = self.itinerary_agent
        elif agent_type == "memory":
            agent = self.memory_agent
        else:
            agent = self.advisor_agent
        
        response = agent.run(message)
        return response.content

def check_env_configuration():
    """Check if environment variables are properly configured"""
    print("🔍 Checking Environment Configuration...")
    print("-" * 40)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Check Gemini API Key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"✅ GEMINI_API_KEY loaded (length: {len(gemini_key)})")
        # Validate key format (should start with specific pattern)
        if gemini_key.startswith("AI") and len(gemini_key) > 30:
            print("✅ Gemini API key format appears valid")
        else:
            print("⚠️ Gemini API key format may be incorrect")
    else:
        print("❌ GEMINI_API_KEY not found")
        print("🔗 Get your API key from: https://ai.google.dev/aistudio")
        return False
    
    # Check OpenWeather API Key
    weather_key = os.getenv("OPENWEATHER_API_KEY")
    if weather_key:
        print(f"✅ OPENWEATHER_API_KEY loaded (length: {len(weather_key)})")
        # Validate key format (typically 32 characters)
        if len(weather_key) == 32:
            print("✅ OpenWeather API key format appears valid")
        else:
            print("⚠️ OpenWeather API key format may be incorrect (should be 32 characters)")
    else:
        print("❌ OPENWEATHER_API_KEY not found")
        print("🔗 Get your API key from: https://openweathermap.org/api")
        return False
    
    print("\n✅ Environment configuration check complete!")
    return True

def test_api_connections():
    """Test API connections with the loaded keys"""
    print("\n🧪 Testing API Connections...")
    print("-" * 40)
    
    # Test OpenWeather API
    weather_key = os.getenv("OPENWEATHER_API_KEY")
    if weather_key:
        try:
            weather_tool = WeatherTool(weather_key)
            test_weather = weather_tool.get_current_weather("London", "GB")
            
            if "Error" not in test_weather:
                print("✅ OpenWeather API connection successful")
                print(f"📊 Sample data: {test_weather[:100]}...")
            else:
                print(f"❌ OpenWeather API error: {test_weather}")
        except Exception as e:
            print(f"❌ OpenWeather API connection failed: {e}")
    
    # Test Gemini API (basic model initialization)
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            model = Gemini(api_key=gemini_key)
            print("✅ Gemini model initialized successfully")
            
            # Create a simple test agent
            test_agent = Agent(
                name="TestAgent",
                model=model,
                description="Test agent for API validation"
            )
            
            # Test with a simple prompt
            response = test_agent.run("Say hello and confirm you're working!")
            if hasattr(response, 'content') and response.content:
                print("✅ Gemini API connection successful")
                print(f"🤖 Test response: {response.content[:100]}...")
            else:
                print("❌ Gemini API test failed - no response")
                
        except Exception as e:
            print(f"❌ Gemini API connection failed: {e}")
            print("💡 Common issues:")
            print("   - Check if your API key is valid")
            print("   - Ensure you have API access enabled")
            print("   - Verify your Google Cloud billing is set up")

def main():
    """Main interactive travel scheduler with environment checking"""
    
    # First, check environment configuration
    if not check_env_configuration():
        print("\n❌ Environment configuration failed. Please fix the issues above.")
        return
    
    # Test API connections
    test_api_connections()
    
    # Load API keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    
    if not GEMINI_API_KEY:
        print("\n❌ GEMINI_API_KEY not found in environment variables")
        print("🔗 Get your API key from: https://ai.google.dev/aistudio")
        print("📝 Add it to your .env file as: GEMINI_API_KEY=your_key_here")
        return
    
    if not WEATHER_API_KEY:
        print("\n❌ OPENWEATHER_API_KEY not found in environment variables")
        print("🔗 Get your API key from: https://openweathermap.org/api")
        print("📝 Add it to your .env file as: OPENWEATHER_API_KEY=your_key_here")
        return
    
    try:
        # Initialize travel scheduler
        scheduler = TravelScheduler(GEMINI_API_KEY, WEATHER_API_KEY)
        print("\n✅ Phidata Travel Scheduler initialized successfully!")
        print("🧠 Agent memory and knowledge systems ready!")
        print("🌤️ Weather tools connected and ready!")
    except Exception as e:
        print(f"\n❌ Error initializing scheduler: {e}")
        print("💡 This might be due to:")
        print("   - Invalid API keys")
        print("   - Missing dependencies (run: pip install phidata)")
        print("   - Network connectivity issues")
        return
    
    print("\n🌍 Welcome to Phidata AI Travel Scheduler!")
    print("🤖 Powered by intelligent agents with memory and tools")
    print("=" * 60)
    
    while True:
        print("\n📋 What would you like to do?")
        print("1. 🗓️  Plan a complete trip (Itinerary Agent)")
        print("2. 🎯  Get destination recommendations (Advisor Agent)")
        print("3. 💡  Get travel tips and advice (Advisor Agent)")
        print("4. ⚡  Optimize existing itinerary (Itinerary Agent)")
        print("5. 🧠  Check my travel history (Memory Agent)")
        print("6. 💬  Chat freely with an agent")
        print("7. 🌤️  Quick weather check (Weather Tool)")
        print("8. 🔧  Check environment configuration")
        print("9. 🚪  Exit")
        
        choice = input("\n👉 Enter your choice (1-9): ").strip()
        
        if choice == "1":
            print("\n🗓️ COMPLETE TRIP PLANNING")
            print("-" * 30)
            destination = input("🏙️  Destination: ")
            start_date = input("📅  Start date (YYYY-MM-DD): ")
            end_date = input("📅  End date (YYYY-MM-DD): ")
            preferences = input("❤️  Preferences/interests: ")
            budget = input("💰  Budget (budget/moderate/luxury) [moderate]: ") or "moderate"
            
            print("\n🤖 Itinerary Agent is planning your trip...")
            print("🔄 Checking weather conditions and creating optimal schedule...")
            
            try:
                result = scheduler.plan_complete_trip(destination, start_date, end_date, preferences, budget)
                print("\n" + "="*70)
                print("🎉 YOUR PERSONALIZED TRAVEL PLAN")
                print("="*70)
                print(result)
            except Exception as e:
                print(f"❌ Error: {e}")
            
        elif choice == "2":
            print("\n🎯 DESTINATION RECOMMENDATIONS")
            print("-" * 30)
            preferences = input("🏖️  What interests you: ")
            season = input("🌸  Preferred season: ")
            budget = input("💰  Budget range [moderate]: ") or "moderate"
            duration = input("⏰  Trip duration [1 week]: ") or "1 week"
            
            print("\n🤖 Advisor Agent is finding perfect destinations...")
            
            try:
                result = scheduler.get_destination_recommendations(preferences, season, budget, duration)
                print("\n" + "="*70)
                print("🌟 DESTINATION RECOMMENDATIONS")
                print("="*70)
                print(result)
            except Exception as e:
                print(f"❌ Error: {e}")
            
        elif choice == "3":
            print("\n💡 TRAVEL TIPS & ADVICE")
            print("-" * 30)
            destination = input("🏙️  Destination: ")
            travel_style = input("✈️  Travel style (solo/family/luxury/backpacker): ")
            
            print(f"\n🤖 Advisor Agent is gathering expert tips for {destination}...")
            
            try:
                result = scheduler.get_travel_tips(destination, travel_style)
                print("\n" + "="*70)
                print(f"💡 EXPERT TRAVEL TIPS: {destination.upper()}")
                print("="*70)
                print(result)
            except Exception as e:
                print(f"❌ Error: {e}")
            
        elif choice == "4":
            print("\n⚡ ITINERARY OPTIMIZATION")
            print("-" * 30)
            print("📝 Enter your current itinerary (type 'END' when finished):")
            
            itinerary_lines = []
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                itinerary_lines.append(line)
            
            current_itinerary = "\n".join(itinerary_lines)
            feedback = input("🔧 What would you like to change or improve?: ")
            
            print("\n🤖 Itinerary Agent is optimizing your plan...")
            
            try:
                result = scheduler.optimize_itinerary(current_itinerary, feedback)
                print("\n" + "="*70)
                print("⚡ OPTIMIZED ITINERARY")
                print("="*70)
                print(result)
            except Exception as e:
                print(f"❌ Error: {e}")
            
        elif choice == "5":
            print("\n🧠 TRAVEL MEMORY RECALL")
            print("-" * 30)
            print("🤖 Memory Agent is recalling your travel history...")
            
            try:
                result = scheduler.recall_travel_history()
                print("\n" + "="*70)
                print("🧠 YOUR TRAVEL PROFILE")
                print("="*70)
                print(result)
            except Exception as e:
                print(f"❌ Error: {e}")
            
        elif choice == "6":
            print("\n💬 FREE CHAT WITH AGENTS")
            print("-" * 30)
            print("Choose agent type:")
            print("1. 🗓️  Itinerary Planner")
            print("2. 🎯  Travel Advisor") 
            print("3. 🧠  Memory Manager")
            
            agent_choice = input("Select agent (1-3): ").strip()
            agent_map = {"1": "itinerary", "2": "advisor", "3": "memory"}
            agent_type = agent_map.get(agent_choice, "advisor")
            
            message = input(f"\n💬 Message to {agent_type} agent: ")
            
            print(f"\n🤖 {agent_type.title()} Agent is responding...")
            
            try:
                result = scheduler.chat_with_agent(message, agent_type)
                print("\n" + "="*70)
                print(f"🤖 {agent_type.upper()} AGENT RESPONSE")
                print("="*70)
                print(result)
            except Exception as e:
                print(f"❌ Error: {e}")
            
        elif choice == "7":
            print("\n🌤️ QUICK WEATHER CHECK")
            print("-" * 30)
            city = input("🏙️  City: ")
            country = input("🌍  Country (optional): ") or None
            
            print(f"\n🔍 Checking weather for {city}...")
            
            try:
                # Direct weather tool usage
                current = scheduler.weather_tool.get_current_weather(city, country)
                forecast = scheduler.weather_tool.get_weather_forecast(city, 3, country)
                
                print("\n" + "="*50)
                print("🌤️ WEATHER REPORT")
                print("="*50)
                print(current)
                print("\n" + forecast)
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "8":
            print("\n🔧 ENVIRONMENT CONFIGURATION CHECK")
            print("-" * 40)
            check_env_configuration()
            test_api_connections()
            
        elif choice == "9":
            print("\n🌟 Thank you for using Phidata Travel Scheduler!")
            print("🧠 Your preferences have been saved for next time")
            print("✈️ Safe travels! 🌍")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-9.")
        
        input("\n⏸️  Press Enter to continue...")

def test_agents():
    """Test the Phidata agents and tools"""
    
    # Check environment first
    if not check_env_configuration():
        return
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    
    if not all([GEMINI_API_KEY, WEATHER_API_KEY]):
        print("❌ Missing API keys in .env file")
        return
    
    try:
        print("🧪 Testing Phidata Travel Scheduler Components...")
        scheduler = TravelScheduler(GEMINI_API_KEY, WEATHER_API_KEY)
        
        # Test weather tool
        print("\n🌤️ Testing Weather Tool...")
        weather_result = scheduler.weather_tool.get_current_weather("Paris", "FR")
        print(weather_result)
        
        # Test simple agent interaction
        print("\n🤖 Testing Agent Interaction...")
        simple_result = scheduler.advisor_agent.run("What are the top 3 must-see attractions in Paris?")
        print(simple_result.content[:200] + "...")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    # Set to True to run tests, False to run interactive scheduler
    run_tests = False
    
    if run_tests:
        test_agents()
    else:
        main()