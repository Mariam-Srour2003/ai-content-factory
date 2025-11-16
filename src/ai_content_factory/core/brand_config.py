# src/ai_content_factory/core/brand_config.py
from typing import Dict, List, Any
from pydantic import BaseModel
import json

class BrandConfig(BaseModel):
    name: str
    description: str
    tone_guidelines: Dict[str, List[str]]
    voice_characteristics: List[str]
    target_audience: Dict[str, str]
    prohibited_phrases: List[str]
    preferred_phrases: List[str]
    supported_tones: List[str]
    consistency_threshold: float = 0.3

# Pre-configured brand profiles
BRAND_PROFILES = {
    "tech_startup": BrandConfig(
        name="TechStart Inc.",
        description="Innovative tech startup with casual, energetic voice",
        tone_guidelines={
            "casual": [
                "Use emojis and exclamation points sparingly",
                "Contractions are encouraged",
                "Friendly and approachable tone",
                "Use modern tech slang appropriately"
            ],
            "technical": [
                "Explain complex concepts simply",
                "Focus on user benefits, not just features",
                "Use analogies for technical concepts"
            ],
            "enthusiastic": [
                "Show excitement about innovation",
                "Use positive, forward-looking language",
                "Highlight growth and potential"
            ]
        },
        voice_characteristics=[
            "Young and energetic",
            "Innovation-focused",
            "User-centric",
            "Transparent and honest"
        ],
        target_audience={
            "age_range": "20-35",
            "profession": "Tech professionals, entrepreneurs",
            "tech_savviness": "High"
        },
        prohibited_phrases=[
            "Corporate jargon",
            "Legacy systems",
            "At this time",
            "Please be advised"
        ],
        preferred_phrases=[
            "Game-changing",
            "Next-generation",
            "User-friendly",
            "Seamless experience"
        ],
        supported_tones=["casual", "technical", "enthusiastic"]
    ),
    
    "corporate_finance": BrandConfig(
        name="Global Finance Corp",
        description="Established financial institution with formal, trustworthy voice",
        tone_guidelines={
            "formal": [
                "Use complete sentences with proper grammar",
                "Avoid contractions",
                "Maintain professional terminology",
                "Be precise and unambiguous"
            ],
            "authoritative": [
                "Use data and statistics",
                "Reference industry standards",
                "Show expertise confidently"
            ],
            "reassuring": [
                "Emphasize security and stability",
                "Use calming language during uncertainty",
                "Highlight long-term reliability"
            ]
        },
        voice_characteristics=[
            "Professional and polished",
            "Data-driven",
            "Risk-aware",
            "Client-focused"
        ],
        target_audience={
            "age_range": "35-65",
            "profession": "Executives, investors, high-net-worth individuals",
            "industry": "Finance, banking, investment"
        },
        prohibited_phrases=[
            "No worries",
            "Hey guys",
            "Awesome",
            "Cool feature"
        ],
        preferred_phrases=[
            "We are pleased to announce",
            "Based on our analysis",
            "In accordance with",
            "We take this opportunity to"
        ],
        supported_tones=["formal", "authoritative", "reassuring"],
        consistency_threshold=0.4
    ),
    
    "health_wellness": BrandConfig(
        name="Mindful Wellness Co.",
        description="Health and wellness brand with compassionate, educational voice",
        tone_guidelines={
            "compassionate": [
                "Use empathetic language",
                "Acknowledge challenges and struggles",
                "Offer support and encouragement"
            ],
            "educational": [
                "Explain health concepts clearly",
                "Cite scientific sources when appropriate",
                "Break down complex information"
            ],
            "inspirational": [
                "Share success stories",
                "Use motivational language",
                "Focus on positive outcomes"
            ]
        },
        voice_characteristics=[
            "Empathetic and caring",
            "Evidence-based",
            "Holistic approach",
            "Community-focused"
        ],
        target_audience={
            "age_range": "25-55",
            "health_focus": "Mental and physical wellness",
            "values": "Mindfulness, sustainability, self-care"
        },
        prohibited_phrases=[
            "Just try harder",
            "It's simple",
            "Everyone can do it",
            "Miracle cure"
        ],
        preferred_phrases=[
            "We understand that",
            "Research suggests",
            "Many people find",
            "At your own pace"
        ],
        supported_tones=["compassionate", "educational", "inspirational"]
    ),
    
    "eco_brand": BrandConfig(
        name="EarthFirst Solutions",
        description="Environmental brand with passionate, action-oriented voice",
        tone_guidelines={
            "passionate": [
                "Show genuine concern for environment",
                "Use compelling storytelling",
                "Connect to larger purpose"
            ],
            "action_oriented": [
                "Use active voice",
                "Provide clear calls to action",
                "Focus on solutions, not just problems"
            ],
            "hopeful": [
                "Highlight positive changes",
                "Share success stories",
                "Emphasize collective impact"
            ]
        },
        voice_characteristics=[
            "Purpose-driven",
            "Transparent about impact",
            "Community-building",
            "Solution-focused"
        ],
        target_audience={
            "age_range": "18-45",
            "values": "Sustainability, environmentalism, social responsibility",
            "activism_level": "Moderate to high"
        },
        prohibited_phrases=[
            "It's too late",
            "Someone else will handle it",
            "Greenwashing terms without evidence"
        ],
        preferred_phrases=[
            "Together we can",
            "Every action counts",
            "Join the movement",
            "Sustainable future"
        ],
        supported_tones=["passionate", "action_oriented", "hopeful"]
    )
}

def get_brand_config(brand_key: str) -> BrandConfig:
    """Get brand configuration by key"""
    if brand_key not in BRAND_PROFILES:
        raise ValueError(f"Brand '{brand_key}' not found. Available brands: {list(BRAND_PROFILES.keys())}")
    return BRAND_PROFILES[brand_key]

def list_available_brands() -> List[str]:
    """List all available brand configurations"""
    return list(BRAND_PROFILES.keys())