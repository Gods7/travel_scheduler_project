import streamlit as st
from datetime import date
from scheduler import TravelScheduler
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

# --- Sidebar ---
st.sidebar.title("🌍 Travel Scheduler")
menu = st.sidebar.radio("📋 Choose an option", [
    "🗓️ Plan a Trip",
    "🎯 Recommendations",
    "💡 Travel Tips",
    "⚡ Optimize Itinerary",
    "🧠 Travel History",
    "🌤️ Weather Check",
    "💬 Chat with Agent"
])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Tips")
st.sidebar.markdown("- Be specific with destinations")
st.sidebar.markdown("- Include your interests")
st.sidebar.markdown("- Match your budget realistically")

# --- MAIN CONTENT ---
st.title("🌍 AI Travel Scheduler")
st.markdown("✨ Plan smarter, travel better with AI-powered itineraries!")

# --- Plan a Trip ---
if menu.startswith("🗓️"):
    st.header("🗓️ Plan Your Trip")
    with st.form("trip_form"):
        col1, col2 = st.columns(2)
        with col1:
            destination = st.text_input("🎯 Destination", placeholder="e.g., Paris, France")
            start_date = st.date_input("📅 Start Date", date.today())
            budget = st.selectbox("💰 Budget", ["low", "moderate", "luxury"])
        with col2:
            preferences = st.text_area("❤️ Preferences / Interests",
                                       placeholder="e.g., museums, food, adventure...")
            end_date = st.date_input("📅 End Date", date.today())

        submit_trip = st.form_submit_button("🚀 Generate Itinerary", use_container_width=True)

    if submit_trip:
        destination = destination.strip()
        if not destination:
            st.error("⚠️ Please enter a destination.")
        elif start_date > end_date:
            st.error("⚠️ End date must be after start date.")
        else:
            # Detect single city name → add country hint
            if "," not in destination and " " not in destination:
                destination_hint = f"{destination}, India"
                st.info(f"🌎 Detected single-word destination: **{destination}** → assuming **{destination_hint}**")
            else:
                destination_hint = destination
                st.success(f"🏙️ Destination set: **{destination_hint}**")

            with st.spinner("🤖 Planning your amazing trip..."):
                try:
                    itinerary = scheduler.plan_complete_trip(
                        destination_hint, str(start_date), str(end_date), preferences, budget
                    )
                    if itinerary:
                        st.success("✅ Trip Planned Successfully!")
                        with st.expander("📋 Your Complete Itinerary", expanded=True):
                            st.markdown(itinerary, unsafe_allow_html=True)

                        st.download_button(
                            "📄 Download Itinerary",
                            data=itinerary,
                            file_name=f"{destination.replace(', ', '_')}_itinerary.md",
                            mime="text/markdown"
                        )
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# --- Recommendations ---
elif menu.startswith("🎯"):
    st.header("🎯 Destination Recommendations")
    with st.form("reco_form"):
        col1, col2 = st.columns(2)
        with col1:
            prefs = st.text_area("🌟 Your Interests", placeholder="e.g., hiking, culture...")
            budget = st.selectbox("💰 Budget", ["budget", "moderate", "luxury"])
        with col2:
            season = st.text_input("🌤️ Preferred Season", placeholder="e.g., summer, winter...")
            duration = st.text_input("⏰ Trip Duration", "1 week")

        submit_reco = st.form_submit_button("🔍 Get Recommendations", use_container_width=True)

    if submit_reco:
        if not prefs.strip():
            st.error("⚠️ Please describe your interests.")
        else:
            with st.spinner("🔍 Finding perfect destinations..."):
                try:
                    recos = scheduler.get_destination_recommendations(prefs, season, budget, duration)
                    st.success("✅ Recommendations Ready!")
                    st.markdown(recos, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# --- Travel Tips ---
elif menu.startswith("💡"):
    st.header("💡 Travel Tips & Advice")
    with st.form("tips_form"):
        col1, col2 = st.columns(2)
        with col1:
            dest = st.text_input("🌍 Destination", placeholder="e.g., Tokyo, Japan")
        with col2:
            style = st.selectbox("🎒 Travel Style", ["general", "solo", "family", "luxury", "backpacker"])

        submit_tips = st.form_submit_button("💡 Get Tips", use_container_width=True)

    if submit_tips:
        if not dest.strip():
            st.error("⚠️ Please enter a destination.")
        else:
            with st.spinner("📚 Gathering expert advice..."):
                try:
                    tips = scheduler.get_travel_tips(dest, style)
                    st.success("✅ Tips Ready!")
                    st.markdown(tips, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# --- Optimize Itinerary ---
elif menu.startswith("⚡"):
    st.header("⚡ Optimize Existing Itinerary")
    with st.form("opt_form"):
        itinerary_text = st.text_area("📋 Your Current Itinerary", height=200)
        feedback = st.text_area("💭 Feedback / Changes")
        submit_opt = st.form_submit_button("⚡ Optimize", use_container_width=True)

    if submit_opt:
        if not itinerary_text.strip():
            st.error("⚠️ Please enter your current itinerary.")
        else:
            with st.spinner("🔧 Optimizing your itinerary..."):
                try:
                    optimized = scheduler.optimize_itinerary(itinerary_text, feedback)
                    st.success("✅ Optimization Complete!")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📝 Original")
                        st.text_area("Original", itinerary_text, height=300, disabled=True)
                    with col2:
                        st.subheader("⚡ Optimized")
                        st.markdown(optimized, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# --- Travel History ---
elif menu.startswith("🧠"):
    st.header("🧠 Your Travel History")
    if st.button("📚 Show History", use_container_width=True):
        with st.spinner("🔍 Loading history..."):
            try:
                history = scheduler.recall_travel_history()
                st.markdown(history if history else "No history found.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# --- Weather Check ---
elif menu.startswith("🌤️"):
    st.header("🌤️ Weather Information")
    with st.form("weather_form"):
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("🏙️ City", placeholder="e.g., London")
        with col2:
            country = st.text_input("🌍 Country (optional)", placeholder="e.g., UK")
        submit_weather = st.form_submit_button("🌤️ Check Weather", use_container_width=True)

    if submit_weather:
        if not city.strip():
            st.error("⚠️ Please enter a city.")
        elif not WEATHER_API_KEY:
            st.warning("⚠️ Weather service unavailable. Please check API key.")
        else:
            with st.spinner("🌤️ Fetching weather..."):
                try:
                    current = scheduler.weather_tool.get_current_weather(city, country)
                    forecast = scheduler.weather_tool.get_weather_forecast(city, 3, country)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("🌡️ Current")
                        st.markdown(current, unsafe_allow_html=True)
                    with col2:
                        st.subheader("📅 3-Day Forecast")
                        st.markdown(forecast, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# --- Chat with Agent ---
elif menu.startswith("💬"):
    st.header("💬 Chat with Travel Agent")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Chat input (press Enter works here)
    user_input = st.chat_input("Ask me anything about your trip:")

    if user_input:
        # Save user message
        st.session_state.chat_history.append(("user", user_input))
        with st.spinner("🤖 Thinking..."):
            try:
                response = scheduler.chat_with_agent(user_input)
                # Save agent response
                st.session_state.chat_history.append(("agent", response))
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # Display chat history
    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"🧑 **You:** {msg}")
        else:
            st.markdown(f"🤖 **Agent:** {msg}")
