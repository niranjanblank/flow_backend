import uvicorn
from app.main import app  # Importing app from the inner api.py

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)