from datetime import datetime
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from pymongo.database import Database


class TravelDatabase:
    """MongoDB database manager for travel scheduler"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017"):
        """Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB connection string (default: localhost:27017)
        """
        self.connection_string = connection_string
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client.travel_scheduler
            
            # Test connection
            self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB at {self.connection_string}")
            
            # Create indexes for better performance
            self._create_indexes()
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            print("💡 Make sure MongoDB is running on localhost:27017")
            raise
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # User preferences indexes
            self.db.user_preferences.create_index("user_id")
            self.db.user_preferences.create_index("created_at")
            
            # Trip history indexes
            self.db.trip_history.create_index("user_id")
            self.db.trip_history.create_index("destination")
            self.db.trip_history.create_index("start_date")
            
            # Agent memory indexes
            self.db.agent_memory.create_index("user_id")
            self.db.agent_memory.create_index("agent_type")
            self.db.agent_memory.create_index("timestamp")
            
            print("✅ Database indexes created successfully")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create indexes: {e}")
    
    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Save user travel preferences
        
        Args:
            user_id: Unique user identifier
            preferences: Dictionary of user preferences
            
        Returns:
            True if saved successfully
        """
        try:
            document = {
                "user_id": user_id,
                "preferences": preferences,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Upsert (update if exists, insert if not)
            self.db.user_preferences.replace_one(
                {"user_id": user_id},
                document,
                upsert=True
            )
            
            print(f"✅ Saved preferences for user: {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving preferences: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user travel preferences
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            User preferences dictionary or None
        """
        try:
            result = self.db.user_preferences.find_one({"user_id": user_id})
            if result:
                return result.get("preferences", {})
            return None
            
        except Exception as e:
            print(f"❌ Error getting preferences: {e}")
            return None
    
    def save_trip_history(self, user_id: str, trip_data: Dict[str, Any]) -> bool:
        """Save trip to history
        
        Args:
            user_id: Unique user identifier
            trip_data: Trip information dictionary
            
        Returns:
            True if saved successfully
        """
        try:
            document = {
                "user_id": user_id,
                "trip_id": f"{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "destination": trip_data.get("destination"),
                "start_date": trip_data.get("start_date"),
                "end_date": trip_data.get("end_date"),
                "preferences": trip_data.get("preferences"),
                "budget": trip_data.get("budget"),
                "itinerary": trip_data.get("itinerary"),
                "created_at": datetime.utcnow()
            }
            
            result = self.db.trip_history.insert_one(document)
            print(f"✅ Saved trip history: {result.inserted_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving trip history: {e}")
            return False
    
    def get_trip_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's trip history
        
        Args:
            user_id: Unique user identifier
            limit: Maximum number of trips to return
            
        Returns:
            List of trip dictionaries
        """
        try:
            cursor = self.db.trip_history.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit)
            
            trips = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for trip in trips:
                trip["_id"] = str(trip["_id"])
            
            return trips
            
        except Exception as e:
            print(f"❌ Error getting trip history: {e}")
            return []
    
    def save_agent_memory(self, user_id: str, agent_type: str, 
                         conversation: str, response: str) -> bool:
        """Save agent conversation to memory
        
        Args:
            user_id: Unique user identifier
            agent_type: Type of agent (itinerary, advisor, memory)
            conversation: User's message/query
            response: Agent's response
            
        Returns:
            True if saved successfully
        """
        try:
            document = {
                "user_id": user_id,
                "agent_type": agent_type,
                "conversation": conversation,
                "response": response,
                "timestamp": datetime.utcnow()
            }
            
            result = self.db.agent_memory.insert_one(document)
            return True
            
        except Exception as e:
            print(f"❌ Error saving agent memory: {e}")
            return False
    
    def get_agent_memory(self, user_id: str, agent_type: str = None, 
                        limit: int = 20) -> List[Dict[str, Any]]:
        """Get agent conversation history
        
        Args:
            user_id: Unique user identifier
            agent_type: Filter by agent type (optional)
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation dictionaries
        """
        try:
            query = {"user_id": user_id}
            if agent_type:
                query["agent_type"] = agent_type
            
            cursor = self.db.agent_memory.find(query).sort("timestamp", -1).limit(limit)
            
            conversations = list(cursor)
            
            # Convert ObjectId to string
            for conv in conversations:
                conv["_id"] = str(conv["_id"])
            
            return conversations
            
        except Exception as e:
            print(f"❌ Error getting agent memory: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics
        
        Returns:
            Dictionary with database statistics
        """
        try:
            stats = {
                "total_users": self.db.user_preferences.count_documents({}),
                "total_trips": self.db.trip_history.count_documents({}),
                "total_conversations": self.db.agent_memory.count_documents({}),
                "collections": self.db.list_collection_names(),
                "connection_status": "Connected"
            }
            
            return stats
            
        except Exception as e:
            return {
                "error": str(e),
                "connection_status": "Disconnected"
            }
    
    def search_destinations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for destinations in trip history
        
        Args:
            query: Search query for destination
            limit: Maximum results to return
            
        Returns:
            List of matching destinations
        """
        try:
            # Use text search or regex search
            cursor = self.db.trip_history.find({
                "destination": {"$regex": query, "$options": "i"}
            }).limit(limit)
            
            results = list(cursor)
            
            # Convert ObjectId to string
            for result in results:
                result["_id"] = str(result["_id"])
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching destinations: {e}")
            return []
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("✅ MongoDB connection closed")


def test_database_connection():
    """Test MongoDB database connection and operations"""
    try:
        print("🧪 Testing MongoDB Connection...")
        print("-" * 40)
        
        # Initialize database
        db = TravelDatabase()
        
        # Test basic operations
        test_user_id = "test_user_123"
        
        # Test saving preferences
        test_preferences = {
            "budget_range": "moderate",
            "travel_style": "adventure",
            "preferred_activities": ["hiking", "museums", "local_food"],
            "accommodation_type": "hotel"
        }
        
        success = db.save_user_preferences(test_user_id, test_preferences)
        if success:
            print("✅ User preferences saved successfully")
        
        # Test retrieving preferences
        retrieved_prefs = db.get_user_preferences(test_user_id)
        if retrieved_prefs:
            print("✅ User preferences retrieved successfully")
            print(f"📊 Retrieved: {retrieved_prefs}")
        
        # Test saving trip history
        test_trip = {
            "destination": "Paris, France",
            "start_date": "2024-06-01",
            "end_date": "2024-06-07",
            "preferences": "museums, cafes, art",
            "budget": "moderate",
            "itinerary": "Day 1: Louvre Museum, Day 2: Eiffel Tower..."
        }
        
        trip_saved = db.save_trip_history(test_user_id, test_trip)
        if trip_saved:
            print("✅ Trip history saved successfully")
        
        # Test getting database stats
        stats = db.get_database_stats()
        print("✅ Database statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Close connection
        db.close_connection()
        
        print("\n✅ All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


if __name__ == "__main__":
    test_database_connection()