# src/ai_content_factory/quick_brand_test.py
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .core.brand_config import get_brand_config, list_available_brands
from .core.brand_voice_documenter import BrandVoiceDocumenter
from .core.few_shot_prompt_builder import FewShotPromptBuilder
from .core.file_utils import safe_json_dump
from .core.brand_voice_system import BrandVoiceSystem
import json

def test_single_brand(brand_key: str):
    """Test a single brand with sample content"""
    print(f"🧪 TESTING BRAND: {brand_key.upper()}")
    print("=" * 50)
    
    try:
        # Get brand configuration
        brand_config = get_brand_config(brand_key)
        print(f"🏷️  Brand: {brand_config.name}")
        print(f"📝 {brand_config.description}")
        
        # Create brand documentation
        documenter = BrandVoiceDocumenter(brand_config.name)
        
        # Set up brand guidelines
        for tone, guidelines in brand_config.tone_guidelines.items():
            documenter.add_tone_guideline(tone, guidelines)
        
        documenter.add_voice_characteristics(brand_config.voice_characteristics)
        documenter.set_target_audience(brand_config.target_audience)
        documenter.add_prohibited_phrases(brand_config.prohibited_phrases)
        documenter.add_preferred_phrases(brand_config.preferred_phrases)
        documenter.set_supported_tones(brand_config.supported_tones)
        
        # Create brand examples
        brand_examples = create_brand_examples(brand_config)
        
        # Save files
        documenter.export_json(f'data/{brand_key}_brand_voice.json')
        safe_json_dump(brand_examples, f'data/{brand_key}_examples.json')
        
        print(f"✅ Created {brand_config.name} configuration")
        print(f"✅ Generated {sum(len(ex) for ex in brand_examples.values())} examples")
        
        # Test with sample content
        test_with_sample_content(brand_key, brand_config, brand_examples)
        
    except Exception as e:
        print(f"❌ Error testing brand {brand_key}: {e}")
        import traceback
        traceback.print_exc()

def create_brand_examples(brand_config):
    """Create example content for the brand"""
    # Generic examples that will work for all brands
    examples = {
        "announcement": [
            "We're excited to share some important news with you.",
            "Please be informed about upcoming changes to our services.",
            "We have an important update regarding our products."
        ],
        "instruction": [
            "Please follow these steps to complete the process.",
            "Here's how to get started with our platform.",
            "Make sure to review the guidelines before proceeding."
        ],
        "support": [
            "We're here to help if you have any questions.",
            "Please reach out if you need assistance.",
            "Our team is available to support you."
        ],
        "urgent": [
            "Important notice that requires your attention.",
            "Please take immediate action on this matter.",
            "This issue needs to be addressed as soon as possible."
        ]
    }
    
    # Map to brand-specific tones
    brand_mapping = {
        "tech_startup": {
            "announcement": "enthusiastic",
            "instruction": "technical", 
            "support": "casual",
            "urgent": "casual"
        },
        "corporate_finance": {
            "announcement": "formal",
            "instruction": "authoritative",
            "support": "reassuring", 
            "urgent": "formal"
        },
        "health_wellness": {
            "announcement": "inspirational",
            "instruction": "educational",
            "support": "compassionate",
            "urgent": "compassionate"
        },
        "eco_brand": {
            "announcement": "passionate", 
            "instruction": "action_oriented",
            "support": "hopeful",
            "urgent": "action_oriented"
        }
    }
    
    brand_key = [k for k, v in get_brand_config.__globals__['BRAND_PROFILES'].items() 
                if v.name == brand_config.name][0]
    
    brand_examples = {}
    for content_type, brand_tone in brand_mapping[brand_key].items():
        if content_type in examples:
            if brand_tone not in brand_examples:
                brand_examples[brand_tone] = []
            brand_examples[brand_tone].extend(examples[content_type])
    
    return brand_examples

