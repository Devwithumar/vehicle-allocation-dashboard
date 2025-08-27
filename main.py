# backend/main.py - FastAPI skeleton for tracking & OTP endpoints
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI(title="Vehicle Allocation Backend (skeleton)")

# simple in-memory store for demo (replace with DB in production)
TRACKS = {}

class TrackPing(BaseModel):
    vehicle_id: str
    lat: float
    lon: float
    ts: Optional[datetime] = None

@app.post("/track")
def receive_ping(ping: TrackPing):
    ts = ping.ts or datetime.utcnow()
    entry = {"vehicle_id": ping.vehicle_id, "lat": ping.lat, "lon": ping.lon, "ts": ts.isoformat()}
    TRACKS.setdefault(ping.vehicle_id, []).append(entry)
    return {"status":"ok", "stored": entry}

@app.get("/track/{vehicle_id}")
def get_vehicle_track(vehicle_id: str):
    return {"vehicle_id": vehicle_id, "track": TRACKS.get(vehicle_id, [])}

@app.get("/health")
def health():
    return {"status":"ok", "time": datetime.utcnow().isoformat()}
