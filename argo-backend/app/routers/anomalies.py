from fastapi import APIRouter
import google.generativeai as genai
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/v1/api/anomalies", tags=["anomalies"])

if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

@router.get("", response_model=dict)
async def get_anomalies():
    return {"message": "No anomalies detected"}

@router.post("/analyze", response_model=dict)
async def analyze_anomaly(context: str):
    if not settings.GEMINI_API_KEY:
        return {"error": "Gemini API key not configured"}
    
    model = genai.GenerativeModel('gemini-3-pro-preview')
    response = model.generate_content(f"Analyze this art world anomaly: {context}")
    return {"analysis": response.text}
