# app/routers/update_data.py

from fastapi import APIRouter, UploadFile, File
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os

router = APIRouter()

@router.post("/update-data")
async def update_data(file: UploadFile = File(...)):
    upload_dir = "uploaded_docs"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 處理文件並重建 index
    documents = SimpleDirectoryReader(upload_dir).load_data()
    node_parser = SentenceSplitter()
    nodes = node_parser.get_nodes_from_documents(documents)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    index = VectorStoreIndex(nodes, embed_model=embed_model)

    # 儲存 index
    index.storage_context.persist(persist_dir="index")

    return {"status": "success", "filename": file.filename}
