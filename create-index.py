# create-index.py
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType,
    SimpleField, SearchableField,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
    SemanticConfiguration, SemanticSearch,
    SemanticPrioritizedFields, SemanticField
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os
load_dotenv()

index_client = SearchIndexClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)

fields = [
    SimpleField(name="id",              type=SearchFieldDataType.String,  key=True),
    SearchableField(name="content",     type=SearchFieldDataType.String,  analyzer_name="en.lucene"),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="hnsw-profile"
    ),
    SimpleField(name="topic",           type=SearchFieldDataType.String,  filterable=True, facetable=True),
    SimpleField(name="subtopic",        type=SearchFieldDataType.String,  filterable=True),
    SimpleField(
        name="fare_classes",
        type=SearchFieldDataType.Collection(SearchFieldDataType.String),
        filterable=True, facetable=True
    ),
    SimpleField(name="language",        type=SearchFieldDataType.String,  filterable=True),
    SimpleField(name="section_heading", type=SearchFieldDataType.String,  retrievable=True),
    SimpleField(name="url",             type=SearchFieldDataType.String,  retrievable=True),
    SimpleField(name="chunk_index",     type=SearchFieldDataType.Int32,   retrievable=True),
]

vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="hnsw-algo")],
    profiles=[VectorSearchProfile(name="hnsw-profile", algorithm_configuration_name="hnsw-algo")]
)

semantic_config = SemanticConfiguration(
    name="iberia-semantic",
    prioritized_fields=SemanticPrioritizedFields(
        content_fields=[SemanticField(field_name="content")],
        keywords_fields=[SemanticField(field_name="topic"), SemanticField(field_name="section_heading")]
    )
)

index = SearchIndex(
    name="iberia-help",
    fields=fields,
    vector_search=vector_search,
    semantic_search=SemanticSearch(configurations=[semantic_config])
)

index_client.create_or_update_index(index)
print("✅ Index created: iberia-help")