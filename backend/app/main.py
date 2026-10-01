import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.config import CORS_ALLOWED_ORIGINS, BACKEND_HOST, BACKEND_PORT
from app.routers import calendar, queues

app = FastAPI(
    title="Sistema de Predicción de Ausentismo",
    description="Backend en FastAPI con inferencia de ausentismo en tiempo real y dimensionamiento estocástico M/M/s.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calendar.router)
app.include_router(queues.router)

@app.get("/")
def read_root():
    return {"message": "Backend running successfully.", "status": "active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)
