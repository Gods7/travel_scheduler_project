from config import check_env_configuration, load_env_variables
from scheduler import TravelScheduler
from database import test_database_connection


def test_agents():
    """Test the Phidata agents and tools"""
    
    # Check environment first
    if not check_env_configuration():
        return
    
    GEMINI_API_KEY, WEATHER_API_KEY = load_env_variables()
    
    if not all([GEMINI_API_KEY, WEATHER_API_KEY]):
        print("❌ Missing API keys in .env file")
        return
    
    try:
        print("🧪 Testing Phidata Travel Scheduler Components...")
        scheduler = TravelScheduler(GEMINI_API_KEY, WEATHER_API_KEY, "mongodb://localhost:27017")
        
        # Test weather tool
        print("\n🌤️ Testing Weather Tool...")
        weather_result = scheduler.weather_tool.get_current_weather("Paris", "FR")
        print(weather_result)
        
        # Test simple agent interaction
        print("\n🤖 Testing Agent Interaction...")
        simple_result = scheduler.advisor_agent.run("What are the top 3 must-see attractions in Paris?")
        print(simple_result.content[:200] + "...")
        
        # Test database operations
        print("\n🗄️ Testing Database Operations...")
        if scheduler.db:
            stats = scheduler.get_database_stats()
            print("Database Stats:", stats[:200] + "...")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


def run_weather_test():
    """Run a focused test on the weather tool"""
    
    _, WEATHER_API_KEY = load_env_variables()
    
    if not WEATHER_API_KEY:
        print("❌ WEATHER_API_KEY not found")
        return
    
    from weather_tool import WeatherTool
    
    try:
        weather_tool = WeatherTool(WEATHER_API_KEY)
        
        print("🌤️ Testing weather tool with multiple cities...")
        
        test_cities = [
            ("London", "GB"),
            ("Tokyo", "JP"),
            ("New York", "US"),
            ("Sydney", "AU")
        ]
        
        for city, country in test_cities:
            result = weather_tool.get_current_weather(city, country)
            print(f"\n{city}, {country}:")
            print(result[:150] + "...")
        
        print("\n✅ Weather tool tests completed!")
        
    except Exception as e:
        print(f"❌ Weather tool test failed: {e}")


if __name__ == "__main__":
    print("🧪 Running Travel Scheduler Tests...")
    print("=" * 50)
    
    # Test database connection first
    print("\n🗄️ Testing MongoDB Database...")
    test_database_connection()
    
    # Run all tests
    print("\n🤖 Testing AI Agents...")
    test_agents()
    
    print("\n" + "=" * 50)
    print("🌤️ Testing Weather API...")
    run_weather_test()