from fastapi import FastAPI

app = FastAPI(title="Synllion API", version="0.1.0")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}