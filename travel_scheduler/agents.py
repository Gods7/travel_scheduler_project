from phi.agent import Agent
from phi.model.google import Gemini
from phi.memory import AgentMemory
from weather_tool import WeatherTool


def setup_agents(gemini_api_key: str, weather_tool: WeatherTool):
    """Setup specialized travel agents with memory and tools"""
    
    # Initialize Gemini model
    model = Gemini(api_key=gemini_api_key)
    
    # Create memory for agents (file-based for simplicity)
    memory = AgentMemory(
        db_file="travel_agent_memory.db",
        create_db=True
    )
    
    # Itinerary Planning Agent
    itinerary_agent = Agent(
        name="TravelItineraryPlanner",
        model=model,
        tools=[weather_tool],
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
    advisor_agent = Agent(
        name="TravelAdvisor",
        model=model,
        tools=[weather_tool],
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
    memory_agent = Agent(
        name="TravelMemoryManager",
        model=model,
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
    
    return itinerary_agent, advisor_agent, memory_agent, memory