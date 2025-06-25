from fastapi import APIRouter, Query
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import load_index_from_storage, StorageContext, Settings

# 使用本地嵌入模型
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.embed_model = embed_model
Settings.llm = None  # 關閉 LLM，避免預設使用 OpenAI

# 載入 index（預設從 index 資料夾讀）
storage_context = StorageContext.from_defaults(persist_dir="index")
index = load_index_from_storage(storage_context)

# 查詢引擎（retriever-only 模式）
query_engine = index.as_query_engine(llm=None)

router = APIRouter()

@router.get("/ask")
async def ask(question: str = Query(...)):
    response = query_engine.query(question)
    return {
        "question": question,
        "answer": str(response)
    }
