# Concurrency and Parallelism in FastAPI

FastAPI is designed to support asynchronous (non-blocking) operations, which makes it an excellent framework for handling many concurrent requests. However, it’s essential to understand the trade-offs and techniques when dealing with blocking code or when a higher level of parallelism is required.

This document explains several methods to improve concurrency in FastAPI, covering:

- Blocking versus Non-blocking operations
- Using asynchronous endpoints
- Offloading blocking tasks with thread pools
- Deploying with multiple worker processes

---

## 1. Blocking Requests in FastAPI

### Example: `main_simple.py`

In the `main_simple.py` example, the endpoint uses the blocking function `time.sleep(3)`:

```python
@app.post("/delay")
async def delayed_response():
    logger.info("Received POST request to delay endpoint")
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Starting delay at {start_time}")
    
    time.sleep(3)  # Blocking call
    
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Ending delay at {end_time}")
    
    response = {
        "message": "Response after 3 seconds delay",
        "start_time": start_time,
        "end_time": end_time
    }
    logger.info(f"Sending response: {response}")
    return response
```

**Issues:**

- **Blocking Nature:** Although the endpoint is declared with `async def`, using `time.sleep(3)` blocks the entire event loop. This means that while one request is sleeping, other incoming requests must wait.
- **Concurrency Impact:** For CPU-bound or blocking I/O operations, a single worker process can only handle one request at a time until the blocking call completes.

---

## 2. Using Asynchronous Sleep and Non-Blocking I/O

### Example: `main_sync.py`

To fully leverage FastAPI's asynchronous capabilities, you should use non-blocking I/O functions such as `await asyncio.sleep()`. In the `main_sync.py` example, an asynchronous sleep is used:

```python
@app.post("/delay")
async def delayed_response():
    logger.info("Received POST request to delay endpoint")
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Starting delay at {start_time}")
    
    # Non-blocking sleep (async)
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
```

**Benefits:**

- **Non-Blocking:** Using `await asyncio.sleep(5)` suspends only the current coroutine, allowing the event loop to handle other tasks concurrently.
- **Improved Scalability:** Multiple requests can be processed concurrently without waiting for the blocking call to complete.

---

## 3. Offloading Blocking Operations with a Thread Pool

### Example: `main_threadpool.py`

If you must use blocking code (for example, when working with libraries that don't support asynchronous operations), you can offload these tasks to a thread pool using `run_in_threadpool`:

```python
from fastapi.concurrency import run_in_threadpool

@app.post("/delay")
async def delayed_response_threadpool():
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Starting delay at {start_time}")
    
    # Offload blocking sleep to a thread pool
    await run_in_threadpool(time.sleep, 5)
    
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Ending delay at {end_time}")
    
    response = {
        "message": "Response after 3 seconds delay",
        "start_time": start_time,
        "end_time": end_time
    }
    return response
```

**Advantages:**

- **No Event Loop Blockage:** The blocking operation runs in a separate thread, so it does not block the main event loop.
- **Hybrid Approach:** It allows you to use blocking libraries within an asynchronous framework without significant performance penalties.

---

## 4. Deploying with Multiple Worker Processes

### Example: `main_worker.py`

Even with non-blocking code or thread pools, there are cases (such as CPU-bound tasks) where running multiple processes can improve performance. FastAPI, when served with Uvicorn, supports deployment with multiple workers. In `main_worker.py`, a worker identifier is added using the process ID to help illustrate which worker handles each request:

```python
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
    
    time.sleep(3)  # Blocking call for demonstration
    
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
```

**Key Points:**

- **Identification:** Using `os.getpid()` allows you to see which process (worker) handled the request.
- **Multiple Workers:** Running the app with `uvicorn.run("main_worker:app", ..., workers=4)` spawns multiple processes. Each process runs independently, allowing the application to handle multiple blocking requests concurrently.

### Running with Multiple Workers

To run with multiple workers from the command line, you can also execute:

```bash
uvicorn main_worker:app --host 0.0.0.0 --port 8005 --workers 4
```

**Important Considerations:**

- **State Sharing:** Each worker is an independent process, which means in-memory states are not shared between them. Use external storage or caching if you need to share state.
- **Application Import String:** When using workers or reload mode, Uvicorn requires the application to be specified as an import string, e.g., `"main_worker:app"`.

---

## Summary and Best Practices

- **Avoid Blocking the Event Loop:** When writing asynchronous endpoints, use non-blocking I/O such as `await asyncio.sleep()` instead of `time.sleep()`.
- **Handle Blocking Code with Thread Pools:** For operations that cannot be made asynchronous (e.g., third-party libraries), offload the blocking code using `run_in_threadpool` to prevent blocking the event loop.
- **Leverage Multiple Worker Processes:** Deploy your FastAPI application with multiple worker processes using Uvicorn’s `--workers` parameter or by specifying `workers` in `uvicorn.run()`. This approach can distribute the load even if some requests block.
- **Worker Identification:** Utilize `os.getpid()` to log which worker processes handle specific requests. This can help in debugging and performance monitoring.
- **Deployment Considerations:** In production, use asynchronous programming practices along with multi-worker setups. Always ensure proper state management when using multiple processes.

By combining these methods, you can build a FastAPI application that handles concurrent requests efficiently and scales well under load.