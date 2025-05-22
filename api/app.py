
from configparser import ConfigParser

from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from langchain.embeddings import SentenceTransformerEmbeddings


from flask import Flask, render_template, request, url_for

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 讀取 config.ini
config = ConfigParser()
config.read("config.ini")
genai.configure(api_key=config["Gemini"]["KEY"])

# 初始化 QdrantClient
client = QdrantClient(
    url=config["Qdrant"]["URL"],
    api_key=config["Qdrant"]["KEY"]
)

# 初始化向量庫（僅用於查詢）
embedding_function = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2")

qdrant = Qdrant(
    client=client,
    collection_name="acbe1efa77fa41b08f0f4488bb01f007",
    embeddings=embedding_function
)


# 建立網站設定
app = Flask(__name__)

# 設定LLM模型
gemini_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
    generation_config={
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    },
    system_instruction="請用繁體中文回答以下問題。",
)

# 主畫面


@app.route("/")
def home():
    return render_template("index.html")

# 呼叫LLM回答


@app.route("/call_gemini", methods=["POST"])
def call_gemini():
    if request.method == "POST":
        print("POST!")
        data = request.form
        question = data["message"]  # 使用者問題
        print("使用者問題：" + question)

        # 從 Qdrant 查詢最相關的向量內容
        results = qdrant.similarity_search(question, k=3)

        if not results:
            return "找不到相關內容，請換個問題再試一次。"

        # 整理 context（將每筆內容合併為一段文字）
        context = "\n\n".join(
            f"內容: {doc.page_content}\n相關資訊: {doc.metadata}" for doc in results)
        print("回傳：" + context)

        # prompt 格式
        prompt = f"""請根據以下產品資訊回答問題：
                    <context>
                    {context}
                    </context>
                    問題：{question}
                    請用繁體中文簡潔回答，並在回答最後附上購買連結。"""

        # LLM回應
        response = gemini_model.generate_content(prompt)
        print(response)
        return response.text

# if __name__ == "__main__":
 #   app.run()
