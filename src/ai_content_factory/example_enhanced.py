# src/ai_content_factory/example_enhanced_fixed.py
from ai_content_factory.core.brand_voice_documenter import BrandVoiceDocumenter, create_brand_voice_template
from ai_content_factory.core.few_shot_prompt_builder import FewShotPromptBuilder
from ai_content_factory.core.content_ingestion_pipeline import ContentIngestionPipeline
from ai_content_factory.core.brand_voice_embeddings import BrandVoiceEmbeddings, BrandVoiceRAG
from ai_content_factory.core.brand_voice_system import BrandVoiceSystem
from ai_content_factory.core.file_utils import ensure_directory_exists, safe_json_dump
import json
import os
import sys

def setup_directories():
    """Create all necessary directories"""
    directories = [
        'data',
        'data/sample_content',
        'data/embeddings',
        'data/exports'
    ]
    
    for directory in directories:
        ensure_directory_exists(directory + '/.keep')
    print("✓ Directory structure created")

def create_sample_content():
    """Create sample content for testing"""
    sample_content = [
        {
            "content": "We are excited to announce our new product line! This represents a significant advancement in our technology stack.",
            "source": "marketing_announcement",
            "tone": "casual"
        },
        {
            "content": "Please find attached the quarterly report for your review. The document contains detailed analysis of Q3 performance metrics.",
            "source": "quarterly_report", 
            "tone": "formal"
        },
        {
            "content": "The system requires immediate maintenance to prevent potential downtime. Please schedule the update during off-peak hours.",
            "source": "system_alert",
            "tone": "technical"
        },
        {
            "content": "URGENT: Server cluster experiencing latency issues. Immediate intervention required to maintain service levels.",
            "source": "urgent_alert",
            "tone": "urgent"
        },
        {
            "content": "Hey team, great work on the recent deployment! Let's celebrate this milestone with a team lunch next week.",
            "source": "team_communication",
            "tone": "casual"
        },
        {
            "content": "The API endpoints have been updated to version 2.1. Please refer to the updated documentation for migration guidelines.",
            "source": "technical_update",
            "tone": "technical"
        }
    ]
    
    safe_json_dump(sample_content, 'data/sample_content/content_samples.json')
    print("✓ Sample content created")
    return sample_content

