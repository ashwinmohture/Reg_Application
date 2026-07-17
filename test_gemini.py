from dotenv import load_dotenv
import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

print("Key Found:", bool(os.getenv("GOOGLE_API_KEY")))

emb = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

print("Testing embedding...")

result = emb.embed_query("Hello World")

print("Success!")
print(len(result))