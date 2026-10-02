import os
import json
import logging
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.models import QueryType
from dotenv import load_dotenv
from rich import print as pprint
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console

load_dotenv()

console = Console()
service_endpoint = os.getenv("AZURE_AI_SEARCH_API_ENDPOINT")
api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
index_name = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")

if not service_endpoint:
    raise ValueError("AZURE_AI_SEARCH_API_ENDPOINT is not set.")

if not api_key:
    raise ValueError("AZURE_AI_SEARCH_API_KEY is not set.")

if not index_name:
    raise ValueError("AZURE_AI_SEARCH_INDEX_NAME is not set.")

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

def print_search_results(results, total_count):
    table = Table(title=f"Search Results - Total: {total_count}")
    table.add_column("Document ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Category", style="green")
    table.add_column("Content", style="white")
    table.add_column("@Search.Score", style="red")

    for r in results:
        table.add_row(
            str(r.get("id","")),
            str(r.get("title","")),
            r.get("category",""),
            r.get("content","")[:100],
            str(r.get("@search.score",""))
        )

    console.print(table)

def search_index_by_querytype_simple():

    try:
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(api_key)) as search_client:
            results = search_client.search(
                query_type=QueryType.SIMPLE,
                search_text="gateway",
                scoring_profile="MyProfile",
                include_total_count=True
            )

            # logger.info(f"results: {results}")
            all_results = list(results)
            logger.info(f"resutls:\n{json.dumps([dict(record) for record in all_results], indent=2, ensure_ascii=False)}")


            all_records = [r for r in all_results]

            if not all_records:
                pprint("[yellow]No results found.[/yellow]")
            else:
                print_search_results(all_records, results.get_count())

    except Exception as e:
        pprint(f"[red]An error occurred: {e}[/red]")
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    search_index_by_querytype_simple()
