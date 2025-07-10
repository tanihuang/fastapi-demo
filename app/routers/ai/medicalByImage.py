from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import io
import torch
import torchvision.transforms as transforms
from torchvision import models
import os
import uuid
from pathlib import Path
from datetime import datetime

router = APIRouter()

# 確保儲存資料夾存在
BASE_DIR = Path("static/medical")
BASE_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/medicalByImage")
async def classify_medical(file: UploadFile = File(...)):
  try:
    # 載入模型
    model = models.densenet121()
    model.classifier = torch.nn.Linear(model.classifier.in_features, 2)
    model.load_state_dict(torch.load("models/train_densenet121.pt", map_location='cpu'))
    model.eval()

    # 讀取與儲存原始圖片
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # 建立唯一檔名：時間 + UUID
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    uuid_str = uuid.uuid4().hex
    filename = f"{uuid_str}.jpg"
    filepath = BASE_DIR / filename
    image.save(filepath)

    # 圖片前處理
    transform = transforms.Compose([
      transforms.Resize((224, 224)),
      transforms.ToTensor(),
    ])
    img_tensor = transform(image).unsqueeze(0)

    # 推論
    with torch.no_grad():
      outputs = model(img_tensor)
      predicted = torch.argmax(outputs, dim=1).item()
      prob = torch.softmax(outputs, dim=1)[0][predicted].item()

    label = "正常" if predicted == 0 else "異常"

    return {
      "status": "success",
      "data": [{
        "label": label,
        "confidence": round(prob, 3),
        "highlight": True
      }],
      "imageUrl": f"http://localhost:8000/{filepath.as_posix()}"
    }

  except Exception as e:
    return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
