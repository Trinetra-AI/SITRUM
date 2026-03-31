from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.upgrades.pro_runner import SirtumAIPro
# If you want base mode later:
# from app.main import SirtumAI

app = FastAPI(title="Sirtum AI", version="1.0.0")


@app.get("/")
def home():
    return {
        "status": "live",
        "project": "Sirtum AI",
        "mode": "PRO",
        "message": "Sirtum AI is running on Render"
    }


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/analyze")
def analyze():
    try:
        bot = SirtumAIPro()
        result = bot.analyze()
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )