from weather_tool import WeatherTool
from knowledge_helper import TravelKnowledgeHelper
from agents import setup_agents
from database import TravelDatabase


class TravelScheduler:
    """Main Travel Scheduler with Phidata Agents"""
    
    def __init__(self, gemini_api_key: str, weather_api_key: str, 
                 mongodb_uri: str = "mongodb://localhost:27017"):
        self.gemini_api_key = gemini_api_key
        self.weather_api_key = weather_api_key
        self.user_id = "default_user"  # In a real app, this would come from authentication
        
        # Initialize custom tools and knowledge helper
        self.weather_tool = WeatherTool(weather_api_key)
        self.travel_knowledge = TravelKnowledgeHelper()
        
        # Initialize MongoDB database
        try:
            self.db = TravelDatabase(mongodb_uri)
            print("✅ MongoDB database connected successfully")
        except Exception as e:
            print(f"⚠️ Warning: MongoDB connection failed: {e}")
            print("📝 Continuing without database persistence...")
            self.db = None
        
        # Initialize specialized agents
        self.itinerary_agent, self.advisor_agent, self.memory_agent, self.memory = setup_agents(
            gemini_api_key, self.weather_tool
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
        
        # Save trip to database
        if self.db:
            trip_data = {
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "preferences": preferences,
                "budget": budget,
                "itinerary": response.content
            }
            self.db.save_trip_history(self.user_id, trip_data)
            self.db.save_agent_memory(self.user_id, "itinerary", prompt, response.content)
        
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
        
        # Save to database
        if self.db:
            # Update user preferences
            user_prefs = {
                "preferences": preferences,
                "season": season,
                "budget": budget,
                "duration": duration
            }
            self.db.save_user_preferences(self.user_id, user_prefs)
            self.db.save_agent_memory(self.user_id, "advisor", prompt, response.content)
        
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
        
        # Save to database
        if self.db:
            self.db.save_agent_memory(self.user_id, "advisor", prompt, response.content)
        
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
        
        # Save to database
        if self.db:
            self.db.save_agent_memory(self.user_id, "itinerary", prompt, response.content)
        
        return response.content
    
    def recall_travel_history(self) -> str:
        """Get travel history and preferences from memory"""
        
        if self.db:
            # Get data from database
            trip_history = self.db.get_trip_history(self.user_id, limit=10)
            user_preferences = self.db.get_user_preferences(self.user_id)
            agent_conversations = self.db.get_agent_memory(self.user_id, limit=20)
            
            # Format the data for the agent
            history_summary = "## Your Travel History from Database:\n\n"
            
            if trip_history:
                history_summary += "### Past Trips:\n"
                for trip in trip_history:
                    history_summary += f"- **{trip.get('destination')}** ({trip.get('start_date')} to {trip.get('end_date')})\n"
                    history_summary += f"  Budget: {trip.get('budget')}, Preferences: {trip.get('preferences')}\n\n"
            
            if user_preferences:
                history_summary += "### Your Preferences:\n"
                for key, value in user_preferences.items():
                    history_summary += f"- **{key.replace('_', ' ').title()}:** {value}\n"
                history_summary += "\n"
            
            history_summary += f"### Recent Conversations: {len(agent_conversations)} interactions\n\n"
            
            prompt = f"""
            {history_summary}
            
            Based on this data from your travel history, please provide:
            
            1. **Travel Pattern Analysis:** What patterns do you see in my travel preferences?
            2. **Destination Recommendations:** Based on my history, where should I go next?
            3. **Budget Insights:** What's my typical spending pattern?
            4. **Preference Evolution:** How have my preferences changed over time?
            5. **Next Trip Suggestions:** What type of trip would be perfect for me now?
            
            Use this information to suggest my next trip!
            """
            
            response = self.memory_agent.run(prompt)
            
            # Save this interaction
            self.db.save_agent_memory(self.user_id, "memory", prompt, response.content)
            
            return response.content
        else:
            # Fallback to basic memory agent
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
        
        # Save to database
        if self.db:
            self.db.save_agent_memory(self.user_id, agent_type, message, response.content)
        
        return response.content
    
    def get_database_stats(self) -> str:
        """Get database statistics and information"""
        if not self.db:
            return "❌ Database not connected. Using in-memory storage only."
        
        try:
            stats = self.db.get_database_stats()
            
            stats_text = """
🗄️ **DATABASE STATISTICS**
========================

📊 **Collection Counts:**
- Total Users: {total_users}
- Total Trips: {total_trips}  
- Total Conversations: {total_conversations}

📁 **Collections:** {collections}

🔗 **Connection Status:** {connection_status}

💡 **Your Data:**
- Trip History: {user_trips} trips
- Saved Preferences: {has_preferences}
- Agent Conversations: {user_conversations} interactions
            """.format(
                **stats,
                user_trips=len(self.db.get_trip_history(self.user_id)),
                has_preferences="Yes" if self.db.get_user_preferences(self.user_id) else "No",
                user_conversations=len(self.db.get_agent_memory(self.user_id))
            )
            
            return stats_text
            
        except Exception as e:
            return f"❌ Error getting database stats: {e}"
    
    def search_past_trips(self, destination_query: str) -> str:
        """Search through past trips"""
        if not self.db:
            return "❌ Database not connected. Cannot search past trips."
        
        try:
            results = self.db.search_destinations(destination_query)
            
            if not results:
                return f"🔍 No trips found matching '{destination_query}'"
            
            search_text = f"🔍 **SEARCH RESULTS FOR '{destination_query.upper()}'**\n"
            search_text += "=" * 50 + "\n\n"
            
            for trip in results:
                search_text += f"📍 **{trip.get('destination')}**\n"
                search_text += f"📅 {trip.get('start_date')} to {trip.get('end_date')}\n"
                search_text += f"💰 Budget: {trip.get('budget')}\n"
                search_text += f"❤️ Preferences: {trip.get('preferences')}\n"
                search_text += f"🗓️ Created: {trip.get('created_at')}\n\n"
            
            return search_text
            
        except Exception as e:
            return f"❌ Error searching trips: {e}"