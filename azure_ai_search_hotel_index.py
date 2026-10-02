import os
from dotenv import load_dotenv
import logging
from typing import List
import json
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient

from azure.search.documents.models import QueryType
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    CorsOptions,
    ComplexField,
    TextWeights,
    SearchField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    ScoringProfile
)
from typing import List
from rich import print as pprint
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
from pathlib import Path

load_dotenv()

service_endpoint = os.getenv("AZURE_AI_SEARCH_API_ENDPOINT")
api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
index_name = os.getenv("AZURE_AI_SEARCH_HOTEL_INDEX_NAME")

if not service_endpoint:
    raise ValueError("AZURE_AI_SEARCH_API_ENDPOINT is not set.")

if not api_key:
    raise ValueError("AZURE_AI_SEARCH_API_KEY is not set.")

if not index_name:
    raise ValueError("AZURE_AI_SEARCH_HOTEL_INDEX_NAME is not set.")


def setup_logger():

    logger = logging.getLogger()
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

logger = setup_logger()

def _delete_index():

    try:
        with SearchIndexClient(endpoint=service_endpoint, credential=AzureKeyCredential(api_key)) as search_client:
            search_client.delete_index(index_name)
        logger.info(f"Index `{index_name}` deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete index: {e}")

def _create_index():
    try:
        fields = [
            SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True, filterable=True, sortable=True),
            SearchableField(name="hotelName", type=SearchFieldDataType.String, sortable=True, filterable=True),
            SearchableField(name="description", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
            SearchableField(name="descriptionFr", type=SearchFieldDataType.String, analyzer_name="fr.lucene"),
            SearchableField(name="category", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
            SearchableField(name="tags", type=SearchFieldDataType.String, facetable=True, filterable=True, collection=True),
            SimpleField(name="parkingIncluded", type=SearchFieldDataType.Boolean, filterable=True, sortable=True),
            SimpleField(name="smokingAllowed", type=SearchFieldDataType.Boolean, filterable=True, sortable=True),
            SimpleField(name="lastRenovationDate", type=SearchFieldDataType.DateTimeOffset, facetable=True, filterable=True, sortable=True),
            SimpleField(name="rating", type=SearchFieldDataType.Double, facetable=True, filterable=True, sortable=True),
            SimpleField(name="location", type=SearchFieldDataType.GeographyPoint, filterable=True, sortable=True),
            ComplexField(name="address", fields=[
                SearchableField(name="streetAddress", type=SearchFieldDataType.String),
                SearchableField(name="city", type=SearchFieldDataType.String, facetable=True, sortable=True),
                SearchableField(name="stateProvince", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
                SearchableField(name="postalCode", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
                SearchableField(name="country", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True)
            ]),
            ComplexField(name="rooms", fields=[
                SearchableField(name="description", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
                SearchableField(name="descriptionFr", type=SearchFieldDataType.String, analyzer_name="fr.lucene"),
                SearchableField(name="type", type=SearchFieldDataType.String),
                SimpleField(name="baseRate", type=SearchFieldDataType.Double, filterable=True),
                SimpleField(name="bedOptions", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="sleepsCount", type=SearchFieldDataType.Int32, filterable=True),
                SimpleField(name="smokingAllowed", type=SearchFieldDataType.Boolean, filterable=True),
                SearchableField(name="tags", type=SearchFieldDataType.String, facetable=True, filterable=True, collection=True)
            ],
            collection=True
            )
        ]

        semantic_config = SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="hotelName"),
                keywords_fields=[SemanticField(field_name="category"), SemanticField(field_name="tags")],
                content_fields=[SemanticField(field_name="description"), SemanticField(field_name="descriptionFr")]
            )
        )

        semantic_search = SemanticSearch(configurations=[semantic_config])

        scoring_profiles:List[ScoringProfile] = []
        scoring_profile = ScoringProfile(
            name="my-scoring-profile",
            text_weights=TextWeights(weights={"description": 1.5})
        )

        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)


        index = SearchIndex(
            name=index_name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options,
            semantic_search=semantic_search
        )

        with SearchIndexClient(service_endpoint, AzureKeyCredential(api_key)) as search_index_client:
            search_index_client.create_index(index)
            pprint(f"[green]Index created successfully: {index_name}[/green]")
    except Exception as e:
        pprint(f"[red]Error creating index: {index_name}:{e}[/red]")
        logger.error(f"Error creating index: {index_name}:{e}")

def _upload_documents():

    try:
        path = Path.cwd().joinpath("hotels-small.json")
        with open(path, "r", encoding="utf-8") as f:
            input_data = json.load(f)

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(api_key)) as search_client:
            result = search_client.upload_documents(documents=input_data)
            pprint(f"[green]Documents uploaded successfully: {result}[/green]")
    except Exception as e:
        pprint(f"[red]Error uploading documents: {e}[/red]")
        logger.error(f"Error uploading documents: {e}")

if __name__ == "__main__":
    # _delete_index()
    _create_index()
    _upload_documents()
    
