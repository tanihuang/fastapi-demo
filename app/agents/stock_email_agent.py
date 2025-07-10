import pandas as pd
from datetime import datetime
from app.services.analyze import calculate_indicators
from app.services.mail import send_stock_alert

# 模擬你抓到的股價資料（實際可接 API）
def load_stock_data() -> pd.DataFrame:
  # 假資料：收盤價時間序列
  dates = pd.date_range(end=datetime.today(), periods=30)
  prices = [150 + i * 0.5 for i in range(30)]  # 假設上漲走勢
  df = pd.DataFrame({"Date": dates, "Close": prices})
  return df.set_index("Date")

# 依指標計算並決定是否要寄信
def run_stock_email_agent():
  df = load_stock_data()
  df = calculate_indicators(df)

  latest = df.iloc[-1]
  rsi = latest["RSI"]
  ma = latest["MA"]
  close = latest["Close"]

  # 決策邏輯：RSI 超過 70 則寄出警告信
  if rsi > 70:
    summary = (
      f"Stock Alert - RSI: {rsi:.2f} (>70), MA: {ma:.2f}, Price: {close:.2f}\n"
      f"Action suggested: Consider SELL signal."
    )
    send_stock_alert(summary)
    print("✅ Alert email sent.")
    return summary
  else:
    print("ℹ️ No alert needed today.")
    return "No alert needed today."

if __name__ == "__main__":
  run_stock_email_agent()