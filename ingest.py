# ingest.py
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from scraper import scrape_all, ScrapedPage
from dotenv import load_dotenv
import os, hashlib
load_dotenv()

# Clients
aoai = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2025-04-01-preview"
)

search = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name="iberia-help",
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)

def embed(text: str) -> list:
    resp = aoai.embeddings.create(
        input=text,
        model=os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")
    )
    return resp.data[0].embedding

def chunk_text(text: str, max_words=150, overlap=30) -> list:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunk = " ".join(words[i:i+max_words])
        chunks.append(chunk)
        i += max_words - overlap
    return chunks

def ingest_all(pages: list):
    docs = []
    total_chunks = 0

    for page in pages:
        chunks = chunk_text(page.text)
        print(f"  📄 {page.topic}/{page.subtopic} → {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            doc_id = hashlib.sha256(f"{page.url}::{i}".encode()).hexdigest()[:32]
            vector = embed(chunk)

            docs.append({
                "id": doc_id,
                "content": chunk,
                "content_vector": vector,
                "topic": page.topic,
                "subtopic": page.subtopic,
                "section_heading": page.section_heading,
                "fare_classes": page.fare_classes,
                "language": page.language,
                "url": page.url,
                "chunk_index": i
            })
            total_chunks += 1

    # Upload in batches of 100
    print(f"\n⬆️  Uploading {total_chunks} chunks to Azure AI Search...")
    for i in range(0, len(docs), 100):
        batch = docs[i:i+100]
        search.upload_documents(documents=batch)
        print(f"  ✅ Uploaded batch {i//100 + 1} ({len(batch)} docs)")

    print(f"\n🎉 Ingestion complete! {total_chunks} chunks indexed.")

if __name__ == "__main__":
    print("🔍 Loading knowledge base...")
    pages = scrape_all()
    print(f"\n⚡ Embedding and indexing {len(pages)} sections...")
    ingest_all(pages)