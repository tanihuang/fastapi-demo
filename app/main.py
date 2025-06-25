from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import stock
from app.routers import ask
from app.db.database import init_db
from app.scheduler.jobs import start_scheduler
from dotenv import load_dotenv
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
  init_db()            # 初始化資料庫
  start_scheduler()    # 啟動排程器
  yield                # 讓應用繼續執行
  # 若有 shutdown 清理，也可加在 yield 後

app = FastAPI(lifespan=lifespan)
app.include_router(stock.router)
app.include_router(ask.router)
