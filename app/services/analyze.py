import yfinance as yf
import pandas as pd

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
  delta = series.diff()
  gain = delta.where(delta > 0, 0).rolling(window=period).mean()
  loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
  rs = gain / loss
  return 100 - (100 / (1 + rs))

def calculate_ma(series: pd.Series, period: int = 5) -> pd.Series:
  return series.rolling(window=period).mean()

async def analyze_stock(symbol: str):
  try:
    stock = yf.Ticker(symbol)
    hist = stock.history(period="30d")  # 拉長一點以計算 RSI

    if hist.empty:
      return {"error": "No data found for this symbol."}

    hist["RSI"] = calculate_rsi(hist["Close"])

    # 抽出最近5筆 RSI
    recent_rsi = hist[["Close", "RSI"]].dropna().tail(5)
    rsi_result = [
      {
          "date": idx.strftime("%Y-%m-%d"),
          "close": round(row["Close"], 2),
          "rsi": round(row["RSI"], 2)
      }
      for idx, row in recent_rsi.iterrows()
    ]

    return {
      "symbol": symbol,
      "rsi_period": 14,
      "recent_rsi": rsi_result,
      "last_close": round(hist["Close"].iloc[-1], 2),
    }

  except Exception as e:
    return {"error": str(e)}
