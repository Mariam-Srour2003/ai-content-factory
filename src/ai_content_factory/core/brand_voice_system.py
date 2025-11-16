# src/ai_content_factory/core/brand_voice_system.py
import yaml
from pydantic import BaseModel
from ..mypackages.tone_analyzer import ToneAnalyzer
from ..mypackages.consistency_checker import ConsistencyChecker

import os

def load_config():
    # Get the absolute path to the 'config' folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', '.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class BrandVoiceSystem:
    def __init__(self):
        self.config = load_config()
        # Initialize ToneAnalyzer with tone labels from the config
        tone_labels = self.config['brand_voice']['tone']
        self.tone_analyzer = ToneAnalyzer(candidate_labels=tone_labels)
        self.consistency_checker = ConsistencyChecker(self.config['brand_voice']['consistency_threshold'])

    def analyze_tone(self, text: str):
        return self.tone_analyzer.analyze(text)

    def check_consistency(self, text, example_content):
        """
        Check if the provided text is consistent with the example content.
        """
        return self.consistency_checker.check(text, example_content)