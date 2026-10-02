import os, json, logging, sys
import time
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from dotenv import load_dotenv
from rich import print as pprint
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console

load_dotenv()

service_endpoint = os.getenv("AZURE_AI_SEARCH_API_ENDPOINT")
api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
hotel_index_name = os.getenv("AZURE_AI_SEARCH_HOTEL_INDEX_NAME")

if not service_endpoint:
    raise ValueError("AZURE_AI_SEARCH_API_ENDPOINT is not set.")

if not api_key:
    raise ValueError("AZURE_AI_SEARCH_API_KEY is not set.")

if not hotel_index_name:
    raise ValueError("AZURE_AI_SEARCH_HOTEL_INDEX_NAME is not set.")

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

def _get_index():

    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(api_key)) as search_index_client:
            index = search_index_client.get_index(hotel_index_name)
            pprint(f"Index `{hotel_index_name}` retrieved successfully.")
    except Exception as e:
        pprint(f"[red]Error getting index: `{hotel_index_name}`:{e}")
        logger.exception(f"Error getting index: `{hotel_index_name}`:{e}")

def _get_index_document_count() -> int:
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(api_key)) as search_index_client:
            stats = search_index_client.get_index_statistics(hotel_index_name)
            doc_count = stats.document_count
            pprint(f"[green]Index `{hotel_index_name}` document count: {doc_count}[/green]")

            return doc_count
    except Exception as e:
        pprint(f"[red]Error getting document count for index `{hotel_index_name}`:{e}[/red]")
        logger.exception(f"Error getting document count for index `{hotel_index_name}`:{e}")
        return 0

def _clear_index_documents_with_wait(batch_size=1000) -> None:
    try:
        with SearchClient(service_endpoint, hotel_index_name, AzureKeyCredential(api_key)) as search_client:

            total_deleted = 0

            while True:
                results = list(search_client.search(
                    search_text="*",
                    select=["hotelId"],
                    top=batch_size
                ))

                if not results:
                    break

                keys = [{"hotelId":doc["hotelId"]} for doc in results]

                print(keys)

                search_client.delete_documents(documents=keys)

                total_deleted += len(keys)

                time.sleep(2)

            pprint(f"[green]All documents deleted from index `{hotel_index_name}` successfully. Total deleted: {total_deleted}[/green]")
            logger.info(f"All documents deleted from index `{hotel_index_name}` successfully. Total deleted: {total_deleted}")
    except Exception as e:
        pprint(f"[red]Error clearing documents from index `{hotel_index_name}`: {e}[/red]")
        logger.exception(f"Error clearing documents from index `{hotel_index_name}`: {e}")

if __name__ == "__main__":
    # _get_index()
    _get_index_document_count()
    # _clear_index_documents_with_wait()
    
