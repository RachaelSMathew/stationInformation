# index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
sys.path.append('.') ## appends . to end of PYTHONPATH
from collectPointsKDTree import newsearch, defaultFunc

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize KD-tree when FastAPI starts"""
    defaultFunc()  # Runs once at startup, after server/uvicorn.run starts

# This runs EVERY time someone visits /api/search
@app.get("/api/search")
async def search(lat: float, lon: float, minDistance: float = 0):
    results = newsearch(lat, lon, minDistance)
    return {
        "results": results,
        "count": len(results),
        "time_seconds": time.time() - start_time
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) # This starts server(does not happen at every request), blocks forever