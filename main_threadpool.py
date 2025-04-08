from fastapi.concurrency import run_in_threadpool
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

async def blocking_sleep():
    time.sleep(3)  # This is the blocking call
    return

@app.post("/delay")
async def delayed_response_threadpool():
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Starting delay at {start_time}")
    
    # Run the blocking sleep in a thread pool
    await run_in_threadpool(time.sleep, 5)
    
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Ending delay at {end_time}")
    
    response = {
        "message": "Response after 3 seconds delay",
        "start_time": start_time,
        "end_time": end_time
    }
    return response
