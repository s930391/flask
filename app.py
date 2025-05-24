import os
from flask import Flask, render_template, request

from langchain_community.vectorstores import Qdrant
from langchain_openai import AzureOpenAIEmbeddings
from qdrant_client import QdrantClient
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 設定 Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 設定 Azure OpenAI Embeddings
embedding_function = AzureOpenAIEmbeddings(
    # e.g. text-embedding-3-small
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    # e.g. https://xxx.openai.azure.com/
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    # e.g. 2025-03-01-preview
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    chunk_size=1000
)

# 初始化 QdrantClient
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_KEY")
)


# 初始化向量庫
qdrant = Qdrant(
    client=qdrant_client,
    collection_name="acbe1efa77fa41b08f0f4488bb01f007",
    embeddings=embedding_function
)

# 初始化 Gemini LLM
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
        "max_output_tokens": 2048,
    },
    system_instruction="請用繁體中文回答以下問題。"
)

# 初始化 Flask App
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/call_gemini", methods=["POST"])
def call_gemini():
    if request.method == "POST":
        question = request.form["message"]
        print("使用者問題：" + question)

        # 相似搜尋
        # results = qdrant.similarity_search(question, k=3)
        results = qdrant.max_marginal_relevance_search(
            question, k=20, fetch_k=100, lambda_mult=0.8)

        if not results:
            return "找不到相關內容，請換個問題再試一次。"

        context = "\n\n".join(
            f"內容: {doc.page_content}\n相關資訊: {doc.metadata}" for doc in results)

        prompt = f"""你是一位鍵盤推薦助手，請依照使用者的需求，並根據以下產品資訊，以進行產品推薦：
                    <context>
                    {context}
                    </context>
                    使用者需求：{question}
                    請用繁體中文回答，且回答內容請去除重複句與警語；
                    只要是符合使用者需求的產品，皆要條列出來；
                    回答時要附上產品價格和簡要介紹；
                    每個產品開頭要有編號，後面一定要附上購買連結，格式在購買連結：後加上link的內容,並且要依據HTML使用跳出視窗的方式；
                    回答的結果若要使用粗體，請依據HTML的規則使用<b>，不要使用**來加粗文字；
                    若有後續補充或建議，開頭用※，不要前後使用**
                    除了上述要求，回答時不要出現多餘的HTML文字。"""

        response = gemini_model.generate_content(prompt)
        return response.text


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
