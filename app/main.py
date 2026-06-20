from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.api import quality, availability, diversion, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MedTrack API",
    description="AI-powered pharmaceutical intelligence — quality, availability, and diversion detection.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quality.router, prefix="/api/quality", tags=["Quality"])
app.include_router(availability.router, prefix="/api/availability", tags=["Availability"])
app.include_router(diversion.router, prefix="/api/diversion", tags=["Diversion"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
def root():
    return {"status": "ok", "service": "MedTrack API v0.1.0"}