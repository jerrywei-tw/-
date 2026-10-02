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

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_API_EMBEDDING_ENDPOINT = os.getenv("AZURE_OPENAI_API_EMBEDDING_ENDPOINT")
AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT")

service_endpoint = os.getenv("AZURE_AI_SEARCH_API_ENDPOINT")
api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
index_name = "azure-ai-search-vector-index6"

if not service_endpoint:
    raise ValueError("AZURE_AI_SEARCH_API_ENDPOINT environment variable is not set.")
if not api_key:
    raise ValueError("AZURE_AI_SEARCH_API_KEY environment variable is not set.")
if not AZURE_OPENAI_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set.")
if not AZURE_OPENAI_API_VERSION:
    raise ValueError("AZURE_OPENAI_API_VERSION environment variable is not set.")
if not AZURE_OPENAI_API_EMBEDDING_ENDPOINT:
    raise ValueError("AZURE_OPENAI_API_EMBEDDING_ENDPOINT environment variable is not set.")
if not AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT:
    raise ValueError("AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT environment variable is not set.")

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_API_EMBEDDING_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION
)

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

def print_search_results(results, top_k, query):
    table = Table(title=f"Top {top_k} Search Results for Query: `{query}`")
    table.add_column("Id", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Category", style="green")
    table.add_column("Content", style="green")
    table.add_column("TitleVector", style="yellow")
    table.add_column("ContentVector", style="yellow")
    table.add_column("@SearchScore", style="red")

    for r in results:
        table.add_row(
            str(r.get("id", "")),
            str(r.get("title", "")),
            str(r.get("category", "")),
            str(r.get("content", ""))[:100] + "..." if r.get("content", "") else "",
            str(r.get("titleVector", ""))[:10] + "..." if r.get("titleVector", "") else "",
            str(r.get("contentVector", ""))[:10] + "..." if r.get("contentVector", "") else "",
            str(r.get("@search.score", ""))
        )

    console.print(table)

def _vector_search():

    try:
        query = "tools for software development"
        embedding = client.embeddings.create(
            input=query,
            model=AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT
        ).data[0].embedding

        vector_query = VectorizedQuery(
            vector=embedding,
            k_nearest_neighbors=3,
            fields="contentVector,titleVector"
        )

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(api_key)) as search_client:
            results = search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                top=2
                # select=["id", "title", "category", "content", "titleVector", "contentVector"]
            )

            all_results = list(results)

            log_results = []

            for r in all_results:
                record_dict = dict(r)
                record_dict.pop("titleVector",None)
                record_dict.pop("contentVector",None)
                log_results.append(record_dict)
            logger.info(f"results:\n{json.dumps(log_results, indent=2, ensure_ascii=False)}")

            all_records = [r for r in all_results]

            if not all_records:
                pprint("[yellow]No results found.[/yellow]")
            else:
                print_search_results(all_records, top_k=2, query=query)

    except Exception as e:
        pprint(f"[red]Error occurred during vector search: {e}[/red]")
        logger.error(f"Error occurred during vector search: {e}")

if __name__ == "__main__":
    _vector_search()

