"""Metrics tracking and logging system."""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

from .metrics import ContentMetrics


class MetricsLogger:
    """Logs and tracks content generation metrics over time."""

    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize metrics logger.

        Args:
            log_dir: Directory to store metrics logs. Defaults to './metrics_logs'
        """
        self.log_dir = log_dir or Path("./metrics_logs")
        self.log_dir.mkdir(exist_ok=True)

        self.json_log = self.log_dir / "metrics_history.json"
        self.csv_log = self.log_dir / "metrics_history.csv"

        # Initialize CSV if it doesn't exist
        if not self.csv_log.exists():
            self._init_csv()

    def _init_csv(self):
        """Initialize CSV file with headers."""
        headers = [
            'timestamp',
            'content_quality_score',
            'brand_voice_similarity',
            'keyword_density',
            'readability_score',
            'word_count_accuracy',
            'generation_time',
            'heading_structure_score',
            'seo_requirements_score',
            'passes_requirements',
            'actual_word_count',
            'target_word_count'
        ]

        with open(self.csv_log, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

    def log_metrics(self, metrics: ContentMetrics, metadata: Optional[Dict] = None):
        """Log metrics to both JSON and CSV files.

        Args:
            metrics: The metrics to log
            metadata: Optional additional metadata (topic, keyword, etc.)
        """
        # Prepare data
        passes, _ = metrics.passes_requirements()

        data = {
            **metrics.to_dict(),
            'passes_requirements': passes,
            'metadata': metadata or {}
        }

        # Log to JSON
        self._log_json(data)

        # Log to CSV
        self._log_csv(metrics, passes)

    def _log_json(self, data: Dict):
        """Append to JSON log file."""
        # Read existing data
        if self.json_log.exists():
            with open(self.json_log, 'r', encoding='utf-8') as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
        else:
            history = []

        # Append new data
        history.append(data)

        # Write back
        with open(self.json_log, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)

    def _log_csv(self, metrics: ContentMetrics, passes: bool):
        """Append to CSV log file."""
        row = {
            'timestamp': metrics.timestamp,
            'content_quality_score': metrics.content_quality_score,
            'brand_voice_similarity': metrics.brand_voice_similarity,
            'keyword_density': metrics.keyword_density,
            'readability_score': metrics.readability_score,
            'word_count_accuracy': metrics.word_count_accuracy,
            'generation_time': metrics.generation_time,
            'heading_structure_score': metrics.heading_structure_score,
            'seo_requirements_score': metrics.seo_requirements_score,
            'passes_requirements': passes,
            'actual_word_count': metrics.details.get('actual_word_count', 0),
            'target_word_count': metrics.details.get('target_word_count', 0)
        }

        with open(self.csv_log, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writerow(row)

    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get metrics history.

        Args:
            limit: Maximum number of recent entries to return

        Returns:
            List of metrics dictionaries
        """
        if not self.json_log.exists():
            return []

        with open(self.json_log, 'r', encoding='utf-8') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                return []

        if limit:
            return history[-limit:]
        return history

    def get_summary_stats(self) -> Dict:
        """Get summary statistics across all logged metrics.

        Returns:
            Dictionary with average, min, max for each metric
        """
        history = self.get_history()

        if not history:
            return {}

        # Extract metric values
        metrics = {
            'content_quality_score': [],
            'brand_voice_similarity': [],
            'keyword_density': [],
            'readability_score': [],
            'word_count_accuracy': [],
            'generation_time': [],
            'heading_structure_score': [],
            'seo_requirements_score': []
        }

        passes_count = 0

        for entry in history:
            for key in metrics.keys():
                if key in entry:
                    metrics[key].append(entry[key])

            if entry.get('passes_requirements'):
                passes_count += 1

        # Calculate stats
        stats = {}
        for key, values in metrics.items():
            if values:
                stats[key] = {
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }

        stats['pass_rate'] = (passes_count / len(history) * 100) if history else 0
        stats['total_articles'] = len(history)

        return stats

    def print_summary(self):
        """Print summary statistics."""
        stats = self.get_summary_stats()

        if not stats:
            print("No metrics logged yet.")
            return

        print("\n" + "="*70)
        print("  📈 METRICS SUMMARY")
        print("="*70)
        print(f"\nTotal Articles: {stats['total_articles']}")
        print(f"Pass Rate: {stats['pass_rate']:.1f}%")

        print("\n" + "-"*70)
        print("AVERAGE SCORES")
        print("-"*70)

        metric_names = {
            'content_quality_score': 'Content Quality',
            'brand_voice_similarity': 'Brand Voice',
            'keyword_density': 'Keyword Density',
            'readability_score': 'Readability',
            'word_count_accuracy': 'Word Count Accuracy',
            'generation_time': 'Generation Time',
            'heading_structure_score': 'Heading Structure',
            'seo_requirements_score': 'SEO Requirements'
        }

        for key, name in metric_names.items():
            if key in stats:
                avg = stats[key]['average']
                min_val = stats[key]['min']
                max_val = stats[key]['max']

                if key == 'generation_time':
                    print(f"{name:.<30} {avg:.1f}s (range: {min_val:.1f}s - {max_val:.1f}s)")
                elif key in ['brand_voice_similarity', 'heading_structure_score', 'seo_requirements_score']:
                    print(f"{name:.<30} {avg:.2f} (range: {min_val:.2f} - {max_val:.2f})")
                elif key == 'keyword_density':
                    print(f"{name:.<30} {avg:.2f}% (range: {min_val:.2f}% - {max_val:.2f}%)")
                else:
                    print(f"{name:.<30} {avg:.1f} (range: {min_val:.1f} - {max_val:.1f})")

        print("\n" + "="*70 + "\n")
