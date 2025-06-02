
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlmodel import select
from app.services.fetch import fetch_stock_data
from app.services.analyze import calculate_rsi
from app.services.analyze import calculate_ma
from app.db import get_session
from app.models.stock import StockAnalysis
from app.models.stock import StockAnalysis
import pandas as pd

router = APIRouter()

@router.get("/stocks/{symbol}")
def get_stock_data(symbol: str):
  data = fetch_stock_data(symbol)
  return data.tail(5).to_dict()

@router.get("/analyze/{symbol}")
def analyze_stock(symbol: str):
  data = fetch_stock_data(symbol)
  rsi = calculate_rsi(data["Close"])
  ma = calculate_ma(data["Close"])

  session = get_session()
  recent_data = []

  for date in data.index[-5:]:
    close = round(data["Close"][date], 2)
    rsi_val = round(rsi[date], 2) if pd.notna(rsi[date]) else None
    ma_val = round(ma[date], 2) if pd.notna(ma[date]) else None

    record = StockAnalysis(
      symbol=symbol.upper(),
      date=date.date(),
      close=close,
      rsi=rsi_val,
      ma=ma_val
    )
    session.add(record)
    recent_data.append({
      "date": date.strftime("%Y-%m-%d"),
      "close": close,
      "rsi": rsi_val,
      "ma": ma_val
    })

  session.commit()

  return {
    "symbol": symbol.upper(),
    "rsi_period": 14,
    "recent_analysis": recent_data,
    "last_close": round(data["Close"].iloc[-1], 2)
  }

@router.get("/history/{symbol}")
def get_history(symbol: str, session: Session = Depends(get_session)):
  statement = (
    select(StockAnalysis)
    .where(StockAnalysis.symbol == symbol)
    .order_by(StockAnalysis.date.desc())
    .limit(10)  # 👉 只取最近的 10 筆
  )
  results = session.exec(statement).all()
  return [
    {
      "date": r.date.isoformat(),
      "close": r.close,
      "rsi": round(r.rsi, 2)
    } for r in results
  ]

@router.get("/history/{symbol}")
def get_stock_history(symbol: str, db: Session = Depends(get_session)):
  rows = (
    db.query(StockAnalysis)
    .filter(StockAnalysis.symbol == symbol.upper())
    .order_by(StockAnalysis.date.desc())
    .limit(10)
    .all()
  )
  return [
    {
      "date": row.date.isoformat(),
      "symbol": row.symbol,
      "close": row.close,
      "rsi": round(row.rsi, 2),
    }
    for row in reversed(rows)  # 時間順序回傳
  ]
