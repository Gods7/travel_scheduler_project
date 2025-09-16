# 🌍 AI Travel Scheduler

AI-powered travel planning with Gemini AI and real-time weather integration.

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add API Keys
Create `.env` file:
```env
GEMINI_API_KEY=your_gemini_key
OPENWEATHER_API_KEY=your_weather_key
```

**Get Keys:**
- [Gemini API](https://makersuite.google.com/app/apikey) (free)
- [OpenWeather API](https://openweathermap.org/api) (free)

### 3. Run Application
```bash
# Web Interface
streamlit run streamlit_travel_app.py

# Command Line
python scheduler.py
```

## ✨ Features

- 🤖 **AI Trip Planning** - Complete itineraries via Gemini AI
- 🌤️ **Weather Integration** - Real-time weather data
- 🎯 **Smart Recommendations** - Personalized suggestions
- 💡 **Travel Tips** - Expert advice and local insights
- 🖥️ **Dual Interface** - Web + CLI options

## 📋 Core Files

- `streamlit_travel_app.py` - Web interface
- `scheduler.py` - Main application logic
- `weather_tool.py` - Weather API integration
- `agents.py` - AI agents for planning
- `config.py` - Configuration management
- `requirements.txt` - Dependencies

## 🛠️ Troubleshooting

**Module errors:**
```bash
pip install phidata google-generativeai python-dotenv requests streamlit
```

**API key errors:**
- Check `.env` file exists in project root
- Verify keys are valid (no quotes needed)

**Import errors:**
```bash
# Run from project root directory
cd travel_scheduler
python scheduler.py
```

---

**Happy Travels!** ✈️🌍