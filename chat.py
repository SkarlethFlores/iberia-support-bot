# chat.py
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

SYSTEM_PROMPT = """You are a helpful Iberia customer support assistant.
Answer questions using ONLY the context provided below.
Always mention the fare type (Basico, Clasico, Flexible) when relevant.
If the answer is not in the context, say: "I don't have clear information 
on that — please contact Iberia directly at iberia.com/en/contact."
At the end of your answer always add a 'Source:' line with the section heading.
Be concise and friendly."""

def retrieve(question: str, top_k: int = 3) -> list:
    vector = aoai.embeddings.create(
        input=question,
        model=os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")
    ).data[0].embedding

    results = search.search(
        search_text=question,
        vector_queries=[VectorizedQuery(
            vector=vector,
            k_nearest_neighbors=top_k,
            fields="content_vector"
        )],
        select=["content", "topic", "section_heading", "url", "fare_classes"],
        top=top_k
    )
    return list(results)

def ask(question: str) -> str:
    # Step 1 — retrieve relevant chunks
    chunks = retrieve(question)

    if not chunks:
        return "I don't have information on that — please contact Iberia directly at iberia.com/en/contact."

    # Step 2 — build context from retrieved chunks
    context = ""
    for i, chunk in enumerate(chunks):
        context += f"\n[{i+1}] {chunk['section_heading']}\n{chunk['content']}\n"

    # Step 3 — generate answer with GPT-4.1-mini
    response = aoai.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ],
        temperature=0.2,  # low temp = more factual, less creative
        max_tokens=400
    )

    return response.choices[0].message.content

def main():
    print("✈️  Iberia Support Bot")
    print("Type your question or 'quit' to exit\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if not question:
            continue

        print("\nBot:", ask(question))
        print()

if __name__ == "__main__":
    main()