def demonstrate_complete_system():
    print("COMPLETE BRAND VOICE MANAGEMENT SYSTEM")
    print("=" * 60)
    
    # Setup directories first
    print("\n1. SETTING UP DIRECTORY STRUCTURE")
    setup_directories()
    
    # 1. Create Brand Voice Documentation
    print("\n2. CREATING BRAND VOICE DOCUMENTATION")
    documenter = create_brand_voice_template()
    
    # Export documentation
    documenter.export_json('data/brand_voice_documentation.json')
    print("✓ Brand voice documentation exported")
    
    # 2. Load or create brand voice examples
    print("\n3. SETTING UP BRAND VOICE EXAMPLES")
    try:
        with open('data/brand_voice_examples.json', 'r') as f:
            brand_voice_examples = json.load(f)
        print("✓ Loaded existing brand voice examples")
    except FileNotFoundError:
        # Create default examples if file doesn't exist
        brand_voice_examples = {
            "formal": [
                "Please ensure that your response is both thorough and precise.",
                "We appreciate your cooperation in this matter.",
                "Kindly submit the required documentation at your earliest convenience."
            ],
            "casual": [
                "Hey, could you quickly shoot me an update on this when you get a chance?",
                "Thanks for reaching out! We're here to help.",
                "Great job on the presentation today!"
            ],
            "technical": [
                "Ensure that all parameters are correctly initialized before proceeding.",
                "The system requires a minimum of 8GB RAM for optimal performance.",
                "Please update the dependencies to the latest stable version."
            ],
            "urgent": [
                "Immediate action required to resolve the critical issue.",
                "System downtime expected if not addressed within the hour.",
                "Please prioritize this task above all others."
            ]
        }
        safe_json_dump(brand_voice_examples, 'data/brand_voice_examples.json')
        print("✓ Created default brand voice examples")
    
    # 3. Initialize Few-Shot Prompt Builder
    print("\n4. INITIALIZING FEW-SHOT PROMPT BUILDER")
    prompt_builder = FewShotPromptBuilder(brand_voice_examples)
    
    # Create few-shot dataset
    prompt_builder.create_few_shot_dataset('data/few_shot_dataset.json')
    print("✓ Few-shot dataset created")
    
    # 4. Create sample content for ingestion
    print("\n5. CREATING SAMPLE CONTENT")
    create_sample_content()
    
    # 5. Initialize Content Ingestion Pipeline
    print("\n6. SETTING UP CONTENT INGESTION PIPELINE")
    try:
        brand_voice_system = BrandVoiceSystem()
        ingestion_pipeline = ContentIngestionPipeline(brand_voice_system)
        
        print("  Ingesting content...")
        # Ingest content
        ingestion_pipeline.ingest_from_directory('data/sample_content')
        ingestion_pipeline.export_analysis('data/content_analysis.json')
        print("✓ Content ingestion completed")
        
        # Show ingestion results
        print(f"  - Ingested {len(ingestion_pipeline.ingested_content)} content items")
        tones_dist = ingestion_pipeline._get_tones_distribution()
        print(f"  - Tone distribution: {tones_dist}")
        consistency_rate = ingestion_pipeline._get_consistency_rate()
        print(f"  - Consistency rate: {consistency_rate:.2%}")
        
    except Exception as e:
        print(f"⚠ Content ingestion pipeline failed: {e}")
        ingestion_pipeline = None
        return
    
    # 6. Create Brand Voice Embeddings
    print("\n7. CREATING BRAND VOICE EMBEDDINGS")
    try:
        if ingestion_pipeline and ingestion_pipeline.ingested_content:
            embeddings = BrandVoiceEmbeddings()
            print("  Generating embeddings...")
            embeddings.create_embeddings(ingestion_pipeline.ingested_content)
            print("✓ Brand voice embeddings created")
            
            # Test embedding search
            test_query = "urgent system update required"
            search_results = embeddings.search_similar_content(test_query, top_k=2)
            print(f"✓ Embedding search test successful")
            print(f"  Search for '{test_query}':")
            for i, result in enumerate(search_results, 1):
                print(f"    {i}. {result['content'][:60]}... (Score: {result['similarity_score']:.3f})")
            
            # 7. Initialize RAG System
            print("\n8. INITIALIZING RAG SYSTEM")
            rag_system = BrandVoiceRAG(embeddings, prompt_builder)
            
            # Example RAG query
            test_query = "We need to inform customers about system maintenance"
            rag_prompt = rag_system.generate_rag_prompt(
                query=test_query,
                target_tone="formal",
                context="Scheduled maintenance notification"
            )
            
            print("✓ RAG system initialized")
            print(f"  Example RAG prompt created")
            
        else:
            print("⚠ Embeddings skipped: No content available for embedding")
            
    except Exception as e:
        print(f"⚠ Embeddings creation failed: {e}")
        return
    
    print("\n" + "=" * 60)
    print("🎉 SYSTEM READY: All components integrated successfully!")
    print("=" * 60)
    
    # Show summary
    print("\n📊 SYSTEM SUMMARY:")
    print(f"  • Brand Voice Documentation: ✓ Complete")
    print(f"  • Few-Shot Learning: ✓ {len(brand_voice_examples)} tones configured")
    print(f"  • Content Pipeline: ✓ {len(ingestion_pipeline.ingested_content)} items ingested")
    print(f"  • Embeddings: ✓ {len(ingestion_pipeline.ingested_content)} vectors created")
    print(f"  • RAG System: ✓ Ready for content generation")
    
    # Show created files
    print("\n📁 CREATED FILES:")
    created_files = []
    for root, dirs, files in os.walk('data'):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                created_files.append((file_path, file_size))
    
    for file_path, file_size in sorted(created_files):
        print(f"  📄 {file_path} ({file_size} bytes)")

if __name__ == "__main__":
    try:
        demonstrate_complete_system()
    except Exception as e:
        print(f"\n❌ SYSTEM SETUP FAILED: {e}")
        import traceback
        traceback.print_exc()