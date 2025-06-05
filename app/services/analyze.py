import pandas as pd

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_ma(series: pd.Series, period: int = 5) -> pd.Series:
    return series.rolling(window=period).mean()

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df["RSI"] = calculate_rsi(df["Close"])
    df["MA"] = calculate_ma(df["Close"])
    return df
