import os, json, logging, sys
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType, VectorizedQuery
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    CorsOptions,
    ScoringProfile,
    ComplexField,
    TextWeights,
    SearchField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    VectorSearchProfile
)
from typing import List
from rich import print as pprint
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
from pathlib import Path
from openai import AzureOpenAI

load_dotenv()

service_endpoint = os.getenv("AZURE_AI_SEARCH_API_ENDPOINT")
api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
index_name = "azure-ai-search-vector-index6"

if not service_endpoint:
    raise ValueError("AZURE_AI_SEARCH_API_ENDPOINT environment variable is not set.")
if not api_key:
    raise ValueError("AZURE_AI_SEARCH_API_KEY environment variable is not set.")

def setup_logging():

    logger = logging.getLogger(__file__)
    logger.setLevel(logging.INFO)

    console_handler = RichHandler()
    console_handler.setLevel(logging.WARNING)

    file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()

console = Console()

def _delete_index():

    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(api_key)) as search_index_client:
            result = search_index_client.delete_index(index_name)
            pprint(f"[yellow]Index `{index_name}` deleted successfully.[/yellow]")
            logger.info(f"Index `{index_name}` deleted successfully.")
    except Exception as e:
        pprint(f"[red]Failed to delete index `{index_name}`, error: {e}[/red]")
        logger.error(f"Failed to delete index `{index_name}`, error: {e}")

def _create_index():

    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(api_key)) as search_index_client:
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="title", type=SearchFieldDataType.String),
                SearchableField(name="category", type=SearchFieldDataType.String, filterable=True),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SearchField(
                    name="titleVector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="my-vector-search-profile"
                ),
                SearchField(
                    name="contentVector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="my-vector-search-profile"
                )
            ]

            vector_search = VectorSearch(
                profiles=[VectorSearchProfile(name="my-vector-search-profile", algorithm_configuration_name="my-hnsw-algorithm")],
                algorithms=[HnswAlgorithmConfiguration(name="my-hnsw-algorithm")]
            )

            scoring_profiles:List[ScoringProfile] = []
            scoring_profile = ScoringProfile(
                name="my-scoring-profile",
                text_weights=TextWeights(weights={"content":2.0})
            )
            scoring_profiles.append(scoring_profile)
            cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)

            semantic_config = SemanticConfiguration(
                name="my-semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    keywords_fields=[SemanticField(field_name="category")],
                    content_fields=[SemanticField(field_name="content")]
                )
            )

            semantic_search = SemanticSearch(configurations=[semantic_config])

            index = SearchIndex(
                name=index_name,
                fields=fields,
                cors_options=cors_options,
                scoring_profiles=scoring_profiles,
                vector_search=vector_search,
                semantic_search=semantic_search
            )

            result = search_index_client.create_index(index)
            pprint(f"[green]Index `{index_name}` created successfully.[/green]")
    except Exception as e:
        pprint(f"[red]Failed to create index `{index_name}`: {e}[/red]")
        logger.error(f"Failed to create index `{index_name}`: {e}")

if __name__ == "__main__":
    _create_index()
