from dotenv import load_dotenv
load_dotenv()

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

import os

# 設定使用本地模型：`BAAI/bge-small-en`（推薦的小模型）
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")

# 設定嵌入模型（新版寫法）
Settings.embed_model = embed_model

# 載入檔案
data_dir = "app/data"
index_dir = "index"

documents = SimpleDirectoryReader(data_dir).load_data()
index = VectorStoreIndex.from_documents(documents)

# 儲存 index
index.storage_context.persist(index_dir)
print("✅ 已使用本地模型建立索引並儲存至 index/")
