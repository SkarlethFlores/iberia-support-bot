# test-search.py
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

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

def retrieve(question: str, top_k: int = 3):
    # Embed the question
    vector = aoai.embeddings.create(
        input=question,
        model=os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")
    ).data[0].embedding

    # Vector search
    results = search.search(
        search_text=question,
        vector_queries=[VectorizedQuery(
            vector=vector,
            k_nearest_neighbors=top_k,
            fields="content_vector"
        )],
        select=["content", "topic", "subtopic", "section_heading", "url", "fare_classes"],
        top=top_k
    )

    print(f"\n🔍 Query: '{question}'\n")
    for i, r in enumerate(results):
        print(f"Result {i+1}:")
        print(f"  Topic:   {r['topic']} / {r['subtopic']}")
        print(f"  Heading: {r['section_heading']}")
        print(f"  Fares:   {r['fare_classes']}")
        print(f"  Preview: {r['content'][:150]}...")
        print()

# Test with a few questions
retrieve("Can I change my Basico flight?")
retrieve("How much luggage can I bring?")
retrieve("Can I bring my cat on the plane?")