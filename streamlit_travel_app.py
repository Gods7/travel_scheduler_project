import streamlit as st
from datetime import date
from travel_scheduler import TravelScheduler
import os
from dotenv import load_dotenv

# --- Load Environment ---
load_dotenv()

def load_css(file_name):
    """Load custom CSS file safely"""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.info("🎨 Custom styling not found. Using default Streamlit theme.")

# Apply custom CSS
load_css("styles.css")

# --- API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not GEMINI_API_KEY:
    st.error("🚨 GEMINI_API_KEY not found. Please set it in your .env file.")
    st.stop()

if not WEATHER_API_KEY:
    st.warning("⚠️ OPENWEATHER_API_KEY not found. Weather features will be disabled.")

# --- Initialize Scheduler ---
try:
    scheduler = TravelScheduler(GEMINI_API_KEY, WEATHER_API_KEY)
except Exception as e:
    st.error(f"❌ Failed to initialize Travel Scheduler.\n\n**Details:** {str(e)}")
    st.stop()

st.sidebar.title("🌍 Travel Scheduler")
st.sidebar.markdown("---")

menu = st.sidebar.radio("Choose an option", [
    "Plan a Trip",
    "Recommendations",
    "Travel Tips",
    "Optimize Itinerary",
    "Travel History",
    "Weather Check"
])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Tips")
st.sidebar.markdown("- Be specific with destinations")
st.sidebar.markdown("- Include your interests and preferences")
st.sidebar.markdown("- Consider your budget realistically")

# --- MAIN CONTENT ---
st.title("🌍 AI Travel Scheduler")
st.markdown("Plan your perfect trip with AI-powered recommendations!")

# --- Plan a Trip ---
if menu == "Plan a Trip":
    st.header("🗓️ Plan Your Trip")
    with st.form("trip_planning_form"):
        col1, col2 = st.columns(2)
        with col1:
            destination = st.text_input("🎯 Destination", placeholder="e.g., Paris, France")
            start_date = st.date_input("📅 Start Date", date.today())
            budget = st.selectbox("💰 Budget", ["low", "moderate", "luxury"])
        with col2:
            preferences = st.text_area("❤️ Preferences / Interests",
                                       placeholder="e.g., museums, food, adventure...")
            end_date = st.date_input("📅 End Date", date.today())

        submit_button = st.form_submit_button("🚀 Generate Itinerary", use_container_width=True)

    if submit_button:
        destination = destination.strip()
        if not destination:
            st.error("⚠️ Please enter a destination.")
        elif start_date >= end_date:
            st.error("⚠️ End date must be after start date.")
        else:
            # --- NEW: Smarter city/country detection ---
            if "," not in destination and " " not in destination:
                # Likely a single city name -> add country hint for better results
                destination_with_hint = f"{destination}, India"
                st.info(f"🌎 Detected single-word destination: **{destination}** → assuming **{destination_with_hint}**")
            else:
                destination_with_hint = destination
                st.success(f"🏙️ Detected location: **{destination_with_hint}**")

            with st.spinner("🤖 Planning your amazing trip..."):
                try:
                    itinerary = scheduler.plan_complete_trip(
                        destination_with_hint, str(start_date), str(end_date),
                        preferences, budget
                    )
                    if itinerary and isinstance(itinerary, str):
                        st.success("✅ Trip Planned Successfully!")
                        with st.expander("📋 Your Complete Itinerary", expanded=True):
                            st.markdown(itinerary)

                        st.download_button(
                            label="📄 Download Itinerary",
                            data=itinerary,
                            file_name=f"{destination.replace(', ', '_')}_itinerary.md",
                            mime="text/markdown"
                        )
                    else:
                        st.error("⚠️ Could not generate itinerary. Try rephrasing the destination or using a well-known location.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Try simplifying your request or check API keys.")

