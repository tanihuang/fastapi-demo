from fastapi import APIRouter, Query
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import load_index_from_storage, StorageContext, Settings
from app.config.llm_config import llm  # ✅ 匯入自定義本地 LLM

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.embed_model = embed_model
Settings.llm = llm  # ✅ 指定本地 LLM

storage_context = StorageContext.from_defaults(persist_dir="index")
index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine()

router = APIRouter()

@router.get("/ask")
async def ask(question: str = Query(...)):
  response = query_engine.query(question)
  return {
    "question": question,
    "answer": str(response)
  }
