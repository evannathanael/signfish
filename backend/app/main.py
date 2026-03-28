from fastapi import FastAPI

from .routes.predict import router as predict_router

app = FastAPI(title="SignFish Backend", version="0.1.0")
app.include_router(predict_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
