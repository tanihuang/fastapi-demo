from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from ultralytics import YOLO
from PIL import Image
import io
import numpy as np
import os
from datetime import datetime

router = APIRouter()

# ✅ 載入本地模型（免費）
model = YOLO("yolov8n.pt")  # 官方訓練好的模型 或自行訓練後替換為 "runs/detect/train/weights/best.pt"

@router.post("/classifyByYolo")
async def defect_classifier(file: UploadFile = File(...)):
  try:
    # 讀取圖片內容
    contents = await file.read()
    print("✅ 收到上傳的檔案：", file)
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    np_image = np.array(image)

    # 進行推論
    results = model.predict(np_image, conf=0.25)

    boxes = []
    for r in results:
      names = r.names if hasattr(r, "names") else model.names
      for box in r.boxes.data:
        x1, y1, x2, y2, conf, cls = box.tolist()
        boxes.append({
          "box": [x1, y1, x2, y2],
          "confidence": conf,
          "label": names[int(cls)]
        })

    # ✅ 儲存圖片並產出 URL（可選）
    image_filename = f"defect_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    image_path = f"static/{image_filename}"
    os.makedirs("static", exist_ok=True)
    image.save(image_path)

    return {
      "status": "success",
      "data": boxes,
      "imageUrl": f"http://localhost:8000/{image_path}",
    }

  except Exception as e:
    return JSONResponse(status_code=500, content={"error": str(e)})

# 💰 若改用 Ultralytics 雲端服務：
# model = YOLO("https://api.ultralytics.com/v1/predict")  # 需搭配 API key，費用約 $5/1000 張
