"""Script to load brand voice samples into ChromaDB."""

import json
from pathlib import Path
from typing import Dict, List

from ..config.config_loader import load_config
from ..database.chroma_manager import VectorStoreHybrid
from ..utils.logger import get_logger, setup_logging

# Setup logging
setup_logging(log_level="INFO")
logger = get_logger(__name__)


def load_brand_voice_samples(json_file: Path) -> List[Dict]:
    """Load brand voice samples from JSON file.

    Args:
        json_file: Path to the JSON file

    Returns:
        List of brand voice examples
    """
    logger.info(f"Loading brand voice samples from {json_file}")

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    examples = data.get("brand_voice_examples", [])
    logger.info(f"✓ Loaded {len(examples)} brand voice examples")

    return examples


def prepare_documents(examples: List[Dict]) -> tuple[List[str], List[Dict], List[str]]:
    """Prepare documents for ChromaDB ingestion.

    Args:
        examples: List of brand voice example dicts

    Returns:
        Tuple of (texts, metadatas, ids)
    """
    texts = []
    metadatas = []
    ids = []

    for example in examples:
        # The text to embed and search
        text = f"{example['title']}\n\n{example['content']}"
        texts.append(text)

        # Metadata for filtering and context
        metadata = {
            "id": example["id"],
            "content_type": example["content_type"],
            "title": example["title"],
            "voice_characteristics": ",".join(example.get("voice_characteristics", [])),
            "formal_casual": example.get("tone_rating", {}).get("formal_casual", 3),
            "serious_playful": example.get("tone_rating", {}).get("serious_playful", 2),
            "clinical_emotional": example.get("tone_rating", {}).get("clinical_emotional", 2),
        }
        metadatas.append(metadata)

        # Use the example ID as the document ID
        ids.append(example["id"])

    logger.info(f"✓ Prepared {len(texts)} documents for ingestion")
    return texts, metadatas, ids


def main():
    """Main function to load brand voice samples into ChromaDB."""
    logger.info("="*60)
    logger.info("BRAND VOICE LOADER")
    logger.info("="*60)

    # Get paths
    config = load_config()
    project_root = Path(__file__).parent.parent.parent.parent
    json_file = project_root / "src" / "ai_content_factory" / "sample_data" / "brand_voice_samples.json"

    if not json_file.exists():
        logger.error(f"Brand voice samples file not found: {json_file}")
        return

    # Load samples
    examples = load_brand_voice_samples(json_file)

    if not examples:
        logger.error("No examples found in JSON file")
        return

    # Prepare documents
    texts, metadatas, ids = prepare_documents(examples)

    # Initialize vector store
    logger.info("Initializing ChromaDB...")
    db_manager = VectorStoreHybrid()

    # Get collection name from config
    collection_name = config.vector_db.collection_names.get("brand_voice", "brand_voice_examples")

    # Check if collection exists and delete it (to avoid duplicates)
    existing_collections = db_manager.list_collections()
    if collection_name in existing_collections:
        logger.info(f"Collection '{collection_name}' already exists. Deleting...")
        db_manager.delete_collection(collection_name)

    # Add documents
    logger.info(f"Adding {len(texts)} documents to collection '{collection_name}'...")
    count = db_manager.add_documents(
        collection_name=collection_name,
        texts=texts,
        metadatas=metadatas,
        ids=ids
    )

    logger.info(f"✓ Successfully added {count} brand voice examples")

    # Verify by listing collections
    collections = db_manager.list_collections()
    logger.info(f"Available collections: {collections}")

    # Test a query
    logger.info("\nTesting retrieval...")
    results = db_manager.query(
        collection_name=collection_name,
        query_text="skincare routine",
        k=3
    )

    logger.info(f"✓ Retrieved {len(results)} examples for test query 'skincare routine'")
    for i, doc in enumerate(results, 1):
        logger.info(f"  {i}. {doc.metadata.get('title', 'Untitled')} ({doc.metadata.get('content_type', 'unknown')})")

    logger.info("\n" + "="*60)
    logger.info("✅ BRAND VOICE LOADING COMPLETE")
    logger.info("="*60)


if __name__ == "__main__":
    main()
