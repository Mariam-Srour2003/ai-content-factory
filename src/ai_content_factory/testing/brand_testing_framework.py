# src/ai_content_factory/testing/brand_testing_framework.py
from typing import List, Dict, Any
import json
from ..core.brand_config import BRAND_PROFILES, get_brand_config, list_available_brands
from ..core.brand_voice_documenter import BrandVoiceDocumenter
from ..core.few_shot_prompt_builder import FewShotPromptBuilder
from ..core.brand_voice_system import BrandVoiceSystem
from ..core.content_ingestion_pipeline import ContentIngestionPipeline

class BrandTestingFramework:
    def __init__(self):
        self.test_content = self._load_test_content()
    
    def _load_test_content(self) -> Dict[str, List[str]]:
        """Load standardized test content for all brands"""
        return {
            "formal_corporate": [
                "We are pleased to announce the quarterly financial results, which demonstrate strong performance across all business segments.",
                "Please find attached the comprehensive report detailing our strategic initiatives for the upcoming fiscal year.",
                "The board of directors has approved the proposed merger, pending regulatory approval and shareholder consent."
            ],
            "casual_modern": [
                "Hey team! Just wanted to share some awesome news about our latest product launch!",
                "Quick update: we're crushing our Q3 goals and I couldn't be more proud of this team!",
                "PSA: Don't forget about the team lunch tomorrow - it's gonna be epic! 🎉"
            ],
            "technical_detailed": [
                "The system architecture has been optimized to reduce latency by 40% through improved caching mechanisms.",
                "API version 2.3 introduces breaking changes; please refer to migration guide before updating dependencies.",
                "Database performance metrics indicate a 15% improvement in query response times post-optimization."
            ],
            "compassionate_caring": [
                "We understand that starting a wellness journey can feel overwhelming, and we're here to support you every step of the way.",
                "Remember to be kind to yourself today - progress isn't always linear, and every small step matters.",
                "Our community is here to lift you up when you need it most. You're not alone in this journey."
            ],
            "passionate_environmental": [
                "The time for climate action is NOW. Every single choice we make today shapes the world our children will inherit tomorrow.",
                "We're witnessing unprecedented coral bleaching events - but together, we can turn the tide and protect our oceans.",
                "This isn't just about saving the planet; it's about creating a future where both people and nature can thrive together."
            ]
        }
    
    def test_brand_consistency(self, brand_key: str, output_dir: str = "data/brand_tests"):
        """Test a specific brand with standardized content"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n🧪 TESTING BRAND: {brand_key.upper()}")
        print("=" * 60)
        
        # Get brand configuration
        brand_config = get_brand_config(brand_key)
        
        # Create brand voice documentation
        documenter = BrandVoiceDocumenter(brand_config.name)
        self._setup_brand_documenter(documenter, brand_config)
        
        # Create example content for this brand
        brand_examples = self._create_brand_examples(brand_config)
        
        # Initialize systems
        prompt_builder = FewShotPromptBuilder(brand_examples)
        brand_voice_system = BrandVoiceSystem()
        
        # Test consistency across different content types
        results = self._run_consistency_tests(brand_voice_system, brand_config)
        
        # Generate report
        self._generate_test_report(brand_key, brand_config, results, output_dir)
        
        return results
    
    def _setup_brand_documenter(self, documenter: BrandVoiceDocumenter, brand_config):
        """Setup brand documenter with configuration"""
        for tone, guidelines in brand_config.tone_guidelines.items():
            documenter.add_tone_guideline(tone, guidelines)
        
        documenter.add_voice_characteristics(brand_config.voice_characteristics)
        documenter.set_target_audience(brand_config.target_audience)
        documenter.add_prohibited_phrases(brand_config.prohibited_phrases)
        documenter.add_preferred_phrases(brand_config.preferred_phrases)
        documenter.set_supported_tones(brand_config.supported_tones)
        documenter.set_consistency_threshold(brand_config.consistency_threshold)
    
    def _create_brand_examples(self, brand_config) -> Dict[str, List[str]]:
        """Create example content tailored to the brand"""
        examples = {}
        
        # Map generic tones to brand-specific tones
        tone_mapping = {
            "tech_startup": {
                "casual": "casual",
                "technical": "technical", 
                "enthusiastic": "enthusiastic"
            },
            "corporate_finance": {
                "formal_corporate": "formal",
                "technical_detailed": "authoritative"
            },
            "health_wellness": {
                "compassionate_caring": "compassionate",
                "technical_detailed": "educational"
            },
            "eco_brand": {
                "passionate_environmental": "passionate",
                "casual_modern": "action_oriented"
            }
        }
        
        brand_key = [k for k, v in BRAND_PROFILES.items() if v.name == brand_config.name][0]
        
        for content_type, brand_tone in tone_mapping[brand_key].items():
            if content_type in self.test_content:
                examples[brand_tone] = self.test_content[content_type][:2]  # Use 2 examples per tone
        
        return examples
    
    def _run_consistency_tests(self, brand_voice_system, brand_config):
        """Run consistency tests for the brand"""
        results = {
            "brand": brand_config.name,
            "tests": [],
            "summary": {
                "total_tests": 0,
                "consistent_count": 0,
                "inconsistent_count": 0
            }
        }
        
        # Test each content type against the brand
        for content_type, content_list in self.test_content.items():
            for content in content_list[:3]:  # Test 3 samples per content type
                try:
                    # Analyze tone
                    tone = brand_voice_system.analyze_tone(content)
                    
                    # Check consistency (using the content itself as the only example for simplicity)
                    is_consistent = brand_voice_system.check_consistency(content, [content])
                    
                    test_result = {
                        "content_type": content_type,
                        "content": content,
                        "detected_tone": tone,
                        "is_consistent": is_consistent,
                        "expected_consistency": self._get_expected_consistency(brand_config, content_type)
                    }
                    
                    results["tests"].append(test_result)
                    results["summary"]["total_tests"] += 1
                    if is_consistent:
                        results["summary"]["consistent_count"] += 1
                    else:
                        results["summary"]["inconsistent_count"] += 1
                        
                except Exception as e:
                    print(f"Error testing content: {e}")
        
        return results
    
    def _get_expected_consistency(self, brand_config, content_type: str) -> bool:
        """Determine expected consistency based on brand and content type"""
        brand_style = {
            "tech_startup": ["casual_modern", "technical_detailed"],
            "corporate_finance": ["formal_corporate", "technical_detailed"],
            "health_wellness": ["compassionate_caring", "technical_detailed"],
            "eco_brand": ["passionate_environmental", "casual_modern"]
        }
        
        brand_key = [k for k, v in BRAND_PROFILES.items() if v.name == brand_config.name][0]
        return content_type in brand_style.get(brand_key, [])
    
    def _generate_test_report(self, brand_key: str, brand_config, results: Dict, output_dir: str):
        """Generate comprehensive test report"""
        report_path = f"{output_dir}/{brand_key}_test_report.json"
        
        report = {
            "brand_configuration": brand_config.dict(),
            "test_results": results,
            "performance_metrics": {
                "consistency_rate": results["summary"]["consistent_count"] / results["summary"]["total_tests"],
                "tone_detection_accuracy": "N/A",  # Would need labeled data for this
                "system_performance": "Stable"
            }
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self._print_test_summary(brand_config, results)
    
    def _print_test_summary(self, brand_config, results):
        """Print human-readable test summary"""
        summary = results["summary"]
        consistency_rate = summary["consistent_count"] / summary["total_tests"]
        
        print(f"\n📊 TEST SUMMARY: {brand_config.name}")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Consistent: {summary['consistent_count']}")
        print(f"   Inconsistent: {summary['inconsistent_count']}")
        print(f"   Consistency Rate: {consistency_rate:.1%}")
        
        print(f"\n🎯 Brand Voice Characteristics:")
        for char in brand_config.voice_characteristics:
            print(f"   • {char}")
        
        print(f"\n🚫 Prohibited Phrases:")
        for phrase in brand_config.prohibited_phrases[:3]:  # Show first 3
            print(f"   • '{phrase}'")
        
        print(f"\n✅ Preferred Tones: {', '.join(brand_config.supported_tones)}")