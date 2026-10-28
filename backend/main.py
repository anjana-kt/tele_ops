from fastapi import FastAPI
from starlette import status

app = FastAPI(
    title="Realtime Telemetry & Log ingestion API",
    version="1.0",
    description="To get live data for observability"
)

@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health check"])
async def health_check():
    return {"status": "ok", "service": "Telemetry ingestion gateway"}

async def logs():
    return "log 1"
