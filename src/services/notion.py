from pathlib import Path
from integrations.lingq.fetcher import LingQFetcher
import yaml
from notion_client import Client

class NotionClient:
    def __init__(self, token: str, config_path: str):
        self.client = Client(auth=token)
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def get_database_config(self, integration_name: str):
        if integration_name not in self.config:
            raise ValueError(f"No configuration found for integration {integration_name}")
        return self.config[integration_name]

    def build_properties(self, field_mappings, data: dict):
        properties = {}
        for field, config in field_mappings.items():
            field_type = config.get("type")
            label = config["label"]

            if field_type == "date":
                properties[label] = {
                    "date": {"start": data[config["key"]]}
                }
            elif field_type == "number":
                properties[label] = {
                    "number": data[config["key"]]
                }
            elif field_type == "relation":
                relation_database_id = config["relation"]["database_id"]
                # Assume data contains IDs for related entries
                properties[label] = {
                    "relation": [{"id": related_id} for related_id in data.get(config["key"], [])]
                }
            else:
                raise ValueError(f"Unsupported field type: {field_type}")

        return properties

    def create_page(self, integration_name: str, data: dict):
        config = self.get_database_config(integration_name)
        database_id = config["database_id"]
        properties = self.build_properties(config, config["field_mappoings"], data)

        return self.client.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )


if __name__ == "__main__":
    print("Notion Client")
