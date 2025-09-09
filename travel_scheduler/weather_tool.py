import requests
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