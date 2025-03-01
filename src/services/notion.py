import os
import yaml
import hashlib
from notion_client import Client

from src.utils.logger import get_logger

logger = get_logger()

class NotionClient:
    def __init__(self, config_path: str):
        api_key = os.environ.get("NOTION_API_KEY")
        if not api_key:
            raise ValueError("Notion API key not valid:", api_key)
        self.client = Client(auth=api_key)
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file).get("notion")

    def get_database_config(self, integration_name: str):
        """
        Get the database configuration from the config file.
        """
        integrations = self.config.get("integrations")
        if integration_name not in integrations:
            err_msg = f"No configuration found for integration {integration_name}"
            logger.error(err_msg)
            raise ValueError(err_msg)
        logger.info("Notion database config loaded.")
        return integrations[integration_name]
    
    def get_existing_records(self, integration_name, date_str):
        """
        Fetch existing Notion records for a given date and return a {hash: record} mapping
        """
        integration_config = self.get_database_config(integration_name)
        database_id = integration_config['database_id']

        response = self.client.databases.query(
            database_id=database_id,
            filter={"property": "Date", "date": {"equals": date_str}}
        )

        existing_records = response.get("results", [])
        return {record["properties"]["Custom ID"]["rich_text"][0]["text"]["content"]: record 
                    for record in existing_records if "Custom ID" in record["properties"]}
    
    def get_related_id(self, related_database_id, key, value):
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

    def create_page(self, integration_name: str, data: dict):
        """Create a new page in Notion with a custom ID."""
        integration_config = self.get_database_config(integration_name)
        database_id = integration_config["database_id"]
        field_mappings = integration_config["field_mappings"]
        properties = self.build_properties(field_mappings, data)

        resp = self.client.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        logger.info(f"Page created in the database: {database_id}")
        return resp
    
    def update_page(self, page_id, integration_name, data: dict):
        """Update an existing Notion record if data has changed."""
        integration_config = self.get_database_config(integration_name)
        field_mappings = integration_config["field_mappings"]
        properties = self.build_properties(field_mappings, data)

        return self.client.pages.update(
            page_id=page_id,
            properties=properties
        )

if __name__ == "__main__":
    logger.info("Notion Client")
