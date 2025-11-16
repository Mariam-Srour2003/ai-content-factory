# src/ai_content_factory/core/brand_voice_embeddings.py
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from ai_content_factory.core.few_shot_prompt_builder import FewShotPromptBuilder
import faiss
import json
import pickle

class BrandVoiceEmbeddings:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.content_data = []
        self.dimension = 384  # Default for all-MiniLM-L6-v2
    
    def create_embeddings(self, content_items: List[Dict[str, Any]]):
        """Create embeddings for brand voice content"""
        texts = [item['content'] for item in content_items]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index
        self.dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype(np.float32))
        
        # Store content data
        self.content_data = content_items
        
        return embeddings
    
    def search_similar_content(self, query: str, top_k: int = 5, tone_filter: str = None) -> List[Dict[str, Any]]:
        """Search for similar content using embeddings"""
        if self.index is None:
            raise ValueError("No embeddings index created. Call create_embeddings first.")
        
        # Encode query
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype(np.float32), top_k * 2)  # Get extra for filtering
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.content_data):
                content_item = self.content_data[idx]
                
                # Apply tone filter if specified
                if tone_filter and content_item.get('tone') != tone_filter:
                    continue
                
                results.append({
                    'content': content_item['content'],
                    'tone': content_item.get('tone', 'unknown'),
                    'similarity_score': float(score),
                    'is_consistent': content_item.get('is_consistent', False),
                    'source': content_item.get('source', 'unknown')
                })
                
                if len(results) >= top_k:
                    break
        
        return results
    
    def find_tone_examples(self, tone: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find best examples for a specific tone"""
        tone_content = [item for item in self.content_data if item.get('tone') == tone and item.get('is_consistent')]
        
        if not tone_content:
            return []
        
        # Use the most consistent and representative examples
        representative_examples = sorted(
            tone_content,
            key=lambda x: (x.get('is_consistent', False), len(x['content'])),
            reverse=True
        )[:top_k]
        
        return representative_examples
    
    def get_tone_centroids(self) -> Dict[str, np.ndarray]:
        """Calculate centroid embeddings for each tone"""
        tone_embeddings = {}
        
        for item in self.content_data:
            tone = item.get('tone', 'unknown')
            if tone not in tone_embeddings:
                tone_embeddings[tone] = []
            
            # Create embedding for this content
            embedding = self.model.encode([item['content']])[0]
            faiss.normalize_L2(embedding.reshape(1, -1))
            tone_embeddings[tone].append(embedding)
        
        # Calculate centroids
        centroids = {}
        for tone, embeddings in tone_embeddings.items():
            if embeddings:
                centroid = np.mean(embeddings, axis=0)
                faiss.normalize_L2(centroid.reshape(1, -1))
                centroids[tone] = centroid[0]
        
        return centroids
    
    def save_embeddings(self, file_path: str):
        """Save embeddings and index to file"""
        data = {
            'content_data': self.content_data,
            'dimension': self.dimension
        }
        
        # Save FAISS index
        faiss.write_index(self.index, file_path + '.index')
        
        # Save metadata
        with open(file_path + '.meta', 'wb') as f:
            pickle.dump(data, f)
    
    def load_embeddings(self, file_path: str):
        """Load embeddings and index from file"""
        # Load FAISS index
        self.index = faiss.read_index(file_path + '.index')
        
        # Load metadata
        with open(file_path + '.meta', 'rb') as f:
            data = pickle.load(f)
        
        self.content_data = data['content_data']
        self.dimension = data['dimension']

# RAG Integration Class
class BrandVoiceRAG:
    def __init__(self, embeddings: BrandVoiceEmbeddings, few_shot_builder: FewShotPromptBuilder):
        self.embeddings = embeddings
        self.few_shot_builder = few_shot_builder
    
    def generate_rag_prompt(self, query: str, target_tone: str, context: str = "") -> str:
        """Generate RAG-enhanced prompt using similar examples"""
        # Find similar content
        similar_content = self.embeddings.search_similar_content(query, top_k=3, tone_filter=target_tone)
        
        # Find tone examples
        tone_examples = self.embeddings.find_tone_examples(target_tone, top_k=2)
        
        # Build enhanced prompt
        prompt = f"""
Generate content based on the query and context, following our brand voice.

QUERY: {query}
CONTEXT: {context}
TARGET TONE: {target_tone}

RELEVANT EXAMPLES:
"""
        
        # Add similar content examples
        if similar_content:
            prompt += "\nSimilar successful examples:\n"
            for i, example in enumerate(similar_content, 1):
                prompt += f"{i}. {example['content']} (Tone: {example['tone']}, Score: {example['similarity_score']:.3f})\n"
        
        # Add tone-specific examples
        if tone_examples:
            prompt += f"\n{target_tone.upper()} tone examples:\n"
            for i, example in enumerate(tone_examples, 1):
                prompt += f"{i}. {example['content']}\n"
        
        prompt += f"\nGenerate {target_tone} content that addresses the query while maintaining brand consistency:"
        
        return prompt
    
    def analyze_and_suggest(self, content: str) -> Dict[str, Any]:
        """Analyze content and provide suggestions using RAG"""
        # Find similar content
        similar_content = self.embeddings.search_similar_content(content, top_k=5)
        
        # Get predicted tone
        tone_result = self.embeddings.model.encode([content])
        # This would integrate with your tone analyzer
        
        analysis = {
            'input_content': content,
            'similar_examples': similar_content,
            'suggestions': self._generate_suggestions(content, similar_content),
            'consistency_score': self._calculate_consistency_score(content, similar_content)
        }
        
        return analysis
    
    def _generate_suggestions(self, content: str, similar_content: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if not similar_content:
            suggestions.append("No similar brand-consistent examples found. Consider adding more examples to your brand voice database.")
            return suggestions
        
        # Analyze consistency patterns
        consistent_examples = [ex for ex in similar_content if ex['is_consistent']]
        if consistent_examples:
            suggestions.append(f"Found {len(consistent_examples)} similar examples that match brand voice. Use these as reference.")
        
        # Check tone alignment
        tones = [ex['tone'] for ex in similar_content[:3]]
        if len(set(tones)) == 1:
            suggestions.append(f"Most similar content uses {tones[0]} tone. Ensure your content aligns with this tone.")
        
        return suggestions
    
    def _calculate_consistency_score(self, content: str, similar_content: List[Dict[str, Any]]) -> float:
        """Calculate consistency score based on similar content"""
        if not similar_content:
            return 0.0
        
        # Weight scores by similarity and consistency
        total_weight = 0
        weighted_score = 0
        
        for example in similar_content:
            weight = example['similarity_score']
            consistency = 1.0 if example['is_consistent'] else 0.0
            
            weighted_score += weight * consistency
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0