# src/ai_content_factory/core/ingestors/example_content_ingestor.py
import os
import json

class ExampleContentIngestor:
    def __init__(self, file_name):
        self.file_name = file_name

    def ingest(self):
        # Get the absolute path to the 'data' folder at the root of the project
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        file_path = os.path.join(project_root, self.file_name)

        # Check if the file exists before opening it
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist!")
        
        # Open and read the file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Return the original dictionary structure
        return data