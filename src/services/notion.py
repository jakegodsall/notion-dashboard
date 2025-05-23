import os
import yaml
from datetime import datetime, timedelta
from notion_client import Client

from src.utils.logger import get_logger

logger = get_logger()

class NotionClient:
    def __init__(self, config_path: str, integration_name: str):
        self._config_path = config_path
        self.integration_name = integration_name

    @property
    def api_key(self) -> str:
        """Retrieve the Notion API key from environment variables."""
        key = os.environ.get("NOTION_API_KEY")
        if not key:
            raise ValueError("Notion API key not valid:", key)
        return key
    
    @property
    def client(self) -> Client:
        """Lazy-load the Notion client with authentication."""
        if not hasattr(self, "_client"):
            self._client = Client(auth=self.api_key)
        return self._client
    
    @property
    def config(self) -> dict:
        """Load the Notion configuration from the YAML file for the given integration."""
        if not hasattr(self, "_config"):
            with open(self._config_path, 'r') as file:
                config = yaml.safe_load(file).get("notion", {})
                integrations = config.get('integrations', {})

                if self.integration_name not in integrations:
                    err_msg = f"No configuration found for integration {self.integration_name}"
                    logger.error(err_msg)
                    raise ValueError(err_msg)
                
                logger.info("Notion database config loaded.")
                self._config = integrations[self.integration_name]

        return self._config

    def build_properties(self, field_mappings, data: dict):
        """
        Builds the Notion properties from data and field mappings.
        """
        properties = {}
        for field, config in field_mappings.items():
            try:
                field_type = config.get("type")
                label = config["label"]

                if field_type == "date":
                    if config["key"] not in data:
                        raise KeyError(f"Missing key '{config['key']}' in data for 'date' field.")
                    properties[label] = {
                        "date": {"start": data[config["key"]]}
                    }
                elif field_type == "number":
                    if config["key"] not in data:
                        raise KeyError(f"Missing key '{config['key']}' in data for 'number' field with field {field}.")
                    properties[label] = {
                        "number": data[config["key"]]
                    }
                elif field_type == "relation":
                    if config["key"] not in data:
                        raise KeyError(f"Missing key '{config['key']}' in data for 'relation' field.")
                    related_database_id = config["relation"]["database_id"]
                    related_field_name = config["relation"]["field_name"]
                    properties[label] = {
                        "relation": [
                            {"id": self.get_related_id(related_database_id, related_field_name, data[config["key"]])}]
                    }
                elif field_type == "text":
                    if config["key"] not in data:
                        raise KeyError(f"Missing key '{config['key']}' in data for 'text' field.")
                    properties[label] = {
                        "rich_text": [{"type": "text", "text": {"content": data[config["key"]]}}]
                    }
                elif field_type == "select":
                    if config["key"] not in data:
                        raise KeyError(f"Missing key '{config['key']}' in data for 'select' field.")
                    properties[label] = {
                        "select": {"name": data[config["key"]]}
                    }
                elif field_type == "title":
                    if config["key"] not in data:
                        raise KeyError(f"Missing key '{config['key']}' in data for 'title' field.")
                    properties[label] = {
                        "title": [{"type": "text", "text": {"content": data[config["key"]]}}]
                    }
                else:
                    err_msg = f"Unsupported field type: {field_type}"
                    logger.error(err_msg)
                    raise ValueError(err_msg)

            except KeyError as e:
                err_msg = f"Error processing field '{field}': {e}"
                logger.error(err_msg)
                raise ValueError(err_msg) from e
            except Exception as e:
                err_msg = f"Unexpected error processing field '{field}': {e}"
                logger.error(err_msg)
                raise ValueError(err_msg) from e

        return properties
    
    def get_related_id(self, related_database_id, key, value):
        """Get the id for the related page in a related database."""
        response = self.client.databases.query(
            database_id=related_database_id,
            filter={
                "property": key,
                "rich_text": {
                    "equals": value
                }
            }
        )
        results = response.get("results", [])

        if results:
            return results[0]["id"]
        return None
    
    def get_pages(self, date_str: str):
        """Get pages from the Notion database for the given day."""
        logger.info(f"Getting pages for the database id {self.config['database_id']} for date: {date_str}")
        try:
            database_id = self.config["database_id"]

            next_day = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

            pages = self.client.databases.query(**{
                "database_id": database_id,
                "filter": {
                    "and": [
                        {"property": "Date", "date": {"on_or_after": date_str}},
                        {"property": "Date", "date": {"before": next_day}}
                    ]
                }
            })

            pages = pages.get('results', [])
            if not pages:
                logger.info(f"No pages found for {date_str} in Notion database.")

            return pages
        except ValueError:
            logger.error(f'Invalid date format: {date_str}. Expected YYYY-MM-DD')

    def get_pages_two_day_period(self, date_str: str):
        """Get pages from the Notion database for the given day and previous day."""
        logger.info(f"Getting pages for two day period ending on {date_str}")
        try:
            database_id = self.config["database_id"]
            
            # Get previous day
            prev_day = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            next_day = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

            pages = self.client.databases.query(**{
                "database_id": database_id,
                "filter": {
                    "and": [
                        {"property": "Date", "date": {"on_or_after": prev_day}},
                        {"property": "Date", "date": {"before": next_day}}
                    ]
                }
            })

            pages = pages.get('results', [])
            if not pages:
                logger.info(f"No pages found for period {prev_day} to {date_str} in Notion database.")

            return pages
        except ValueError:
            logger.error(f'Invalid date format: {date_str}. Expected YYYY-MM-DD')

    def create_page(self, data: dict):
        """Create a new page in Notion with a custom ID."""
        database_id = self.config["database_id"]
        field_mappings = self.config["field_mappings"]
        properties = self.build_properties(field_mappings, data)

        resp = self.client.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        logger.info(f"Page created in the database: {database_id}")
        return resp
    
    def update_or_create_page(self, date_str: str, data: dict, data_field: str, notion_field: str, use_two_day_period: bool = False):
        """
        Check the pages from the database for the given day and update the record if present,
        create if not.

        Args:
            date_str: The date to check for records
            data: The data to update or create
            data_field: The field in the data dict to match against
            notion_field: The field in Notion to match against
            use_two_day_period: Whether to check both the current and previous day for matches
        """
        logger.info("Running update or create sync...")

        field_mappings = self.config["field_mappings"]
        properties = self.build_properties(field_mappings, data)

        # Get the pages for the specified period from the database
        pages = self.get_pages_two_day_period(date_str) if use_two_day_period else self.get_pages(date_str)
        matching = [page for page in pages if page['properties'][notion_field]['number'] == data[data_field]]

        if matching:  # Ensures there is at least one match before accessing index 0
            matching_id = matching[0]['id']
            logger.info("Match found. Updating page")
            self.client.pages.update(page_id=matching_id, properties=properties)
            logger.info("Page updated.")
        else:
            logger.info("No matching pages found. Creating a new page.")
            self.create_page(data)
    
if __name__ == "__main__":
    logger.info("Notion Client")
