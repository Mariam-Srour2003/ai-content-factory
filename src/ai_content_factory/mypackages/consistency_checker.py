# src/ai_content_factory/mypackages/consistency_checker.py
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from typing import List

class ConsistencyChecker:
    def __init__(self, consistency_threshold=0.3):
        self.consistency_threshold = consistency_threshold
        self.vectorizer = TfidfVectorizer(min_df=1)  # min_df=1 to handle small datasets

    def check(self, text: str, example_content: List[str]) -> bool:
        """
        Check if the provided text is consistent with the example content.
        Returns True if consistent, False otherwise.
        """
        if not example_content:
            # If no examples, consider it consistent (or adjust logic as needed)
            return True
        
        # Combine the input text with examples
        all_text = [text] + example_content
        
        try:
            # Transform text to TF-IDF vectors
            vectors = self.vectorizer.fit_transform(all_text)
            
            # Check if we have valid vectors
            if vectors.shape[0] < 2 or vectors.shape[1] == 0:
                return True  # Fallback: consider consistent if no valid comparison
            
            # Compute cosine similarity between input text and examples
            similarity_matrix = cosine_similarity(vectors[0:1], vectors[1:])
            
            # Check if any similarity meets the threshold
            if similarity_matrix.size > 0 and np.max(similarity_matrix[0]) >= self.consistency_threshold:
                return True
            return False
            
        except Exception as e:
            print(f"Consistency check failed: {e}")
            return True  # Fallback: consider consistent on error