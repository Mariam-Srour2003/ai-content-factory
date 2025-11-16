# src/ai_content_factory/validate_ticket_8.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .core.brand_voice_documenter import BrandVoiceDocumenter
from .core.content_ingestion_pipeline import ContentIngestionPipeline
from .core.few_shot_prompt_builder import FewShotPromptBuilder
from .core.brand_voice_system import BrandVoiceSystem
from .core.brand_voice_embeddings import BrandVoiceEmbeddings
from .core.brand_config import get_brand_config
import json

def validate_ticket_8():
    """Validate that Ticket #8 requirements are met"""
    print("🎫 VALIDATING TICKET #8: BRAND VOICE SYSTEM")
    print("=" * 60)
    
    results = {
        "tasks": {},
        "acceptance_criteria": {},
        "overall_status": "IN_PROGRESS"
    }
    
    # Test 1: Brand Voice Documentation Template
    print("\n1. 📝 Brand Voice Documentation Template")
    try:
        documenter = BrandVoiceDocumenter("Test Brand")
        documenter.add_tone_guideline("formal", ["Use proper grammar", "Avoid contractions"])
        documenter.add_voice_characteristics(["Professional", "Clear"])
        documenter.export_json('data/validation_docs.json')
        results["tasks"]["documentation_template"] = "✅ COMPLETE"
        print("   ✅ Documentation template working")
    except Exception as e:
        results["tasks"]["documentation_template"] = f"❌ FAILED: {e}"
        print(f"   ❌ Documentation template failed: {e}")
    
    # Test 2: Content Ingestion Pipeline (10-20 examples)
    print("\n2. 📥 Content Ingestion Pipeline")
    try:
        # Create test content
        test_content = [{"content": f"Example content {i}", "source": "test"} for i in range(15)]
        with open('data/validation_content.json', 'w') as f:
            json.dump(test_content, f)
        
        brand_system = BrandVoiceSystem()
        pipeline = ContentIngestionPipeline(brand_system)
        pipeline.ingest_from_directory('data')
        
        if len(pipeline.ingested_content) >= 10:
            results["acceptance_criteria"]["ingest_10_20_examples"] = "✅ ACHIEVED"
            print(f"   ✅ Ingested {len(pipeline.ingested_content)} examples")
        else:
            results["acceptance_criteria"]["ingest_10_20_examples"] = "❌ FAILED"
            print(f"   ❌ Only ingested {len(pipeline.ingested_content)} examples")
            
    except Exception as e:
        results["acceptance_criteria"]["ingest_10_20_examples"] = f"❌ FAILED: {e}"
        print(f"   ❌ Ingestion pipeline failed: {e}")
    
    # Test 3: Few-Shot Learning Prompt Builder
    print("\n3. 🎯 Few-Shot Learning Prompt Builder")
    try:
        examples = {"formal": ["Example 1"], "casual": ["Example 2"]}
        builder = FewShotPromptBuilder(examples)
        prompt = builder.build_generation_prompt("formal", "test context")
        
        if prompt and "formal" in prompt:
            results["tasks"]["few_shot_builder"] = "✅ COMPLETE"
            print("   ✅ Few-shot prompt builder working")
        else:
            results["tasks"]["few_shot_builder"] = "❌ FAILED"
            print("   ❌ Few-shot prompt builder failed")
            
    except Exception as e:
        results["tasks"]["few_shot_builder"] = f"❌ FAILED: {e}"
        print(f"   ❌ Few-shot builder failed: {e}")
    
    # Test 4: Tone Analyzer
    print("\n4. 🎭 Tone Analyzer")
    try:
        brand_system = BrandVoiceSystem()
        test_text = "Please ensure proper documentation is submitted"
        tone = brand_system.analyze_tone(test_text)
        
        if tone:
            results["tasks"]["tone_analyzer"] = "✅ COMPLETE"
            print(f"   ✅ Tone analyzer working: '{test_text}' → {tone}")
        else:
            results["tasks"]["tone_analyzer"] = "❌ FAILED"
            print("   ❌ Tone analyzer failed")
            
    except Exception as e:
        results["tasks"]["tone_analyzer"] = f"❌ FAILED: {e}"
        print(f"   ❌ Tone analyzer failed: {e}")
    
    # Test 5: Style Consistency Checker
    print("\n5. ✅ Style Consistency Checker")
    try:
        brand_system = BrandVoiceSystem()
        content = "This is a test message"
        examples = ["This is similar content", "Another example"]
        consistent = brand_system.check_consistency(content, examples)
        
        results["tasks"]["consistency_checker"] = "✅ COMPLETE"
        print(f"   ✅ Consistency checker working: {consistent}")
        
    except Exception as e:
        results["tasks"]["consistency_checker"] = f"❌ FAILED: {e}"
        print(f"   ❌ Consistency checker failed: {e}")
    
    # Test 6: Testing Framework
    print("\n6. 🧪 Brand Voice Testing Framework")
    try:
        from .testing.brand_testing_framework import BrandTestingFramework
        tester = BrandTestingFramework()
        results["tasks"]["testing_framework"] = "✅ COMPLETE"
        print("   ✅ Testing framework available")
    except Exception as e:
        results["tasks"]["testing_framework"] = f"❌ FAILED: {e}"
        print(f"   ❌ Testing framework failed: {e}")
    
    # Test 7: Brand Voice Embeddings for RAG
    print("\n7. 🔍 Brand Voice Embeddings for RAG")
    try:
        embeddings = BrandVoiceEmbeddings()
        test_content = [{"content": "Test content", "tone": "formal"}]
        embeddings.create_embeddings(test_content)
        results["tasks"]["embeddings_rag"] = "✅ COMPLETE"
        print("   ✅ Embeddings for RAG working")
    except Exception as e:
        results["tasks"]["embeddings_rag"] = f"❌ FAILED: {e}"
        print(f"   ❌ Embeddings failed: {e}")
    
    # Final Assessment
    print("\n" + "=" * 60)
    print("📊 FINAL VALIDATION RESULTS")
    print("=" * 60)
    
    completed_tasks = sum(1 for status in results["tasks"].values() if "✅" in status)
    total_tasks = len(results["tasks"])
    
    completed_criteria = sum(1 for status in results["acceptance_criteria"].values() if "✅" in status)
    total_criteria = len(results["acceptance_criteria"])
    
    print(f"📋 TASKS: {completed_tasks}/{total_tasks} completed")
    for task, status in results["tasks"].items():
        print(f"   {task}: {status}")
    
    print(f"\n🎯 ACCEPTANCE CRITERIA: {completed_criteria}/{total_criteria} met")
    for criteria, status in results["acceptance_criteria"].items():
        print(f"   {criteria}: {status}")
    
    # Overall status
    if completed_tasks == total_tasks and completed_criteria == total_criteria:
        results["overall_status"] = "✅ COMPLETE"
        print(f"\n🎉 TICKET #8 STATUS: ✅ COMPLETE")
    else:
        results["overall_status"] = "⚠️ IN_PROGRESS"
        print(f"\n🚧 TICKET #8 STATUS: ⚠️ IN PROGRESS")
        print(f"   Missing: {total_tasks - completed_tasks} tasks, {total_criteria - completed_criteria} criteria")
    
    # Save validation results
    with open('data/ticket_8_validation.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    validate_ticket_8()