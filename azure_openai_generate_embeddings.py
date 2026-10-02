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


def export_embeddings_to_json():

    try:
        path = Path.cwd() / "text-sample.json"
        with open(path, "r", encoding="utf-8") as f:
            input_data = json.load(f)

            titles = [item["title"] for item in input_data]
            contents = [item["content"] for item in input_data]

            titles_response = client.embeddings.create(
                input=titles,
                model=AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT
            )

            content_response = client.embeddings.create(
                input=contents,
                model=AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT
            )

            for i, item in enumerate(input_data):
                title = item["title"]
                content = item["content"]
                item["titleVector"] = titles_response.data[i].embedding
                item["contentVector"] = content_response.data[i].embedding

            output_path = Path.cwd() / "text-sample-embeddings.json"
            with open(output_path, "w", encoding="utf-8") as output_file:
                json.dump(input_data, output_file, ensure_ascii=False, indent=4)
            pprint(f"[green]Embedding exported successfully to {output_path}[/green]")
    except Exception as e:
        logger.error(f"An error occurred while exporting embeddings: {e}")
        pprint(f"[red]An error occurred while exporting embeddings: {e}[/red]")


if __name__ == "__main__":
    export_embeddings_to_json()