def test_with_sample_content(brand_key: str, brand_config, brand_examples):
    """Test the brand with sample content"""
    print(f"\n📊 TESTING SAMPLE CONTENT:")
    print("-" * 40)
    
    # Sample content tailored to brand type
    sample_content = {
        "tech_startup": [
            "Hey team! Our new feature is live and it's absolutely amazing! 🚀",
            "Quick update: we're crushing our user growth targets this month!",
            "PSA: The API will be down for maintenance tonight at midnight."
        ],
        "corporate_finance": [
            "We are pleased to announce the Q3 financial results.",
            "Please review the attached compliance documentation.",
            "The board meeting has been scheduled for next Thursday."
        ],
        "health_wellness": [
            "Remember to take deep breaths during stressful moments.",
            "We're here to support your wellness journey every step of the way.",
            "New research shows the benefits of daily meditation practice."
        ],
        "eco_brand": [
            "Join us in the fight against plastic pollution!",
            "Every small action counts toward a sustainable future.",
            "Our new initiative will plant 10,000 trees this year."
        ]
    }
    
    brand_voice_system = BrandVoiceSystem()
    
    brand_type = brand_key  # Since brand_key matches the profile keys
    if brand_type in sample_content:
        for content in sample_content[brand_type]:
            try:
                print(f"\n📝 '{content}'")
                tone = brand_voice_system.analyze_tone(content)
                print(f"   🎭 Detected Tone: {tone}")
                
                # Check if tone is in brand's supported tones
                if tone in brand_config.supported_tones:
                    print(f"   ✅ Tone matches brand guidelines")
                else:
                    print(f"   ⚠️  Tone doesn't match brand supported tones: {brand_config.supported_tones}")
                    
            except Exception as e:
                print(f"   ❌ Analysis error: {e}")

def compare_all_brands():
    """Compare all available brands"""
    print("🔍 COMPARING ALL BRANDS")
    print("=" * 50)
    
    brands = list_available_brands()
    
    # Test content that works for all brands
    universal_test_content = [
        "We have an important announcement to share.",
        "Please review the following information carefully.",
        "We're here to help if you have any questions.",
        "This requires your immediate attention."
    ]
    
    for brand_key in brands:
        print(f"\n{'='*40}")
        test_single_brand(brand_key)
    
    print(f"\n🎉 COMPARISON COMPLETED!")
    print(f"📁 Check the 'data' folder for brand-specific files")

def show_available_brands():
    """Show all available brands"""
    print("🎨 AVAILABLE BRAND PROFILES")
    print("=" * 40)
    
    brands = list_available_brands()
    for i, brand_key in enumerate(brands, 1):
        try:
            brand_config = get_brand_config(brand_key)
            print(f"{i}. 🏷️  {brand_config.name}")
            print(f"   🔑 Key: {brand_key}")
            print(f"   📝 {brand_config.description}")
            print(f"   🎭 Tones: {', '.join(brand_config.supported_tones)}")
        except Exception as e:
            print(f"{i}. ❌ {brand_key} - Error: {e}")
    
    return brands

def main():
    """Main function with command line support"""
    if len(sys.argv) > 1:
        brand_key = sys.argv[1]
        brands = list_available_brands()
        
        if brand_key in brands:
            test_single_brand(brand_key)
        else:
            print(f"❌ Brand '{brand_key}' not found.")
            print(f"📋 Available brands: {brands}")
    else:
        # Show available brands and run comparison
        brands = show_available_brands()
        print(f"\n🎯 Usage:")
        print(f"   uv run src/ai_content_factory/quick_brand_test.py <brand_key>")
        print(f"   uv run src/ai_content_factory/quick_brand_test.py all")
        print(f"\n📋 Examples:")
        print(f"   uv run src/ai_content_factory/quick_brand_test.py tech_startup")
        print(f"   uv run src/ai_content_factory/quick_brand_test.py corporate_finance")
        print(f"   uv run src/ai_content_factory/quick_brand_test.py all")
        
        # Ask if user wants to compare all
        response = input(f"\n🚀 Compare all brands? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            compare_all_brands()

if __name__ == "__main__":
    main()