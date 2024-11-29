import os
import yaml
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()


class NotionClient:
    def __init__(self, config_path: str):
        self.client = Client(auth=os.environ.get("NOTION_API_KEY"))
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file).get("notion")

    def get_database_config(self, integration_name: str):
        integrations = self.config.get("integrations")
        if integration_name not in integrations:
            raise ValueError(f"No configuration found for integration {integration_name}")
        return integrations[integration_name]

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
        print("RESULTS", response)
        results = response.get("results", [])

        if results:
            return results[0]["id"]
        return None

    def build_properties(self, field_mappings, data: dict):
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
                else:
                    raise ValueError(f"Unsupported field type: {field_type}")

            except KeyError as e:
                raise ValueError(f"Error processing field '{field}': {e}") from e
            except Exception as e:
                raise ValueError(f"Unexpected error processing field '{field}': {e}") from e

        return properties

    def create_page(self, integration_name: str, data: dict):
        integration_config = self.get_database_config(integration_name)

        database_id = integration_config["database_id"]
        field_mappings = integration_config["field_mappings"]
        properties = self.build_properties(field_mappings, data)

        return self.client.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )


if __name__ == "__main__":
    print("Notion Client")
