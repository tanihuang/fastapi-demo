from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from ultralytics import YOLO
from PIL import Image
import io
import numpy as np
import os
from datetime import datetime

router = APIRouter()

# ✅ 載入自訓練模型（請替換成你自己的 best.pt）
model = YOLO("models/train_yolov8n.pt")

# ✅ 中英文標籤對照表（可根據 data.yaml 自行擴充）
label_map = {
  "fracture": "骨折",
  "normal": "正常",
  "opacity": "陰影",
  "nodule": "結節",
  "effusion": "積液",
  # 依據你的類別補上更多...
}

@router.post("/classifyByHighlight")
async def classify_by_yolo(file: UploadFile = File(...), conf_threshold: float = 0.6):
  try:
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    np_image = np.array(image)

    # ✅ 模型推論（不過濾，全部顯示）
    results = model.predict(np_image, conf=0.001)

    boxes = []
    for r in results:
      names = r.names if hasattr(r, "names") else model.names
      for box in r.boxes.data:
        x1, y1, x2, y2, conf, cls = box.tolist()
        label_en = names[int(cls)]
        label_zh = label_map.get(label_en, label_en)
        boxes.append({
          "box": [x1, y1, x2, y2],
          "confidence": round(conf, 3),
          "label_en": label_en,
          "label_zh": label_zh,
          "highlight": conf >= conf_threshold
        })

    # ✅ 儲存圖片供前端顯示（可選）
    image_filename = f"yolo_result_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
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
