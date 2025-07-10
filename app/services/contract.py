from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from transformers import AutoTokenizer, AutoModelForCausalLM
from opencc import OpenCC
from pathlib import Path
import torch
import json

# ✅ 嵌入模型：支援多語（免登入）
embedding_model = HuggingFaceEmbeddings(
  model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# ✅ 中文生成模型（免登入）
llm_model_id = "IDEA-CCNL/Wenzhong-GPT2-110M"
# llm_model_id = "ckiplab/gpt2-base-chinese"

tokenizer = AutoTokenizer.from_pretrained(llm_model_id)
model = AutoModelForCausalLM.from_pretrained(llm_model_id)

# ✅ 繁簡轉換器
cc = OpenCC('t2s')      # 繁轉簡，用於送出 prompt
cc_rev = OpenCC('s2t')  # 簡轉繁，用於回傳結果


def split_sentences(text: str):
  """從 contract router 匯入或複製用"""
  import spacy
  import pkuseg
  from spacy.tokens import Doc

  nlp = spacy.load("zh_core_web_sm")
  if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")
  pkuseg_seg = pkuseg.pkuseg()

  def custom_tokenizer(nlp):
    def tokenizer(text):
      words = pkuseg_seg.cut(text)
      return Doc(nlp.vocab, words=words)
    return tokenizer

  nlp.tokenizer = custom_tokenizer(nlp)
  doc = nlp(text)
  return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


def load_faq_text(json_path: str = "app/data/faq.json") -> str:
  """載入 FAQ JSON 檔案為額外說明文字"""
  path = Path(json_path)
  if path.exists():
    with open(path, "r", encoding="utf-8") as f:
      data = json.load(f)
      if isinstance(data, list):
        return "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in data])
      elif isinstance(data, dict):
        return "\n".join([f"Q: {k}\nA: {v}" for k, v in data.items()])
  return ""


def build_db(text: str, extra_text: str = ""):
  sentences = split_sentences(text)
  extra_sentences = split_sentences(extra_text) if extra_text else []
  all_sentences = sentences + extra_sentences
  docs = [Document(page_content=s) for s in all_sentences]
  db = FAISS.from_documents(docs, embedding_model)
  return db


def rag_answer(text: str, question: str, prompt_template: str, extra_text: str = ""):
  # 建立向量資料庫
  db = build_db(text, extra_text)

  # 語意搜尋相似句
  retrieved_docs = db.similarity_search(question, k=2)
  context = "\n".join([doc.page_content for doc in retrieved_docs])

  # 建立 Prompt
  prompt = prompt_template.format(context=context, question=question)
  prompt_simplified = cc.convert(prompt)

  input_ids = tokenizer.encode(
    prompt_simplified,
    return_tensors="pt",
    truncation=True,
    max_length=512
  )

  output = model.generate(
    input_ids,
    max_new_tokens=100,
    do_sample=False,
    eos_token_id=tokenizer.eos_token_id if tokenizer.eos_token_id else None,
    repetition_penalty=1.2,
    no_repeat_ngram_size=3,
  )

  decoded = tokenizer.decode(output[0], skip_special_tokens=True)
  answer_only = decoded.replace(prompt_simplified, "").strip()

  return cc_rev.convert(answer_only)
