from config import check_env_configuration, test_api_connections, load_env_variables
from scheduler import TravelScheduler

def main():
    """Interactive Travel Scheduler (clean version)"""

    # Check environment
    if not check_env_configuration():
        print("❌ Environment configuration failed. Please fix issues.")
        return

    test_api_connections()
    GEMINI_API_KEY, WEATHER_API_KEY = load_env_variables()

    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY missing. Add it to your .env file.")
        return
    if not WEATHER_API_KEY:
        print("❌ OPENWEATHER_API_KEY missing. Add it to your .env file.")
        return

    try:
        scheduler = TravelScheduler(GEMINI_API_KEY, WEATHER_API_KEY, "mongodb://localhost:27017")
        print("✅ Travel Scheduler initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing scheduler: {e}")
        return

    while True:
        print("\nChoose an option:")
        print("1. Plan a trip")
        print("2. Destination recommendations")
        print("3. Travel tips & advice")
        print("4. Optimize itinerary")
        print("5. Travel history")
        print("6. Quick weather check")
        print("7. Chat with agent")

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            destination = input("Destination: ")
            start_date = input("Start date (YYYY-MM-DD): ")
            end_date = input("End date (YYYY-MM-DD): ")
            preferences = input("Preferences/interests: ")
            budget = input("Budget [moderate]: ") or "moderate"

            try:
                result = scheduler.plan_complete_trip(destination, start_date, end_date, preferences, budget)
                print(result)
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "2":
            preferences = input("Your interests: ")
            season = input("Preferred season: ")
            budget = input("Budget [moderate]: ") or "moderate"
            duration = input("Trip duration [1 week]: ") or "1 week"

            try:
                result = scheduler.get_destination_recommendations(preferences, season, budget, duration)
                print(result)
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "3":
            destination = input("Destination: ")
            style = input("Travel style (solo/family/luxury/backpacker): ")

            try:
                result = scheduler.get_travel_tips(destination, style)
                print(result)
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "4":
            print("Enter your current itinerary (type 'END' to finish):")
            lines = []
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)
            current_itinerary = "\n".join(lines)
            feedback = input("Feedback / changes: ")

            try:
                result = scheduler.optimize_itinerary(current_itinerary, feedback)
                print(result)
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "5":
            try:
                result = scheduler.recall_travel_history()
                print(result if result else "No travel history found.")
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "6":
            city = input("City: ")
            country = input("Country (optional): ") or None

            try:
                current = scheduler.weather_tool.get_current_weather(city, country)
                forecast = scheduler.weather_tool.get_weather_forecast(city, 3, country)
                print("Current Weather:\n", current)
                print("\n3-Day Forecast:\n", forecast)
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "7":
            agent_type = input("Choose agent (itinerary/advisor/memory): ").strip()
            message = input("Message: ")

            try:
                result = scheduler.chat_with_agent(message, agent_type)
                print(result)
            except Exception as e:
                print(f"❌ Error: {e}")

        else:
            print("❌ Invalid choice. Enter 1-7.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
