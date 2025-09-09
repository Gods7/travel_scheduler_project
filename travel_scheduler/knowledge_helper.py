from typing import List


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