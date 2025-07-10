# 這支程式會初始化 LlamaCPP 模型，並提供可重用的 llm 給主程式使用。
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.core.llms import ChatMessage

# 請確認你已將 .gguf 模型下載到 models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
llm = LlamaCPP(
  model_path="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
  temperature=0.7,
  max_new_tokens=512,
  context_window=3900,
  generate_kwargs={},
  model_kwargs={
    "n_gpu_layers": 33,
    "n_batch": 512,
  }
)
