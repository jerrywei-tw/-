# Azure AI Search + Azure OpenAI 向量搜尋範例

這個專案是一組 Azure AI Search / Azure OpenAI 的 Python 範例，示範如何建立向量索引、產生 embedding、上傳文件、執行向量搜尋，以及語意混合搜尋。

## 專案簡介

本範例主要涵蓋以下流程：

- 建立 Azure AI Search 索引
- 使用 Azure OpenAI 文字嵌入模型生成向量
- 將文件與向量一起寫入索引
- 以向量搜尋、簡單文字搜尋與語意混合搜尋查詢結果
- 維護索引與檢查狀態

這些腳本適合用來了解 Azure AI Search 在 RAG（檢索增強生成）場景中的基本使用方式。

## 目錄結構

```text
.
├── .env                          # Azure 服務設定檔（請勿提交到版本控制）
├── app.log                      # 執行紀錄
├── hotels-small.json            # 酒店資料範例
├── text-sample.json             # 測試文字資料
├── text-sample-embeddings.json  # 生成 embedding 後的 JSON
├── azure_ai_search_create_vector_index.py
├── azure_ai_search_hotel_index.py
├── azure_ai_search_index_maintenance.py
├── azure_ai_search_semantic_hybrid_search.py
├── azure_ai_search_simple_query.py
├── azure_ai_search_upload_vector_documents.py
├── azure_ai_search_vector_search.py
├── azure_openai_generate_embeddings.py
├── README.md
└── .gitignore
```

## 必要條件

- Python 3.10+
- Azure AI Search 服務
- Azure OpenAI 服務
- 已建立可用的 embedding deployment（例如 `text-embedding-3-small`）
- Azure SDK Python 套件

## 安裝依賴

```bash
pip install python-dotenv azure-search-documents azure-core openai rich
```

如果你已使用虛擬環境，請先啟用後再安裝。

## 環境變數設定

在專案根目錄建立 `.env` 檔，內容格式如下：

```env
AZURE_AI_SEARCH_API_ENDPOINT=https://<your-search-service>.search.windows.net
AZURE_AI_SEARCH_API_KEY=<your-search-admin-key>
AZURE_AI_SEARCH_INDEX_NAME=azure-ai-search-demo-index

AZURE_AI_SEARCH_HOTEL_INDEX_NAME=hotels-index

AZURE_OPENAI_API_KEY=<your-openai-key>
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_API_EMBEDDING_ENDPOINT=https://<your-openai-resource>.openai.azure.com/
AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT=text-embedding-3-small
```

> 注意：不要將 `.env` 檔案提交到 Git，請保留在本機環境中。

## 執行順序

### 1. 產生 embedding

```bash
python azure_openai_generate_embeddings.py
```

這個腳本會讀取 `text-sample.json`，呼叫 Azure OpenAI 的 embedding API，並輸出 `text-sample-embeddings.json`。

### 2. 建立向量索引

```bash
python azure_ai_search_create_vector_index.py
```

這個腳本會建立包含 `titleVector` 和 `contentVector` 的 Azure AI Search 向量索引。

### 3. 上傳文件

```bash
python azure_ai_search_upload_vector_documents.py
```

將帶有 embedding 的文件寫入到已建立的索引中。

### 4. 執行向量查詢

```bash
python azure_ai_search_vector_search.py
```

此腳本會將使用者查詢文字轉成 embedding，再透過 Azure AI Search 的 vector query 進行相似度搜尋。

### 5. 執行簡單文字查詢

```bash
python azure_ai_search_simple_query.py
```

這個範例展示 `QueryType.SIMPLE` 的搜尋方式，適合測試文字查詢與 scoring profile 的效果。

### 6. 執行語意混合搜尋

```bash
python azure_ai_search_semantic_hybrid_search.py
```

此腳本結合：

- 語意搜尋（semantic search）
- 向量搜尋（vector search）
- 混合查詢（hybrid search）

可用來比較一般搜尋與語意/向量搜尋的結果。

### 7. 酒店索引範例

```bash
python azure_ai_search_hotel_index.py
```

這個腳本示範建立與上傳 hotel 索引，資料來源為 `hotels-small.json`，適合練習更複雜的結構化索引設計。

### 8. 索引維護

```bash
python azure_ai_search_index_maintenance.py
```

這個腳本可用來檢查索引資訊與文件數量，亦可進一步擴充為清除索引文件等維護操作。

## 主要腳本說明

| 檔案 | 用途 |
| --- | --- |
| `azure_openai_generate_embeddings.py` | 生成文字 embedding 並輸出 JSON |
| `azure_ai_search_create_vector_index.py` | 建立向量索引 |
| `azure_ai_search_upload_vector_documents.py` | 上傳文件至索引 |
| `azure_ai_search_vector_search.py` | 執行向量搜尋 |
| `azure_ai_search_simple_query.py` | 執行簡單文字搜尋 |
| `azure_ai_search_semantic_hybrid_search.py` | 執行語意混合搜尋 |
| `azure_ai_search_hotel_index.py` | 建立 hotel 索引與上傳資料 |
| `azure_ai_search_index_maintenance.py` | 管理與檢查索引狀態 |

## 常見使用情境

- 知識庫搜尋（FAQ / 文件檢索）
- 向量搜尋應用程式
- RAG 系統中的檢索層
- 語意搜尋與混合搜尋效果比較
- Azure AI Search 基礎操作學習

## 注意事項

- 若你更改了索引名稱，請同步更新 `index_name` 或環境變數設定。
- 確認 Azure AI Search 與 Azure OpenAI 服務都已啟用且權限正確。
- 若 embedding 部署命名不一致，請修正 `AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT`。
- `app.log` 會記錄執行錯誤與結果，適合除錯時使用。

## 參考

- Azure AI Search 文件
- Azure OpenAI Embeddings 文件
- Python SDK for Azure AI Search

## 授權

本專案僅作為教學與範例使用，請依照你的實際環境與 Azure 服務使用條款來使用。
