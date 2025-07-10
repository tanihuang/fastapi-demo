# RAG 查詢服務（rag.py）
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import load_index_from_storage, StorageContext, Settings
from app.config.llm_config import llm

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.embed_model = embed_model
Settings.llm = llm

storage_context = StorageContext.from_defaults(persist_dir="index")
index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine()

def query_rag(question: str):
  return str(query_engine.query(question))