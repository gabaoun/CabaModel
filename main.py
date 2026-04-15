import uvicorn
import os
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

def start_api():
    """Starts the FastAPI server."""
    print("Starting CabaModel API...")
    uvicorn.run("src.cabamodel.infrastructure.api:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    # Ensure API Key is configured before starting
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not found in .env file")
        print("Please configure your key before running the API.")
    else:
        start_api()
