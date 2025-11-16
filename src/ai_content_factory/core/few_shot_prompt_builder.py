# src/ai_content_factory/core/few_shot_prompt_builder.py
from typing import List, Dict, Any
import json

class FewShotPromptBuilder:
    def __init__(self, brand_voice_examples: Dict[str, List[str]]):
        self.brand_voice_examples = brand_voice_examples
        self.prompt_templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, str]:
        """Load default prompt templates"""
        return {
            "content_generation": """
Generate content in the brand voice based on the following examples:

BRAND VOICE EXAMPLES:
{examples}

TONE: {tone}
CONTEXT: {context}
AUDIENCE: {audience}

Generate content that matches the brand voice and specified tone:
""",
            "content_revision": """
Revise the following content to match our brand voice:

BRAND VOICE EXAMPLES:
{examples}

ORIGINAL CONTENT:
{original_content}

TARGET TONE: {tone}

Revised content:
""",
            "tone_adaptation": """
Adapt the following content from {source_tone} to {target_tone} tone:

{source_tone.upper()} EXAMPLES:
{source_examples}

{TARGET_TONE.upper()} EXAMPLES:
{target_examples}

CONTENT TO ADAPT:
{content}

Adapted content:
"""
        }
    
    def build_generation_prompt(self, tone: str, context: str, audience: str = "general") -> str:
        """Build prompt for content generation"""
        examples = self._format_examples_for_tone(tone)
        return self.prompt_templates["content_generation"].format(
            examples=examples,
            tone=tone,
            context=context,
            audience=audience
        )
    
    def build_revision_prompt(self, original_content: str, target_tone: str) -> str:
        """Build prompt for content revision"""
        examples = self._format_examples_for_tone(target_tone)
        return self.prompt_templates["content_revision"].format(
            examples=examples,
            original_content=original_content,
            tone=target_tone
        )
    
    def build_tone_adaptation_prompt(self, content: str, source_tone: str, target_tone: str) -> str:
        """Build prompt for tone adaptation"""
        source_examples = self._format_examples_for_tone(source_tone)
        target_examples = self._format_examples_for_tone(target_tone)
        
        return self.prompt_templates["tone_adaptation"].format(
            source_tone=source_tone,
            target_tone=target_tone,
            TARGET_TONE=target_tone.upper(),
            source_examples=source_examples,
            target_examples=target_examples,
            content=content
        )
    
    def _format_examples_for_tone(self, tone: str, max_examples: int = 3) -> str:
        """Format examples for a specific tone"""
        if tone not in self.brand_voice_examples:
            return f"No examples found for tone: {tone}"
        
        examples = self.brand_voice_examples[tone][:max_examples]
        formatted_examples = "\n".join([f"- {example}" for example in examples])
        return formatted_examples
    
    def create_few_shot_dataset(self, output_path: str):
        """Create a structured few-shot learning dataset"""
        dataset = {
            "metadata": {
                "total_examples": sum(len(examples) for examples in self.brand_voice_examples.values()),
                "tones": list(self.brand_voice_examples.keys()),
                "example_counts": {tone: len(examples) for tone, examples in self.brand_voice_examples.items()}
            },
            "examples": []
        }
        
        for tone, examples in self.brand_voice_examples.items():
            for example in examples:
                dataset["examples"].append({
                    "tone": tone,
                    "content": example,
                    "length": len(example),
                    "words": len(example.split())
                })
        
        with open(output_path, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        return dataset

# Integration with existing system
class EnhancedBrandVoiceAgent:
    def __init__(self, example_content_path: str):
        self.example_content_path = example_content_path
        self.brand_voice_examples = self._load_examples()
        self.prompt_builder = FewShotPromptBuilder(self.brand_voice_examples)
        # Initialize other components...
    
    def _load_examples(self) -> Dict[str, List[str]]:
        """Load examples from JSON file"""
        import json
        import os
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..'))
        file_path = os.path.join(project_root, self.example_content_path)
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def generate_content(self, tone: str, context: str, audience: str = "general") -> str:
        """Generate brand-consistent content using few-shot learning"""
        prompt = self.prompt_builder.build_generation_prompt(tone, context, audience)
        # Here you would integrate with your LLM of choice
        # For now, return the prompt structure
        return {
            "prompt": prompt,
            "tone": tone,
            "context": context,
            "audience": audience
        }