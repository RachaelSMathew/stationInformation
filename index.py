# index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
sys.path.append('.') ## appends . to end of PYTHONPATH
from collectPointsKDTree import newsearch, defaultFunc
import time
app = FastAPI()
from opensearch import createIndex

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
## a test where the points have more vairant long
## a test where the points have more vairant lat
## a test where the points are all within a mile of aother point 
## do these tests with a point in chicago and one far away (in SC)
@app.on_event("startup")
async def startup_event():
    """Initialize KD-tree when FastAPI starts"""
    createIndex()
    defaultFunc()  # Runs once at startup, after server/uvicorn.run starts

# This runs EVERY time someone visits /api/search
@app.get("/newsearch/")
async def search(lat: float, long: float, minDistance: float = 0):
    start_time = time.time()
    results = newsearch(lat, long, minDistance)
    return {
        "results": results,
        "count": len(results),
        "time_seconds": time.time() - start_time
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) # This starts server(does not happen at every request), blocks forever