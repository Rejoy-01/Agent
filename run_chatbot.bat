@echo off
echo Starting Hybrid Memory Medical Chatbot...
echo ==========================================

REM Kill any existing streamlit processes
taskkill /f /im streamlit.exe 2>nul

REM Start streamlit with headless mode
uv run streamlit run hybrid_chatbot_ui.py --server.headless true --server.port 8501 --browser.gatherUsageStats false

pause
