from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
import shutil
from PIL import Image
import pytesseract
import re
import spacy
import pkuseg
from opencc import OpenCC
from app.services.contract import rag_answer, load_faq_text

router = APIRouter()
BASE_DIR = Path("static/contract")
BASE_DIR.mkdir(parents=True, exist_ok=True)

contract_db = {}

risk_keywords = {
  "責任", "賠償", "違約", "罰則", "終止", "消費", "解約", "退費", "爭議", "索賠", "契約",
  "liability", "compensation", "breach", "penalty", "termination", "dispute", "refund"
}

nlp = spacy.load("zh_core_web_sm")
if "sentencizer" not in nlp.pipe_names:
  nlp.add_pipe("sentencizer")

pkuseg_seg = pkuseg.pkuseg()
from spacy.tokens import Doc

def custom_tokenizer(nlp):
  def tokenizer(text):
    words = pkuseg_seg.cut(text)
    return Doc(nlp.vocab, words=words)
  return tokenizer

nlp.tokenizer = custom_tokenizer(nlp)
cc = OpenCC('s2t')

def split_sentences(text: str):
  doc = nlp(text)
  return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

def extract_text_from_file(filepath: Path):
  suffix = filepath.suffix.lower()
  text = ""
  imageUrl = None
  boxes = []

  try:
    if suffix in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
      image = Image.open(filepath)
      data = pytesseract.image_to_data(
        image, lang="chi_tra+chi_sim+eng", output_type=pytesseract.Output.DICT
      )

      for i, word in enumerate(data["text"]):
        clean_word = word.strip()
        if not clean_word:
          continue
        if any(kw in clean_word for kw in risk_keywords):
          boxes.append({
            "text": clean_word,
            "left": data["left"][i],
            "top": data["top"][i],
            "width": data["width"][i],
            "height": data["height"][i],
            "conf": data["conf"][i],
          })

      text = "\n".join([t.strip() for t in data["text"] if t.strip()])
      imageUrl = f"http://localhost:8000/{filepath.as_posix()}"

    elif suffix == ".pdf":
      from PyPDF2 import PdfReader
      reader = PdfReader(str(filepath))
      text = "\n".join([page.extract_text() or "" for page in reader.pages])

    elif suffix in [".txt", ".md", ".csv"]:
      with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    elif suffix == ".docx":
      import docx
      doc = docx.Document(str(filepath))
      text = "\n".join([para.text for para in doc.paragraphs])

    return text, imageUrl, boxes

  except Exception as e:
    print(f"[❌ extract_text_from_file] failed: {e}")
    return "", None, []

def generate_summary(text: str):
  sentences = split_sentences(text)
  risk_sentences = []

  for sent in sentences:
    keywords_found = [kw for kw in risk_keywords if kw in sent]
    if len(keywords_found) >= 1:
      highlighted = sent
      for kw in keywords_found:
        highlighted = highlighted.replace(kw, f"<mark>{kw}</mark>")
      risk_sentences.append({
        "text": highlighted,
        "keywords": keywords_found
      })

  summary_text = "\n".join([s["text"] for s in risk_sentences[:3]])
  summary_text = cc.convert(summary_text)
  return summary_text, risk_sentences

def answer_question(text: str, question: str):
  keywords = re.findall(r"[\w\u4e00-\u9fff]+", question)
  matches = [line.strip() for line in text.split("\n") if any(k in line for k in keywords)]
  return matches[:3] if matches else []

@router.post("/contract/upload")
async def upload_contract(file: UploadFile = File(...)):
  try:
    file_id = uuid.uuid4().hex
    ext = Path(file.filename).suffix
    filename = f"{file_id}{ext}"
    filepath = BASE_DIR / filename

    with open(filepath, "wb") as buffer:
      shutil.copyfileobj(file.file, buffer)

    text, imageUrl, raw_boxes = extract_text_from_file(filepath)

    if not text.strip():
      return JSONResponse(status_code=400, content={"status": "error", "message": "無法從檔案中擷取文字"})

    summary, risks = generate_summary(text)

    formatted_boxes = []
    for box in raw_boxes:
      x1 = box["left"]
      y1 = box["top"]
      x2 = x1 + box["width"]
      y2 = y1 + box["height"]
      try:
        conf_value = float(box["conf"])
      except:
        conf_value = 0.0

      formatted_boxes.append({
        "box": [x1, y1, x2, y2],
        "label": box["text"],
        "confidence": conf_value / 100.0 if conf_value > 0 else 0.0
      })

    contract_db[file_id] = {
      "text": text,
      "summary": summary,
      "risks": risks,
      "imageUrl": imageUrl,
      "data": formatted_boxes,
    }

    return {
      "status": "success",
      "chatId": file_id,
      "imageUrl": imageUrl,
      "data": formatted_boxes,
    }

  except Exception as e:
    return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.get("/contract/{file_id}/summary")
def get_summary(file_id: str):
  if file_id not in contract_db:
    return JSONResponse(status_code=404, content={"status": "error", "message": "Contract not found"})

  data = contract_db[file_id]
  return {
    "status": "success",
    "summary": data["summary"],
    "risks": data["risks"],
    "data": data.get("data", []),
    "imageUrl": data.get("imageUrl"),
  }

@router.post("/contract/form")
async def ask_contract(
  chatId: str = Form(...),
  question: str = Form(...),
  prompt: str = Form(...)
):
  if chatId not in contract_db:
    return JSONResponse(status_code=404, content={"status": "error", "message": "Contract not found"})

  text = contract_db[chatId]["text"]

  # ✅ 從固定路徑讀取 FAQ JSON
  faq_text = load_faq_text("app/data/faq.json")  # 你可以自訂路徑或讀檔錯誤處理

  answer = rag_answer(text, question, prompt, extra_text=faq_text)

  return {
    "status": "success",
    "question": question,
    "answer": answer
  }
