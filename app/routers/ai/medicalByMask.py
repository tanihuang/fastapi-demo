from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import io
import torch
import numpy as np
import uuid
from pathlib import Path
from monai.transforms import Compose, EnsureChannelFirst, Resize, ToTensor
from monai.networks.nets import UNet

router = APIRouter()

# 建立模型結構
def build_unet():
  return UNet(
    spatial_dims=2,
    in_channels=1,
    out_channels=1,
    channels=(16, 32, 64, 128, 256),
    strides=(2, 2, 2, 2),
    num_res_units=2,
  )

@router.post("/medicalByMask")
async def segment_medical(file: UploadFile = File(...)):
  try:
    # 建立儲存資料夾
    BASE_DIR = Path("static/medical")
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    # 讀取並處理圖片
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("L")
    image_np = np.array(image.resize((256, 256)))  # 給模型推論用，不是用來儲存

    # 儲存原始圖片
    uuid_str = uuid.uuid4().hex
    filename = f"{uuid_str}.jpg"
    filepath = BASE_DIR / filename
    image.save(filepath)  # ✅ 正確儲存原始圖

    # 前處理
    transform = Compose([
      EnsureChannelFirst(channel_dim="no_channel"),
      Resize((256, 256)),
      ToTensor()
    ])
    input_tensor = transform(image_np).unsqueeze(0)

    # 載入模型
    model = build_unet()
    state_dict = torch.load("models/train_monai.pt", map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()

    # 推論遮罩
    with torch.no_grad():
      output = model(input_tensor)
      prob = torch.sigmoid(output)[0][0]
      mask_np = (prob > 0.5).numpy().astype(np.uint8) * 255

    # 疊圖
    overlay = np.stack([image_np] * 3, axis=2)
    overlay[mask_np > 0] = [255, 0, 0]

    # 儲存遮罩與疊圖
    overlay_path = BASE_DIR / f"{uuid_str}_overlay.jpg"
    mask_path = BASE_DIR / f"{uuid_str}_mask.jpg"
    Image.fromarray(overlay.astype(np.uint8)).save(overlay_path)
    Image.fromarray(mask_np).save(mask_path)

    return {
      "status": "success",
      "data": [{
        "label": "異常區域",
        "confidence": round(float(prob.mean().item()), 3),
        "highlight": True,
        "overlayUrl": f"http://localhost:8000/{overlay_path.as_posix()}",
        "maskUrl": f"http://localhost:8000/{mask_path.as_posix()}"
      }],
      "imageUrl": f"http://localhost:8000/{filepath.as_posix()}",
    }

  except Exception as e:
    return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
