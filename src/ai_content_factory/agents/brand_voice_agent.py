# src/ai_content_factory/agents/brand_voice_agent.py
from pydantic import BaseModel, Field
from typing import List, Dict
from ..core.brand_voice_system import BrandVoiceSystem
from ..core.ingestors.example_content_ingestor import ExampleContentIngestor

class BrandVoiceAgent(BaseModel):
    content: str  # The content to be analyzed or generated.
    example_content_path: str  # Path to the example content JSON file.

    def ingest_example_content(self) -> List[str]:
        """Ingest example content from the provided file."""
        ingestor = ExampleContentIngestor(self.example_content_path)
        content = ingestor.ingest()
        # If content is already a list, just return it
        if isinstance(content, list):
            return content
        # If it's a dictionary, flatten it (backward compatibility)
        example_content = []
        for tone in content.values():
            example_content.extend(tone)
        return example_content

    def analyze_tone(self) -> str:
        """Analyze the tone of the content."""
        brand_voice_system = BrandVoiceSystem()
        return brand_voice_system.analyze_tone(self.content)

    def check_consistency(self) -> bool:
        """Check if the content is consistent with the brand voice."""
        example_content = self.ingest_example_content()
        brand_voice_system = BrandVoiceSystem()
        return brand_voice_system.check_consistency(self.content, example_content)

    def run(self) -> dict:
        """Main method to run the Brand Voice Agent."""
        tone = self.analyze_tone()
        is_consistent = self.check_consistency()
        return {
            "tone": tone,
            "is_consistent": is_consistent
        }

# Example usage
if __name__ == "__main__":
    content = "Please ensure that your response is both thorough and precise."
    example_content_path = 'data/brand_voice_examples.json'

    # Instantiate the agent
    agent = BrandVoiceAgent(content=content, example_content_path=example_content_path)

    # Run the agent
    results = agent.run()

    print(f"Tone: {results['tone']}")
    print(f"Is Consistent: {results['is_consistent']}")