# --- Recommendations ---
elif menu == "Recommendations":
    st.header("🎯 Get Destination Recommendations")
    with st.form("recommendations_form"):
        col1, col2 = st.columns(2)
        with col1:
            prefs = st.text_area("🌟 Your Interests", placeholder="e.g., hiking, culture...")
            budget = st.selectbox("💰 Budget", ["budget", "moderate", "luxury"])
        with col2:
            season = st.text_input("🌤️ Preferred Season", placeholder="e.g., summer, winter...")
            duration = st.text_input("⏰ Trip Duration", "1 week")

        submit_button = st.form_submit_button("🔍 Get Recommendations", use_container_width=True)

    if submit_button:
        if not prefs.strip():
            st.error("⚠️ Please describe your interests.")
        else:
            with st.spinner("🔍 Finding perfect destinations..."):
                try:
                    recommendations = scheduler.get_destination_recommendations(
                        prefs, season, budget, duration
                    )
                    st.success("✅ Recommendations Ready!")
                    st.markdown(recommendations)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# --- Travel Tips ---
elif menu == "Travel Tips":
    st.header("💡 Travel Tips & Advice")
    with st.form("travel_tips_form"):
        col1, col2 = st.columns(2)
        with col1:
            dest = st.text_input("🌍 Destination", placeholder="e.g., Tokyo, Japan")
        with col2:
            style = st.selectbox("🎒 Travel Style",
                                 ["general", "solo", "family", "luxury", "backpacker"])

        submit_button = st.form_submit_button("💡 Get Travel Tips", use_container_width=True)

    if submit_button:
        if not dest.strip():
            st.error("⚠️ Please enter a destination.")
        else:
            with st.spinner("📚 Gathering expert travel advice..."):
                try:
                    tips = scheduler.get_travel_tips(dest, style)
                    st.success("✅ Tips Ready!")
                    st.markdown(tips)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# --- Optimize Itinerary ---
elif menu == "Optimize Itinerary":
    st.header("⚡ Optimize Existing Itinerary")
    with st.form("optimize_form"):
        itinerary_input = st.text_area("📋 Enter Your Current Itinerary", height=200)
        feedback = st.text_area("💭 Changes or Feedback", placeholder="Add notes for AI to improve...")
        submit_button = st.form_submit_button("⚡ Optimize Itinerary", use_container_width=True)

    if submit_button:
        if not itinerary_input.strip():
            st.error("⚠️ Please enter your current itinerary.")
        else:
            with st.spinner("🔧 Optimizing your itinerary..."):
                try:
                    optimized = scheduler.optimize_itinerary(itinerary_input, feedback)
                    st.success("✅ Optimized Successfully!")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📝 Original Itinerary")
                        st.text_area("Original", value=itinerary_input, height=300, disabled=True)
                    with col2:
                        st.subheader("⚡ Optimized Version")
                        st.markdown(optimized)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# --- Travel History ---
elif menu == "Travel History":
    st.header("🧠 Your Travel History")
    if st.button("📚 Show Travel History", use_container_width=True):
        try:
            history = scheduler.recall_travel_history()
            st.markdown(history if history else "No travel history found.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# --- Weather Check ---
elif menu == "Weather Check":
    st.header("🌤️ Weather Information")
    with st.form("weather_form"):
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("🏙️ City", placeholder="e.g., London")
        with col2:
            country = st.text_input("🌍 Country (optional)", placeholder="e.g., UK")

        submit_button = st.form_submit_button("🌤️ Check Weather", use_container_width=True)

    if submit_button:
        if not city.strip():
            st.error("⚠️ Please enter a city.")
        elif not hasattr(scheduler, "weather_tool") or scheduler.weather_tool is None:
            st.warning("⚠️ Weather service unavailable. Please check API key.")
        else:
            with st.spinner("🌤️ Fetching weather data..."):
                try:
                    current_weather = scheduler.weather_tool.get_current_weather(city, country)
                    forecast = scheduler.weather_tool.get_weather_forecast(city, 3, country)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("🌡️ Current Weather")
                        st.markdown(current_weather)
                    with col2:
                        st.subheader("📅 3-Day Forecast")
                        st.markdown(forecast)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🌍 AI Travel Scheduler - Plan smarter, travel better!</p>
        <p><small>Powered by Google Gemini AI</small></p>
    </div>
    """,
    unsafe_allow_html=True
)
