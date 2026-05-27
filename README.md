# ✈️ Iberia Customer Support RAG Bot

A production-grade Retrieval-Augmented Generation (RAG) system that answers customer questions about Iberia airline policies — built entirely on Microsoft Azure.

> **Disclaimer:** This is an independent learning project and is not affiliated with, endorsed by, or connected to Iberia Airlines in any way. All policy content is sourced from Iberia's publicly available help documentation.

---

## 🧠 What it does

Users ask natural language questions about Iberia flight policies — baggage allowances, fare rules, check-in times, pet travel, seat selection — and the bot retrieves the most relevant policy content from an Azure AI Search vector index and generates a grounded, cited answer using GPT-4.1-mini.

```
You: Can I change my Basico ticket?
Bot: No, changes are not permitted for Basico fare tickets.
     The ticket is non-changeable and non-refundable.
     Source: Changing your flight by fare type

You: Can I bring my dog on board?
Bot: Yes, small dogs are allowed in the cabin if the total weight
     of the dog plus carrier does not exceed 8kg...
     Source: Travelling with pets in the cabin
```

---

## 🏗️ Architecture

```
Knowledge Base (JSON)
        │
        ▼
   scraper.py          ← loads and structures policy documents
        │
        ▼
   ingest.py           ← chunks text, embeds with text-embedding-3-small,
        │                 pushes vectors to Azure AI Search
        ▼
Azure AI Search        ← hybrid vector + keyword index with
  (iberia-help)          fare_class metadata filtering
        │
        ▼
    chat.py            ← embeds user query → retrieves top-k chunks
        │                 → generates answer with GPT-4.1-mini
        ▼
   User answer         ← grounded response with source citation
```

### Azure services used

| Service | Purpose |
|---|---|
| Azure AI Foundry | Workspace and model management |
| Azure OpenAI — GPT-4.1-mini | Answer generation |
| Azure OpenAI — text-embedding-3-small | Document and query embedding |
| Azure AI Search | Vector index and hybrid retrieval |

---

## 📁 Project structure

```
iberia-support-bot/
├── .env                        # credentials (not committed)
├── data/
│   └── iberia_knowledge.json   # structured policy knowledge base
├── create-index.py             # creates Azure AI Search index schema
├── scraper.py                  # loads knowledge base
├── ingest.py                   # embeds and indexes documents
├── test-search.py              # retrieval testing and validation
└── chat.py                     # interactive chatbot
```

---

## ⚙️ Setup

### Prerequisites

- Python 3.11+
- Azure account with Azure AI Foundry resource
- Azure AI Search resource (Free tier works)

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/iberia-support-bot.git
cd iberia-support-bot
```

### 2. Install dependencies

```bash
pip install openai azure-search-documents azure-storage-blob python-dotenv beautifulsoup4 requests
```

### 3. Configure environment variables

Create a `.env` file in the root directory:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_EMBED_DEPLOYMENT=embedding
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=your_admin_key_here
```

### 4. Create the search index

```bash
python create-index.py
```

### 5. Ingest the knowledge base

```bash
python ingest.py
```

### 6. Run the chatbot

```bash
python chat.py
```

---

## 🔍 How retrieval works

Each user question goes through three steps:

**1. Embedding** — the question is embedded using `text-embedding-3-small` into a 1536-dimensional vector.

**2. Hybrid search** — Azure AI Search runs both vector similarity search and keyword search simultaneously, combining scores for better recall. Results are filtered and ranked by relevance.

**3. Generation** — the top-3 retrieved chunks are passed as context to GPT-4.1-mini with a system prompt that instructs it to answer only from the provided context and always cite its source. If no relevant content is found, the bot directs the user to Iberia's contact page rather than hallucinating.

---

## 🗂️ Index schema

The Azure AI Search index stores the following fields per chunk:

| Field | Type | Purpose |
|---|---|---|
| `id` | String (key) | SHA-256 hash of url + chunk index |
| `content` | String (searchable) | Chunk text for keyword search |
| `content_vector` | Vector (1536-dim) | Embedding for semantic search |
| `topic` | String (filterable) | e.g. baggage, changes, checkin |
| `subtopic` | String (filterable) | e.g. hand_luggage, refunds |
| `fare_classes` | Collection (filterable) | e.g. ["basico", "clasico"] |
| `section_heading` | String | Used as citation in answers |
| `url` | String | Source URL for reference |
| `chunk_index` | Int | Position within original document |

---

## 💬 Example questions to try

```
Can I change my Basico ticket?
How many kilos can I check in with a Clasico fare?
What is the hand luggage size limit?
Can I bring my cat on the plane?
What happens if I miss check-in?
How do I earn Avios points?
Can I get a refund on a Flexible ticket?
What are the fees for extra baggage?
```

---

## 🛠️ Key design decisions

**Fare-class metadata filtering** — every chunk is tagged with the fare classes it mentions (`basico`, `clasico`, `flexible`). This enables targeted retrieval when a user specifies their fare type, returning more precise answers than plain vector search.

**Confidence-based fallback** — when retrieved context doesn't contain a clear answer, the system prompt instructs GPT-4.1-mini to explicitly say so and redirect to Iberia's contact page, rather than hallucinating policy details.

**Low temperature (0.2)** — the generation model is configured with low temperature to produce factual, consistent answers rather than creative variations — critical for a policy Q&A use case.

**Chunk overlap** — text chunks use a 30-word overlap to prevent policy rules from being split across chunk boundaries and missed during retrieval.

---

## 🚀 Potential extensions

- [ ] Azure Functions HTTP trigger to expose the bot as a REST API
- [ ] Streamlit or Gradio frontend for a web UI
- [ ] Fare-class detection from user query to auto-filter retrieval
- [ ] Evaluation harness with ground-truth Q&A pairs
- [ ] Azure Container Apps deployment with CI/CD via GitHub Actions
- [ ] Conversation memory with Azure Cosmos DB
- [ ] Multilingual support (Spanish) using the same index with language filter

---

👤 Author
Skarleth Motiño Flores


## 📄 License

MIT — free to use for learning and portfolio purposes.
