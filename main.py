import os
import subprocess
import time
import sys

def run_services():
    print("🚀 Starting Dreamline Logistics System...")
    
    # 1. Start Streamlit (Dashboard)
    # This will handle the PORT environment variable for Render's health check
    port = os.environ.get("PORT", "10000")
    print(f"📈 Starting Dashboard on port {port}...")
    
    # headles mode and fixed port
    streamlit_proc = subprocess.Popen([
        "streamlit", "run", "dashboard.py",
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])
    
    # 2. Start the Telegram Bot
    # We set SKIP_HEALTH_CHECK because Streamlit is already using the PORT
    print("🤖 Starting Telegram Bot...")
    os.environ["SKIP_HEALTH_CHECK"] = "1"
    
    try:
        # Import and run the bot's main function directly
        from bot import main as start_bot
        start_bot()
    except Exception as e:
        print(f"❌ Bot failed: {e}")
        streamlit_proc.terminate()
        sys.exit(1)

if __name__ == "__main__":
    run_services()
