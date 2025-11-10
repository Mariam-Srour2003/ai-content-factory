from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path
import yaml
from typing import Dict, Optional

from ai_content_factory.utils.exceptions import ConfigurationError

class ProjectConfig(BaseModel):
    name: str
    version: str
    environment: str = "development"
class ModelsConfig(BaseModel):
    primary: str
    secondary: Optional[str] = None
class LLMConfig(BaseModel):
    provider: str
    models: ModelsConfig 
    temperature: float = 0.7
    max_tokens: int = 1024
    timeout_seconds: int = 30

class VectorDBConfig(BaseModel):
    persist_directory: str
    collection_names: Dict[str, str]
    embedding_model: str

class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_file: str = "./logs/app.log"

class AppConfig(BaseSettings):
    project: ProjectConfig
    llm: LLMConfig
    vector_db: VectorDBConfig
    logging: LoggingConfig

    class Config:
        env_prefix = "AICF_"  # allow overrides like AICF_LLM__MODEL
        extra = "ignore"      # ignore unknown fields in YAML


def load_config(path: str = "config.yaml"):
    """
    Load configuration. If `path` is an absolute/relative path it will be used.
    Otherwise we try to load `config.yaml` next to this module.
    """
    config_dir = Path(__file__).parent
    config_path = Path(path) if Path(path).is_file() else config_dir / path

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError as e:
        raise ConfigurationError(f"Failed to load configuration: {e}") from e

    print(f"Raw YAML data: {data}")  # Debug logging

    # Backwards-compatible normalization: allow "llm.model" or "llm.models"
    llm = data.get("llm", {})
    if "model" in llm and "models" not in llm:
        if isinstance(llm["model"], dict):
            llm["models"] = llm.pop("model")
        else:
            llm["models"] = {"primary": llm.pop("model")}
        data["llm"] = llm

    try:
        config = AppConfig(**data)
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration: {e}") from e

    base_dir = Path(__file__).resolve().parent.parent
    config.vector_db.persist_directory = str((base_dir / config.vector_db.persist_directory).resolve())

    print(f"Loaded persist_directory: {config.vector_db.persist_directory}")

    return config