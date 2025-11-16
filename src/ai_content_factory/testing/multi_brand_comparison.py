# src/ai_content_factory/testing/multi_brand_comparison.py
from typing import Dict, List
import json
from ..core.brand_config import list_available_brands, get_brand_config
from .brand_testing_framework import BrandTestingFramework

class MultiBrandComparator:
    def __init__(self):
        self.testing_framework = BrandTestingFramework()
    
    def compare_all_brands(self, test_content: str = None):
        """Compare all available brands with the same test content"""
        brands = list_available_brands()
        results = {}
        
        print("🔍 MULTI-BRAND COMPARISON ANALYSIS")
        print("=" * 70)
        
        if test_content:
            print(f"Test Content: '{test_content}'")
            print("=" * 70)
        
        for brand_key in brands:
            print(f"\n🧪 Testing {brand_key}...")
            brand_results = self.testing_framework.test_brand_consistency(brand_key)
            results[brand_key] = brand_results
        
        self._generate_comparison_report(results, test_content)
        return results
    
    def test_content_across_brands(self, content_samples: List[str]):
        """Test the same content samples across all brands"""
        results = {}
        
        print("📝 CONTENT ANALYSIS ACROSS BRANDS")
        print("=" * 70)
        
        for content in content_samples:
            print(f"\n📄 Analyzing: '{content[:80]}...'")
            brand_analysis = {}
            
            for brand_key in list_available_brands():
                brand_config = get_brand_config(brand_key)
                # Simplified analysis for demonstration
                brand_analysis[brand_key] = {
                    "suitability": self._assess_content_suitability(content, brand_config),
                    "recommended_tone": self._suggest_tone(content, brand_config),
                    "consistency_score": self._estimate_consistency(content, brand_config)
                }
            
            results[content] = brand_analysis
            self._print_content_analysis(content, brand_analysis)
        
        return results
    
    def _assess_content_suitability(self, content: str, brand_config) -> str:
        """Assess how suitable content is for a brand"""
        content_lower = content.lower()
        
        # Check for prohibited phrases
        for phrase in brand_config.prohibited_phrases:
            if phrase.lower() in content_lower:
                return "Poor"
        
        # Check tone alignment
        if any(tone_word in content_lower for tone_word in ["awesome", "epic", "crushing"]):
            return "Excellent" if "tech_startup" in brand_config.name else "Poor"
        
        if any(tone_word in content_lower for tone_word in ["pleased to announce", "board of directors"]):
            return "Excellent" if "corporate_finance" in brand_config.name else "Poor"
        
        return "Moderate"
    
    def _suggest_tone(self, content: str, brand_config) -> str:
        """Suggest the best tone for content within brand guidelines"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["urgent", "immediate", "critical"]):
            return "authoritative" if "corporate_finance" in brand_config.name else "action_oriented"
        
        if any(word in content_lower for word in ["excited", "awesome", "great"]):
            return "enthusiastic" if "tech_startup" in brand_config.name else "inspirational"
        
        return brand_config.supported_tones[0]  # Default to first supported tone
    
    def _estimate_consistency(self, content: str, brand_config) -> float:
        """Estimate consistency score (simplified)"""
        score = 0.5  # Base score
        
        # Positive indicators
        for phrase in brand_config.preferred_phrases:
            if phrase.lower() in content.lower():
                score += 0.2
                break
        
        # Negative indicators  
        for phrase in brand_config.prohibited_phrases:
            if phrase.lower() in content.lower():
                score -= 0.3
                break
        
        return max(0.0, min(1.0, score))
    
    def _print_content_analysis(self, content: str, brand_analysis: Dict):
        """Print analysis results for content"""
        print(f"   Brand Compatibility Analysis:")
        for brand_key, analysis in brand_analysis.items():
            print(f"     • {brand_key:15} | Suitability: {analysis['suitability']:8} | "
                  f"Score: {analysis['consistency_score']:.1f} | "
                  f"Tone: {analysis['recommended_tone']}")
    
    def _generate_comparison_report(self, results: Dict, test_content: str = None):
        """Generate comprehensive comparison report"""
        report = {
            "comparison_timestamp": "2024-01-01",  # Would use datetime in real implementation
            "test_content": test_content,
            "brand_performance": {},
            "recommendations": {}
        }
        
        for brand_key, brand_results in results.items():
            summary = brand_results.get("summary", {})
            total_tests = summary.get("total_tests", 0)
            consistent_count = summary.get("consistent_count", 0)
            
            report["brand_performance"][brand_key] = {
                "consistency_rate": consistent_count / total_tests if total_tests > 0 else 0,
                "total_tests": total_tests,
                "voice_characteristics": brand_results.get("brand_configuration", {}).get("voice_characteristics", [])
            }
        
        # Generate recommendations
        best_brand = max(report["brand_performance"].items(), 
                        key=lambda x: x[1]["consistency_rate"])
        
        report["recommendations"] = {
            "best_performing_brand": best_brand[0],
            "consistency_rate": best_brand[1]["consistency_rate"],
            "suggested_use_cases": self._suggest_use_cases(report["brand_performance"])
        }
        
        # Save report
        with open("data/brand_comparison_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        self._print_comparison_summary(report)
    
    def _suggest_use_cases(self, performance_data: Dict) -> Dict[str, str]:
        """Suggest best use cases for each brand"""
        return {
            "tech_startup": "Product launches, team communications, user onboarding",
            "corporate_finance": "Financial reports, investor communications, formal announcements",
            "health_wellness": "Educational content, community support, product information",
            "eco_brand": "Campaign messaging, community engagement, impact reports"
        }
    
    def _print_comparison_summary(self, report: Dict):
        """Print comparison summary"""
        print("\n" + "=" * 70)
        print("📈 BRAND COMPARISON SUMMARY")
        print("=" * 70)
        
        for brand, performance in report["brand_performance"].items():
            rate = performance["consistency_rate"]
            print(f"   {brand:20} | Consistency: {rate:6.1%} | Tests: {performance['total_tests']:2d}")
        
        print(f"\n🏆 BEST PERFORMER: {report['recommendations']['best_performing_brand']}")
        print(f"   Consistency Rate: {report['recommendations']['consistency_rate']:.1%}")