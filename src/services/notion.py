import os
import yaml
import datetime
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
                        raise KeyError(f"Missing key '{config['key']}' in data for 'number' field.")
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
    
    def get_pages(self, isodate: str):
        """Get pages from the Notion database for the given day."""
        logger.info("Getting pages for the database id...")

        # Ensure the date is in YYYY-MM-DD format
        try:
            isodate = datetime.strptime(isodate, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            logger.error(f'Invalid date format: {isodate}. Expected YYYY-MM-DD')

        database_id = self.config["database_id"]

        pages = self.client.databases.query(**{
            "database_id": database_id,
            "filter": {
                "property": "Date",
                "date": {
                    "equals": isodate
                }
            }
        })
        
        return pages.get('results', [])

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
    
    def update_or_create_page(self, data: dict, compare_field: str):
        """Check the pages from the database for the last day and update the record if present,
        create if not."""
        logger.info("Running update or create sync...")
        database_id = self.config["database_id"]
        field_mappings = self.config["field_mappings"]
        properties = self.build_properties(field_mappings, data)
    
if __name__ == "__main__":
    logger.info("Notion Client")
