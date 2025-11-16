# src/ai_content_factory/core/content_ingestion_pipeline.py
import os
import json
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from ..mypackages.tone_analyzer import ToneAnalyzer

class ContentIngestionPipeline:
    def __init__(self, brand_voice_system):
        self.brand_voice_system = brand_voice_system
        self.tone_analyzer = ToneAnalyzer()
        self.ingested_content = []
    
    def ingest_from_directory(self, directory_path: str, file_extensions: List[str] = None):
        """Ingest content from a directory of files"""
        if file_extensions is None:
            file_extensions = ['.txt', '.json', '.csv', '.md']
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    self.ingest_file(file_path)
    
    def ingest_file(self, file_path: str):
        """Ingest content from a single file"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.json':
                self._ingest_json(file_path)
            elif file_extension == '.csv':
                self._ingest_csv(file_path)
            elif file_extension in ['.txt', '.md']:
                self._ingest_text(file_path)
            else:
                print(f"Unsupported file type: {file_extension}")
        except Exception as e:
            print(f"Error ingesting {file_path}: {e}")
    
    def _ingest_json(self, file_path: str):
        """Ingest content from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            for item in data:
                self._process_content_item(item, file_path)
        elif isinstance(data, dict):
            self._process_content_item(data, file_path)
    
    def _ingest_csv(self, file_path: str):
        """Ingest content from CSV file"""
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            self._process_content_item(row.to_dict(), file_path)
    
    def _ingest_text(self, file_path: str):
        """Ingest content from text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by paragraphs or sections
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        for i, paragraph in enumerate(paragraphs):
            self._process_content_item({
                'content': paragraph,
                'section': i + 1
            }, file_path)
    
    def _process_content_item(self, item: Dict[str, Any], source: str = "unknown"):
        """Process a single content item"""
        if 'content' not in item:
            return
        
        content = item['content']
        if not isinstance(content, str) or len(content.strip()) < 10:
            return
        
        # Analyze tone
        try:
            tone_result = self.tone_analyzer.analyze(content)
            # Handle both dictionary and string responses
            if isinstance(tone_result, dict) and 'labels' in tone_result:
                tone = tone_result['labels'][0]
            else:
                tone = str(tone_result)
        except Exception as e:
            tone = "unknown"
            print(f"Tone analysis error for content '{content[:50]}...': {e}")
        
        # Check consistency - use all previously ingested content as examples
        try:
            existing_examples = [item['content'] for item in self.ingested_content]
            is_consistent = self.brand_voice_system.check_consistency(content, existing_examples)
        except Exception as e:
            is_consistent = False
            print(f"Consistency check error: {e}")
        
        # Store processed content
        processed_item = {
            'content': content,
            'tone': tone,
            'is_consistent': is_consistent,
            'source': item.get('source', source),
            'timestamp': datetime.now().isoformat(),
            'length': len(content),
            'word_count': len(content.split())
        }
        
        self.ingested_content.append(processed_item)
        print(f"  ✓ Ingested: '{content[:60]}...' (Tone: {tone}, Consistent: {is_consistent})")
    
    def export_analysis(self, output_path: str):
        """Export analysis results"""
        analysis = {
            'summary': {
                'total_content': len(self.ingested_content),
                'tones_distribution': self._get_tones_distribution(),
                'consistency_rate': self._get_consistency_rate(),
                'average_length': self._get_average_length()
            },
            'content': self.ingested_content
        }
        
        from ..core.file_utils import safe_json_dump
        safe_json_dump(analysis, output_path)
    
    def _get_tones_distribution(self) -> Dict[str, int]:
        """Get distribution of tones"""
        distribution = {}
        for item in self.ingested_content:
            tone = item['tone']
            distribution[tone] = distribution.get(tone, 0) + 1
        return distribution
    
    def _get_consistency_rate(self) -> float:
        """Get consistency rate"""
        if not self.ingested_content:
            return 0.0
        consistent_count = sum(1 for item in self.ingested_content if item['is_consistent'])
        return consistent_count / len(self.ingested_content)
    
    def _get_average_length(self) -> Dict[str, float]:
        """Get average content length"""
        if not self.ingested_content:
            return {'characters': 0, 'words': 0}
        
        avg_chars = sum(item['length'] for item in self.ingested_content) / len(self.ingested_content)
        avg_words = sum(item['word_count'] for item in self.ingested_content) / len(self.ingested_content)
        
        return {'characters': avg_chars, 'words': avg_words}