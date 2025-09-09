import os
from dotenv import load_dotenv
from weather_tool import WeatherTool
from phi.model.google import Gemini
from phi.agent import Agent


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


def load_env_variables():
    """Load and return environment variables"""
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    weather_key = os.getenv("OPENWEATHER_API_KEY")
    
    return gemini_key, weather_key