from fastapi import FastAPI

from .routes.predict import router as predict_router
from app.routes.api import router as api_router



app.include_router(predict_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

app = FastAPI(
    title="Signfish Backend",
    description="Backend API for ASL fingerspelling typing practice.",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Signfish backend is running."}
