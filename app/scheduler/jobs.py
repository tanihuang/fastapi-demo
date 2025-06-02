from apscheduler.schedulers.background import BackgroundScheduler
from app.services.fetch import fetch_stock_data
from app.services.analyze import calculate_rsi, calculate_ma
from app.db import get_session
from app.models.stock import StockAnalysis
from datetime import datetime

def fetch_and_store(symbol: str = "AAPL"):
  df = fetch_stock_data(symbol)
  if df.empty:
    return

  rsi_series = calculate_rsi(df["Close"])
  ma_series = calculate_ma(df["Close"])

  last_date = df.index[-1].date()
  last_close = float(df["Close"].iloc[-1])
  last_rsi = float(rsi_series.iloc[-1]) if not rsi_series.isna().iloc[-1] else None
  last_ma = float(ma_series.iloc[-1]) if not ma_series.isna().iloc[-1] else None

  with get_session() as session:
    record = StockAnalysis(
      symbol=symbol,
      date=last_date,
      close=last_close,
      rsi=last_rsi,
      ma=last_ma
    )
    session.add(record)
    session.commit()

def start_scheduler():
  scheduler = BackgroundScheduler()
  scheduler.add_job(fetch_and_store, "cron", hour=0, minute=0)  # 每天午夜 00:00 執行
  scheduler.start()
