"""
Script to generate and store embeddings for brand voice samples.
This script processes brand voice JSON files and stores them in ChromaDB
for later retrieval by the content writer agent.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

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

    # Handle both formats: list of samples or dict with "brand_voice_examples" key
    if isinstance(data, list):
        examples = data
    elif isinstance(data, dict) and "brand_voice_examples" in data:
        examples = data.get("brand_voice_examples", [])
    else:
        examples = [data]

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
        # The text to embed and search - combine title and content
        title = example.get('title', '')
        content = example.get('content', '')
        text = f"{title}\n\n{content}" if title else content
        texts.append(text)

        # Metadata for filtering and context
        metadata = {
            "id": example.get("id", f"sample_{len(ids)}"),
            "content_type": example.get("content_type", "unknown"),
            "title": title,
            "tone": example.get("tone", "neutral"),
            "platform": example.get("platform", "general"),
            "word_count": example.get("word_count", len(content.split())),
        }

        # Add optional fields if they exist
        if "voice_characteristics" in example:
            metadata["voice_characteristics"] = ",".join(example["voice_characteristics"])
        if "key_phrases" in example:
            metadata["key_phrases"] = ",".join(example["key_phrases"])
        if "tone_rating" in example:
            metadata["formal_casual"] = example["tone_rating"].get("formal_casual", 3)
            metadata["serious_playful"] = example["tone_rating"].get("serious_playful", 2)
            metadata["clinical_emotional"] = example["tone_rating"].get("clinical_emotional", 2)

        metadatas.append(metadata)

        # Use the example ID as the document ID
        ids.append(example.get("id", f"sample_{len(ids)}"))

    logger.info(f"✓ Prepared {len(texts)} documents for ingestion")
    return texts, metadatas, ids


def main():
    """Main function to load brand voice samples into ChromaDB."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate brand voice embeddings from JSON file')
    parser.add_argument(
        '--input', '-i',
        help='Path to brand voice JSON file',
        default=None
    )
    parser.add_argument(
        '--collection', '-c',
        help='ChromaDB collection name',
        default=None
    )

    args = parser.parse_args()

    logger.info("="*60)
    logger.info("BRAND VOICE EMBEDDING GENERATOR")
    logger.info("="*60)

    # Get paths
    config = load_config()

    # Determine input file
    if args.input:
        json_file = Path(args.input)
    else:
        project_root = Path(__file__).parent.parent.parent.parent
        json_file = project_root / "src" / "ai_content_factory" / "sample_data" / "brand_voice_samples.json"

    if not json_file.exists():
        logger.error(f"Brand voice samples file not found: {json_file}")
        return

    logger.info(f"Input file: {json_file}")

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

    # Get collection name
    collection_name = args.collection or config.vector_db.collection_names.get("brand_voice", "brand_voice_examples")

    # Check if collection exists and delete it (to avoid duplicates)
    existing_collections = db_manager.list_collections()
    if collection_name in existing_collections:
        logger.info(f"Collection '{collection_name}' already exists. Deleting...")
        db_manager.delete_collection(collection_name)

    # Add documents (embeddings are generated automatically by LangChain)
    logger.info(f"Adding {len(texts)} documents to collection '{collection_name}'...")
    logger.info("Generating embeddings using Ollama (this may take a moment)...")

    count = db_manager.add_documents(
        collection_name=collection_name,
        texts=texts,
        metadatas=metadatas,
        ids=ids
    )

    logger.info(f"✓ Successfully added {count} brand voice examples with embeddings")

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
        title = doc.metadata.get('title', 'Untitled')
        content_type = doc.metadata.get('content_type', 'unknown')
        logger.info(f"  {i}. {title} ({content_type})")

    logger.info("\n" + "="*60)
    logger.info("✅ BRAND VOICE EMBEDDING GENERATION COMPLETE")
    logger.info("="*60)


if __name__ == "__main__":
    main()
