from fastapi import APIRouter, Body, HTTPException
from transformers import pipeline

router = APIRouter()

try:
  classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
except Exception as e:
  raise RuntimeError(f"Failed to load model: {e}")

@router.post("/classify")
async def classify_article(text: str = Body(..., embed=True)):
  try:
    result = classifier(
      text,
      candidate_labels=["technology", "health", "politics", "finance", "sports"]
    )
    return {"text": text, "classification": result}
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Classification failed: {e}")
