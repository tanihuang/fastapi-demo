## 📁 ai-legal-assistant 專案總覽

# 根目錄結構

ai-legal-assistant/
├── app/
│ ├── routers/
│ │ ├── ask.py
│ │ ├── agent.py
│ │ └── summary.py
│ ├── services/
│ │ ├── rag.py
│ │ ├── agents.py
│ │ └── summarizer.py
│ ├── config/
│ │ ├── llm_config.py
│ │ └── agent_config.py
│ └── main.py
├── index/ # 向量索引資料夾（已建立）
├── models/ # 放置 GGUF 模型的目錄
├── scheduler/
│ └── crawl_laws.py # 法規每日更新任務
├── build_index.py # 用來建立向量資料庫的程式
├── frontend/ # React 前端專案（另建 repo）
└── README.md # 專案說明與展示
