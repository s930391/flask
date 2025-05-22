import json
from configparser import ConfigParser
from langchain_qdrant import QdrantVectorStore
from langchain.embeddings import SentenceTransformerEmbeddings

# 讀取 config.ini
config = ConfigParser()
config.read("config.ini")

# 讀取 JSON 檔案
with open("list_2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 3. 準備文本內容（轉成向量的主體）與對應的 metadata
texts = [item["feature"] for item in data]  # 要轉成向量的描述內容

metadatas = [
    {
        "ID": item.get("ID"),
        "feature": item.get("feature"),
        "link": item.get("link"),
        "name": item.get("name"),
        "price": item.get("price"),        
        "spec": item.get("spec"),
    }
    for item in data
]

# 4. 設定 embedding model
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# 5. 上傳至 Qdrant 向量資料庫
qdrant = QdrantVectorStore.from_texts(
    texts=texts,
    embedding=embedding_function,
    metadatas=metadatas,
    url=config["Qdrant"]["URL"],
    api_key=config["Qdrant"]["KEY"],
    prefer_grpc=True
) 