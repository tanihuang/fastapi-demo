from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class StockAnalysis(SQLModel, table=True):
  __table_args__ = {"extend_existing": True}  # 解決重複定義錯誤

  id: Optional[int] = Field(default=None, primary_key=True)
  symbol: str
  date: date
  close: float
  rsi: float
