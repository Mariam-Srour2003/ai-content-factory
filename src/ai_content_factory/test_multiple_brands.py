# src/ai_content_factory/examples/test_multiple_brands.py
from .testing.multi_brand_comparison import MultiBrandComparator
from .testing.brand_testing_framework import BrandTestingFramework
from .core.brand_config import list_available_brands

def demo_single_brand_test():
    """Test a single brand in detail"""
    print("🔍 SINGLE BRAND DETAILED TEST")
    print("=" * 50)
    
    tester = BrandTestingFramework()
    
    # Test a specific brand
    brand_to_test = "tech_startup"  # Change to any brand key
    results = tester.test_brand_consistency(brand_to_test)
    
    return results

def demo_multi_brand_comparison():
    """Compare all brands"""
    print("\n🔍 MULTI-BRAND COMPARISON")
    print("=" * 50)
    
    comparator = MultiBrandComparator()
    
    # Compare all brands
    results = comparator.compare_all_brands()
    
    return results

def demo_content_analysis():
    """Analyze specific content across all brands"""
    print("\n📝 CONTENT ANALYSIS ACROSS BRANDS")
    print("=" * 50)
    
    comparator = MultiBrandComparator()
    
    test_content_samples = [
        "We're thrilled to announce our groundbreaking new feature that will revolutionize user experience!",
        "The quarterly financial report indicates strong growth across all market segments with a 15% increase in revenue.",
        "Remember to take deep breaths and be kind to yourself during stressful times. Your mental health matters.",
        "Join us in our mission to reduce plastic waste by 50% through community-driven initiatives and sustainable practices."
    ]
    
    results = comparator.test_content_across_brands(test_content_samples)
    
    return results

def demo_brand_recommendation():
    """Get brand recommendations for specific content"""
    print("\n💡 BRAND RECOMMENDATION ENGINE")
    print("=" * 50)
    
    content_to_analyze = """
    We're excited to launch our new AI-powered analytics platform! 
    This revolutionary tool will help businesses make data-driven decisions 
    and stay ahead of the competition. Get ready to transform your workflow!
    """
    
    print(f"Content to analyze: '{content_to_analyze.strip()}'")
    print("\nBrand Recommendations:")
    
    # Simple recommendation logic
    if "excited" in content_to_analyze.lower() and "revolutionary" in content_to_analyze.lower():
        print("  🎯 Recommended: tech_startup")
        print("  💡 Why: Energetic, innovation-focused language matches startup vibe")
    
    if "data-driven" in content_to_analyze.lower() and "analytics" in content_to_analyze.lower():
        print("  🎯 Recommended: corporate_finance") 
        print("  💡 Why: Data-focused, business-oriented content")
    
    print("  ⚠️  Avoid: eco_brand, health_wellness")
    print("  💡 Why: Content doesn't align with environmental or wellness focus")

if __name__ == "__main__":
    # Show available brands
    print("🎨 AVAILABLE BRAND PROFILES:")
    brands = list_available_brands()
    for i, brand in enumerate(brands, 1):
        print(f"  {i}. {brand}")
    
    # Run demos
    demo_single_brand_test()
    demo_multi_brand_comparison() 
    demo_content_analysis()
    demo_brand_recommendation()