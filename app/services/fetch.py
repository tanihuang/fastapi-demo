
import yfinance as yf
import pandas as pd

def fetch_stock_data(symbol: str) -> pd.DataFrame:
  stock = yf.Ticker(symbol)
  hist = stock.history(period="3mo", interval="1d")

  print(f"[DEBUG] {symbol} history rows: {len(hist)}")

  return hist

