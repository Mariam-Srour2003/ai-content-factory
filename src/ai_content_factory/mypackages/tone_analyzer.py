# src/ai_content_factory/mypackages/tone_analyzer.py
from transformers import pipeline

class ToneAnalyzer:
    def __init__(self, candidate_labels=None, model_type='zero-shot'):
        """
        Initializes the ToneAnalyzer with a chosen model type.
        
        :param model_type: 'zero-shot' for tone classification, 'sentiment' for sentiment analysis
        :param candidate_labels: List of candidate labels for zero-shot classification (e.g., tones)
        """
        self.model_type = model_type
        
        if model_type == 'zero-shot':
            # Use facebook/bart-large-mnli for zero-shot classification
            self.analyzer = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            self.candidate_labels = candidate_labels or ['formal', 'casual', 'technical', 'urgent']
        else:
            # Use sentiment-analysis pipeline for sentiment detection
            self.analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
            self.candidate_labels = None  # Not used for sentiment analysis

    def analyze(self, text):
        if self.model_type == 'zero-shot':
            # Use zero-shot classification for tone detection
            result = self.analyzer(text, candidate_labels=self.candidate_labels)
            return result['labels'][0]  # Return the predicted tone
        else:
            # Use sentiment analysis
            result = self.analyzer(text)
            return result[0]['label']  # Return POSITIVE/NEGATIVE/NEUTRAL