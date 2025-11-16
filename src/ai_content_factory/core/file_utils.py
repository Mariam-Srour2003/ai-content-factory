# src/ai_content_factory/core/file_utils.py
import os
import json

def ensure_directory_exists(file_path: str):
    """Ensure the directory for a file path exists"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return file_path

def safe_json_dump(data, file_path: str, indent: int = 2):
    """Safely dump JSON data to file, creating directories if needed"""
    ensure_directory_exists(file_path)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def safe_yaml_dump(data, file_path: str):
    """Safely dump YAML data to file, creating directories if needed"""
    import yaml
    ensure_directory_exists(file_path)
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False)