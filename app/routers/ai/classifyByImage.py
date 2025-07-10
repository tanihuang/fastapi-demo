# routers/classify_by_image.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import torch
import torchvision.transforms as transforms
from PIL import Image
from io import BytesIO
import os
from datetime import datetime

router = APIRouter()

# ✅ 載入 ResNet 模型與類別
model_path = "models/train_resnet18.pt"
checkpoint = torch.load(model_path, map_location="cpu")

model = torch.hub.load('pytorch/vision', 'resnet18', pretrained=False)
model.fc = torch.nn.Linear(model.fc.in_features, len(checkpoint['classes']))
model.load_state_dict(checkpoint['model'])
model.eval()

class_names = checkpoint['classes']

# ✅ 預處理
transform = transforms.Compose([
  transforms.Resize((224, 224)),
  transforms.ToTensor(),
])

@router.post("/classifyByImage")
async def classify_by_image(file: UploadFile = File(...)):
  try:
    contents = await file.read()
    image = Image.open(BytesIO(contents)).convert("RGB")
    input_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
      outputs = model(input_tensor)
      _, predicted = torch.max(outputs, 1)
      label = class_names[predicted.item()]
      confidence = torch.softmax(outputs, dim=1)[0][predicted.item()].item()

    # ✅ 儲存圖片供前端顯示
    image_filename = f"resnet_result_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    image_path = f"static/{image_filename}"
    os.makedirs("static", exist_ok=True)
    image.save(image_path)

    print(f"[INFO] 預測結果：{label} ({confidence * 100:.2f}%)")

    return {
      "status": "success",
      "data": [{
        "label": label,
        "confidence": round(confidence, 4),
        "highlight": True
      }],
      "imageUrl": f"http://localhost:8000/{image_path}",
    }

  except Exception as e:
    return JSONResponse(status_code=500, content={"error": str(e)})
