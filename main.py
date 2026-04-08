from fastapi import FastAPI
import psutil
from datetime import datetime
import logging
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(
    filename="metrics.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "DevOps Monitor Running 🚀"}

@app.get("/metrics")
def get_metrics():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    data = {
        "cpu_usage": cpu,
        "ram_usage": ram,
        "disk_usage": disk
    }

    # Log data
    logging.info(data)
# 🚨 ALERT LOGIC (ADD HERE)
    alert = None

    if cpu > 80:
        alert = "⚠️ High CPU Usage"
        
    elif ram > 80:
        alert = "⚠️ High RAM Usage"

    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "data": data,
        "alert": alert   # 👈 add this line
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "time": datetime.now().isoformat()
    }


