# src/ai_content_factory/core/brand_voice_documenter.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
import json
import yaml
from .file_utils import safe_json_dump, safe_yaml_dump

class BrandVoiceDocumentation(BaseModel):
    brand_name: str
    version: str = "1.0"
    created_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Core brand voice elements
    tone_guidelines: Dict[str, List[str]] = Field(default_factory=dict)
    voice_characteristics: List[str] = Field(default_factory=list)
    target_audience: Dict[str, str] = Field(default_factory=dict)
    prohibited_phrases: List[str] = Field(default_factory=list)
    preferred_phrases: List[str] = Field(default_factory=list)
    
    # Examples
    content_examples: Dict[str, List[str]] = Field(default_factory=dict)
    before_after_examples: List[Dict[str, str]] = Field(default_factory=list)
    
    # Technical specifications
    consistency_threshold: float = 0.7
    supported_tones: List[str] = Field(default_factory=list)

class BrandVoiceDocumenter:
    def __init__(self, brand_name: str):
        self.brand_name = brand_name
        self.documentation = BrandVoiceDocumentation(brand_name=brand_name)
    
    def add_tone_guideline(self, tone: str, guidelines: List[str]):
        """Add guidelines for a specific tone"""
        self.documentation.tone_guidelines[tone] = guidelines
    
    def add_voice_characteristics(self, characteristics: List[str]):
        """Add brand voice characteristics"""
        self.documentation.voice_characteristics.extend(characteristics)
    
    def set_target_audience(self, demographics: Dict[str, str]):
        """Set target audience demographics"""
        self.documentation.target_audience = demographics
    
    def add_prohibited_phrases(self, phrases: List[str]):
        """Add phrases to avoid"""
        self.documentation.prohibited_phrases.extend(phrases)
    
    def add_preferred_phrases(self, phrases: List[str]):
        """Add preferred phrases"""
        self.documentation.preferred_phrases.extend(phrases)
    
    def add_content_examples(self, tone: str, examples: List[str]):
        """Add content examples for specific tones"""
        if tone not in self.documentation.content_examples:
            self.documentation.content_examples[tone] = []
        self.documentation.content_examples[tone].extend(examples)
    
    def add_before_after_example(self, before: str, after: str, reason: str):
        """Add before/after examples with reasoning"""
        self.documentation.before_after_examples.append({
            "before": before,
            "after": after,
            "improvement_reason": reason
        })
    
    def set_consistency_threshold(self, threshold: float):
        """Set consistency threshold"""
        self.documentation.consistency_threshold = threshold
    
    def set_supported_tones(self, tones: List[str]):
        """Set supported tones"""
        self.documentation.supported_tones = tones
    
    def export_json(self, file_path: str):
        """Export documentation as JSON"""
        safe_json_dump(self.documentation.dict(), file_path)
    
    def export_yaml(self, file_path: str):
        """Export documentation as YAML"""
        safe_yaml_dump(self.documentation.dict(), file_path)
    
    def generate_report(self) -> str:
        """Generate a human-readable report"""
        report = f"""
BRAND VOICE DOCUMENTATION
=========================

Brand: {self.documentation.brand_name}
Version: {self.documentation.version}
Created: {self.documentation.created_date}

TONE GUIDELINES
{'-' * 50}
"""
        for tone, guidelines in self.documentation.tone_guidelines.items():
            report += f"\n{tone.upper()}:\n"
            for guideline in guidelines:
                report += f"  • {guideline}\n"
        
        report += f"""
VOICE CHARACTERISTICS
{'-' * 50}
"""
        for char in self.documentation.voice_characteristics:
            report += f"• {char}\n"
        
        report += f"""
TARGET AUDIENCE
{'-' * 50}
"""
        for key, value in self.documentation.target_audience.items():
            report += f"{key}: {value}\n"
        
        return report

# Example usage template
def create_brand_voice_template():
    """Create a comprehensive brand voice documentation template"""
    documenter = BrandVoiceDocumenter("TechCorp Solutions")
    
    # Add tone guidelines
    documenter.add_tone_guideline("formal", [
        "Use complete sentences with proper grammar",
        "Avoid contractions and slang",
        "Maintain professional terminology",
        "Use respectful and polite language"
    ])
    
    documenter.add_tone_guideline("casual", [
        "Use conversational language",
        "Contractions are acceptable",
        "Friendly and approachable tone",
        "Can use light humor when appropriate"
    ])
    
    documenter.add_tone_guideline("technical", [
        "Use precise technical terminology",
        "Include relevant specifications",
        "Focus on accuracy and clarity",
        "Reference documentation when needed"
    ])
    
    documenter.add_tone_guideline("urgent", [
        "Use clear, direct language",
        "Emphasize time sensitivity",
        "Provide specific action items",
        "Maintain professionalism even in urgency"
    ])
    
    # Add voice characteristics
    documenter.add_voice_characteristics([
        "Authoritative but approachable",
        "Clear and concise",
        "Solution-oriented",
        "Empathetic to user needs",
        "Technically accurate"
    ])
    
    # Set target audience
    documenter.set_target_audience({
        "age_range": "25-45",
        "profession": "Technical professionals",
        "education_level": "Bachelor's degree or higher",
        "industry": "Technology, IT, Engineering"
    })
    
    # Add prohibited phrases
    documenter.add_prohibited_phrases([
        "That's not my problem",
        "I don't know",
        "You're wrong",
        "This is stupid",
        "Whatever"
    ])
    
    # Add preferred phrases
    documenter.add_preferred_phrases([
        "Let me help you with that",
        "I'll find the right solution for you",
        "Thank you for bringing this to our attention",
        "We appreciate your patience",
        "Here's how we can resolve this"
    ])
    
    # Set supported tones
    documenter.set_supported_tones(["formal", "casual", "technical", "urgent"])
    
    return documenter