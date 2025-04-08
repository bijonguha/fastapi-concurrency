from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import asyncio  # Import asyncio for asynchronous sleep
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware to allow requests from our frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files directory
@app.get("/ui")
async def get_ui():
    return FileResponse('index.html')

@app.get("/")
async def read_root():
    logger.info("Received GET request to root endpoint")
    return {"message": "Hello World"}

@app.post("/delay")
async def delayed_response():
    logger.info("Received POST request to delay endpoint")
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Starting delay at {start_time}")
    
    # Non-blocking sleep for 3 seconds
    await asyncio.sleep(5)
    
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Ending delay at {end_time}")
    
    response = {
        "message": "Response after 3 seconds delay",
        "start_time": start_time,
        "end_time": end_time
    }
    logger.info(f"Sending response: {response}")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
