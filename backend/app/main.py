from fastapi import FastAPI

from app.routes.api import router as api_router

app = FastAPI(
    title="Signfish Backend",
    description="Backend API for ASL fingerspelling typing practice.",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Signfish backend is running."}
