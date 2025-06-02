from apscheduler.schedulers.background import BackgroundScheduler
from app.services.fetch import fetch_stock_data
from app.services.analyze import calculate_rsi
from app.db import get_session
from app.models.stock import StockAnalysis
from datetime import date

def analyze_and_save(symbol: str):
  df = fetch_stock_data(symbol)
  rsi = calculate_rsi(df["Close"])
  today = df.index[-1].date()
  close = float(df["Close"][-1])
  latest_rsi = float(rsi[-1])

  session = next(get_session())

  record = StockAnalysis(
    symbol=symbol.upper(),
    date=today,
    close=close,
    rsi=latest_rsi
  )
  session.add(record)
  session.commit()
  print(f"[{today}] Saved RSI for {symbol}: {latest_rsi}")

def start_scheduler():
  scheduler = BackgroundScheduler()
  # 每天早上 9:00 執行一次（UTC 時間，可調整）
  scheduler.add_job(lambda: analyze_and_save("AAPL"), "cron", hour=1, minute=0)
  scheduler.add_job(lambda: analyze_and_save("TSLA"), "cron", hour=1, minute=5)
  scheduler.start()
