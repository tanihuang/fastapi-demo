from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.routers import stock, ask, agent, summary, update_data
from app.routers.ai import classifyByHighlight, classifyByImage, classifyByYolo, medicalByImage, medicalByMask, contract
from app.db.database import init_db
from app.scheduler.jobs import start_scheduler
from app.websocket.agent import websocket_endpoint
from dotenv import load_dotenv
import os

load_dotenv()

# ✅ 應用壽命週期控制（啟動初始化 DB 與排程）
@asynccontextmanager
async def lifespan(app: FastAPI):
  init_db()
  start_scheduler()
  yield
  # 可在此清理資源

app = FastAPI(lifespan=lifespan)

# ✅ 加入 CORS（允許前端跨域連接）
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# ✅ 掛載圖片靜態目錄（提供預測後圖片連結）
if not os.path.exists("static"):
  os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ 路由註冊
app.include_router(stock.router)
app.include_router(ask.router)
app.include_router(update_data.router)
# app.include_router(classify.router)
# app.include_router(agent.router, prefix="/agent")
# app.include_router(summary.router, prefix="/summary")
app.include_router(classifyByYolo.router, prefix="/ai")
app.include_router(classifyByHighlight.router, prefix="/ai")
app.include_router(classifyByImage.router, prefix="/ai")

app.include_router(medicalByImage.router, prefix="/ai")
app.include_router(medicalByMask.router, prefix="/ai")

app.include_router(contract.router, prefix="/ai")
app.websocket("/ws")(websocket_endpoint)
