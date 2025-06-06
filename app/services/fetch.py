
import yfinance as yf
import pandas as pd

def fetch_stock_data(symbol: str) -> pd.DataFrame:
  try:
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1mo")
    if hist.empty:
      print(f"[ERROR] No data for symbol: {symbol}")
    return hist
  except Exception as e:
    print(f"[ERROR] Failed to fetch data for {symbol}: {e}")
    return pd.DataFrame()

