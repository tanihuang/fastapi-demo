from apscheduler.schedulers.background import BackgroundScheduler
from app.services.fetch import fetch_stock_data
from app.services.analyze import calculate_rsi, calculate_ma
from app.services.stock import fetch_and_store
from app.db.database import get_session
from app.models.stock import StockAnalysis
from datetime import datetime

SYMBOLS = ["AAPL", "TSLA", "MSFT"]

def start_scheduler():
  scheduler = BackgroundScheduler()

  for i, symbol in enumerate(SYMBOLS):
    scheduler.add_job(fetch_and_store, "cron", hour=0, minute=i * 5, args=[symbol])

  scheduler.start()

