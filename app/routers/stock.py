from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlmodel import select
from app.services.fetch import fetch_stock_data
from app.services.analyze import calculate_rsi, calculate_ma
from app.db.database import get_session
from app.models.stock import StockAnalysis
import pandas as pd

router = APIRouter()

@router.get("/stocks/{symbol}")
def get_stock(symbol: str):
  df = fetch_stock_data(symbol)
  df = df.dropna()

  if df.empty:
    raise HTTPException(status_code=404, detail=f"No stock data found for symbol: {symbol}")
  
  df["RSI"] = calculate_rsi(df["Close"])
  df["MA"] = calculate_ma(df["Close"])
  latest = df.iloc[-1]

  return {
    "date": latest.name.date().isoformat(),
    "close": round(latest["Close"], 2),
    "rsi": round(latest["RSI"], 2),
    "ma": round(latest["MA"], 2)
  }

@router.get("/history/{symbol}")
def get_history(symbol: str, session: Session = Depends(get_session)):
  statement = (
    select(StockAnalysis)
    .where(StockAnalysis.symbol == symbol.upper())
    .order_by(StockAnalysis.date.desc())
    .limit(10)
  )
  results = session.exec(statement).all()
  return [
    {
        "date": r.date.isoformat(),
        "symbol": r.symbol,
        "close": r.close,
        "rsi": round(r.rsi, 2),
        "ma": round(r.ma, 2)
    } for r in reversed(results)
  ]
