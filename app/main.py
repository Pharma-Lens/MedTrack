"""MedTrack FastAPI entrypoint."""
from fastapi import FastAPI
from app.database import Base, engine
from app.api import dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MedTrack", description="Medicine quality, availability, and diversion intelligence")

app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "MedTrack"}
