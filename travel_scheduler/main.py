from config import check_env_configuration, test_api_connections, load_env_variables
from scheduler import TravelScheduler


def main():
    """Main interactive travel scheduler with environment checking"""
    
    # First, check environment configuration
    if not check_env_configuration():
        print("\n❌ Environment configuration failed. Please fix the issues above.")
        return
    
    # Test API connections
    test_api_connections()
    
    # Load API keys
    GEMINI_API_KEY, WEATHER_API_KEY = load_env_variables()
    
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
        scheduler = TravelScheduler(GEMINI_API_KEY, WEATHER_API_KEY, "mongodb://localhost:27017")
        print("\n✅ Phidata Travel Scheduler initialized successfully!")
        print("🧠 Agent memory and knowledge systems ready!")
        print("🌤️ Weather tools connected and ready!")
        print("🗄️ MongoDB database connected and ready!")
    except Exception as e:
        print(f"\n❌ Error initializing scheduler: {e}")
        print("💡 This might be due to:")
        print("   - Invalid API keys")
        print("   - Missing dependencies (run: pip install phidata)")
        print("   - Network connectivity issues")
        print("   - MongoDB not running (start with: mongod)")
        return
    
    print("\n🌍 Welcome to Phidata AI Travel Scheduler!")
    print("🤖 Powered by intelligent agents with memory and tools")
    print("🗄️ With persistent MongoDB storage")
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
        
        choice = input("\n👉 Enter your choice (1-11): ").strip()
        
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
            print("💾 Saving trip data to database...")
            
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
            print("💾 Updating your preferences in database...")
            
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
            print("💾 Saving conversation to database...")
            
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
            print("💾 Saving optimization to database...")
            
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
            print("🗄️ Loading data from MongoDB database...")
            
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
            print("💾 Saving conversation to database...")
            
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
        

        else:
            print("❌ Invalid choice. Please enter 1-11.")
        
        input("\n⏸️  Press Enter to continue...")


if __name__ == "__main__":
    main()