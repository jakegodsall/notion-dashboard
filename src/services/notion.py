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

    def build_properties(self, config: dict, data: dict):
        field_mappings = config["field_mappings"]
        properties = {}

        for field, notion_field in field_mappings.items():
            if field in data:
                properties[notion_field] = {
                    "rich_text": [
                        {"text": {"content": str(data[field])}}
                    ]
                }

        return properties

    def create_page(self, integration_name: str, data: dict):
        config = self.get_database_config(integration_name)
        database_id = config["database_id"]
        properties = self.build_properties(config, data)

        return self.client.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )

