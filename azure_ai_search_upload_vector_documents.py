import os, json, logging, sys
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient, SearchIndexingBufferedSender
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

def _upload_documents():

    try:
        output_path = Path.cwd() / "text-sample-embeddings.json"

        with open(output_path, "r", encoding="utf-8") as file:
            documents = json.load(file)

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(api_key)) as search_client:
            result = search_client.upload_documents(documents=documents)
            pprint(f"[green]Documents uploaded successfully.[/green]")
    except Exception as e:
        pprint(f"[red]Error uploading documents: {e}[/red]")
        logger.error(f"Error uploading documents: {e}")

def _upload_documents_by_indexingbufferedsender():
    try:
        output_path = Path.cwd() / "text-sample-embeddings.json"

        with open(output_path, "r", encoding="utf-8") as file:
            documents = json.load(file)

        with SearchIndexingBufferedSender(
            endpoint=service_endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key)
        ) as batch_client:
            batch_client.upload_documents(documents=documents)

        pprint(f"[green]Documents uploaded successfully using SearchIndexingBufferedSender.[/green]")
    except Exception as e:
        pprint(f"[red]Error uploading documents using SearchIndexingBufferedSender: {e}[/red]")
        logger.error(f"Error uploading documents using SearchIndexingBufferedSender: {e}")






if __name__ == "__main__":
    _upload_documents()
    # _upload_documents_by_indexingbufferedsender()

