from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import time
from datetime import datetime
import logging
import os

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
    worker_id = os.getpid()
    logger.info(f"GET /ui handled by worker id: {worker_id}")
    return FileResponse('index.html')

@app.get("/")
async def read_root():
    worker_id = os.getpid()
    logger.info(f"GET / handled by worker id: {worker_id}")
    return {"message": "Hello World", "worker_id": worker_id}

@app.post("/delay")
async def delayed_response():
    worker_id = os.getpid()
    logger.info(f"POST /delay handled by worker id: {worker_id}")
    
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Starting delay at {start_time} on worker id: {worker_id}")
    
    time.sleep(3)  # This is a blocking call; consider using await asyncio.sleep(3) for async endpoints
    
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Ending delay at {end_time} on worker id: {worker_id}")
    
    response = {
        "message": "Response after 3 seconds delay",
        "start_time": start_time,
        "end_time": end_time,
        "worker_id": worker_id
    }
    logger.info(f"Sending response: {response}")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_worker:app", host="0.0.0.0", port=8005, workers=4)
