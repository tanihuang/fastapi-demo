from app.services.fetch import fetch_stock_data
from app.services.analyze import calculate_indicators
from app.db.database import get_session
from app.models.stock import StockAnalysis

def fetch_and_store(symbol):
  df = fetch_stock_data(symbol)
  if df.empty:
    return

  df = calculate_indicators(df)
  last = df.dropna().iloc[-1]

  with get_session() as session:
    record = StockAnalysis(
        symbol=symbol.upper(),
        date=last.name.date(),
        close=float(last["Close"]),
        rsi=float(last["RSI"]),
        ma=float(last["MA"])
    )
    session.add(record)
    session.commit()

