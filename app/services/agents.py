from pathlib import Path
from llama_cpp import Llama

# 切換是否使用真實 LLM（False 則回傳模擬訊息）
USE_REAL_LLM = True

# 載入本地 LLM 模型（使用 llama-cpp）
if USE_REAL_LLM:
  model_path = Path(__file__).resolve().parent.parent.parent / "models" / "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
  llm = Llama(model_path=str(model_path), n_ctx=512)

# 中英文混合情緒關鍵字分類
def classify_emotion(text: str):
  text = text.lower()
  emotion_keywords = {
    "happy": ["開心", "喜歡", "好棒", "讚", "happy", "like", "awesome", "great"],
    "sad": ["難過", "不想", "失敗", "傷心", "sad", "unhappy", "depressed"],
    "angry": ["氣", "爛", "不爽", "生氣", "angry", "mad", "furious"],
    "surprise": ["什麼", "真的假的", "驚訝", "surprise", "what", "really"],
    "confused": ["為什麼", "不懂", "怎麼", "confused", "why", "huh"]
  }

  for emotion, keywords in emotion_keywords.items():
    if any(k in text for k in keywords):
      return emotion
  return "neutral"

# 主回應函式，輸入訊息 → 回傳（回答、情緒）
def get_llm_response(message: str):
  if USE_REAL_LLM:
    prompt = f"Human: {message}\nAssistant:"
    output = llm(prompt, max_tokens=128, stop=["Human:"], echo=False)
    response = output["choices"][0]["text"].strip()
  else:
    response = f"你說：{message}，真有趣！"

  emotion = classify_emotion(response)
  return response, emotion
