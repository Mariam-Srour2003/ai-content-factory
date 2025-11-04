from pydantic import BaseModel
from pydantic_settings import BaseSettings
import yaml

class ProjectConfig(BaseModel):
    name: str
    version: str
    environment: str = "development"

class LLMConfig(BaseModel):
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 1024
    timeout_seconds: int = 30

class VectorDBConfig(BaseModel):
    persist_directory: str
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


def load_config(path: str = "config.yaml") -> AppConfig:
    """
    Load configuration from a YAML file into a validated Pydantic model.
    """
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return AppConfig(**data)
