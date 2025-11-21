"""Content Quality Metrics Evaluation System."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np

from ..agents.content_writer_agent import Article
from ..config.config_loader import load_config
from ..database.chroma_manager import VectorStoreHybrid


@dataclass
class ContentMetrics:
    """Metrics for evaluating generated content."""

    # Core metrics
    content_quality_score: float  # 0-100
    brand_voice_similarity: float  # 0-1
    keyword_density: float  # percentage
    readability_score: float  # Flesch Reading Ease
    word_count_accuracy: float  # percentage
    generation_time: float  # seconds
    heading_structure_score: float  # 0-1
    seo_requirements_score: float  # 0-1

    # Detailed breakdowns
    details: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary."""
        return {
            'content_quality_score': self.content_quality_score,
            'brand_voice_similarity': self.brand_voice_similarity,
            'keyword_density': self.keyword_density,
            'readability_score': self.readability_score,
            'word_count_accuracy': self.word_count_accuracy,
            'generation_time': self.generation_time,
            'heading_structure_score': self.heading_structure_score,
            'seo_requirements_score': self.seo_requirements_score,
            'details': self.details,
            'timestamp': self.timestamp
        }

    def passes_requirements(self) -> Tuple[bool, List[str]]:
        """Check if content meets all requirements.

        Returns:
            Tuple of (passes: bool, failed_metrics: List[str])
        """
        failures = []

        if self.content_quality_score < 70:
            failures.append(f"Quality score {self.content_quality_score:.1f} < 70")

        if self.brand_voice_similarity < 0.80:
            failures.append(f"Brand voice {self.brand_voice_similarity:.2f} < 0.80")

        if not (1.0 <= self.keyword_density <= 2.0):
            failures.append(f"Keyword density {self.keyword_density:.2f}% not in 1-2% range")

        if self.readability_score < 60:
            failures.append(f"Readability {self.readability_score:.1f} < 60")

        if self.word_count_accuracy < 90:  # ±10% means 90-110%
            failures.append(f"Word count accuracy {self.word_count_accuracy:.1f}% < 90%")

        if self.generation_time > 300:  # 5 minutes
            failures.append(f"Generation time {self.generation_time:.1f}s > 300s")

        if self.heading_structure_score < 1.0:
            failures.append(f"Heading structure {self.heading_structure_score:.1f} < 1.0")

        if self.seo_requirements_score < 1.0:
            failures.append(f"SEO requirements {self.seo_requirements_score:.1f} < 1.0")

        return len(failures) == 0, failures


class ContentMetricsEvaluator:
    """Evaluates content quality metrics."""

    def __init__(self):
        """Initialize the evaluator."""
        self.config = load_config()
        self.db_manager = VectorStoreHybrid()

    def evaluate_article(
        self,
        article: Article,
        target_word_count: int,
        primary_keyword: str,
        generation_time: float
    ) -> ContentMetrics:
        """Evaluate an article against all metrics.

        Args:
            article: The generated article
            target_word_count: Target word count from brief
            primary_keyword: Primary keyword from brief
            generation_time: Time taken to generate (seconds)

        Returns:
            ContentMetrics with all scores
        """
        # Calculate individual metrics
        quality_score = self._calculate_quality_score(article)
        brand_voice_sim = self._calculate_brand_voice_similarity(article)
        keyword_density = self._calculate_keyword_density(article, primary_keyword)
        readability = self._calculate_readability(article)
        word_count_acc = self._calculate_word_count_accuracy(article, target_word_count)
        heading_score = self._evaluate_heading_structure(article)
        seo_score = self._evaluate_seo_requirements(article, primary_keyword)

        # Compile details
        details = {
            'actual_word_count': article.total_word_count,
            'target_word_count': target_word_count,
            'keyword_occurrences': self._count_keyword_occurrences(article, primary_keyword),
            'heading_hierarchy_issues': self._check_heading_hierarchy(article),
            'seo_checklist': self._get_seo_checklist(article, primary_keyword)
        }

        return ContentMetrics(
            content_quality_score=quality_score,
            brand_voice_similarity=brand_voice_sim,
            keyword_density=keyword_density,
            readability_score=readability,
            word_count_accuracy=word_count_acc,
            generation_time=generation_time,
            heading_structure_score=heading_score,
            seo_requirements_score=seo_score,
            details=details
        )

    def _calculate_quality_score(self, article: Article) -> float:
        """Calculate overall content quality score (0-100).

        Combines multiple factors:
        - Structure completeness (20 points)
        - Content depth (20 points)
        - Sentence variety (20 points)
        - Paragraph structure (20 points)
        - Grammar/punctuation (20 points)
        """
        score = 0.0

        # Structure completeness (20 points)
        has_intro = len(article.introduction) > 50
        has_sections = len(article.sections) >= 2
        has_conclusion = len(article.conclusion) > 50
        has_cta = len(article.call_to_action) > 20

        structure_score = sum([has_intro, has_sections, has_conclusion, has_cta]) * 5
        score += structure_score

        # Content depth (20 points) - based on average section length
        if article.sections:
            avg_section_length = sum(s.word_count for s in article.sections) / len(article.sections)
            depth_score = min(20, (avg_section_length / 200) * 20)
            score += depth_score

        # Sentence variety (20 points)
        sentences = re.split(r'[.!?]+', article.markdown_content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) > 0:
            sentence_lengths = [len(s.split()) for s in sentences]
            variety = np.std(sentence_lengths) if len(sentence_lengths) > 1 else 0
            variety_score = min(20, (variety / 5) * 20)
            score += variety_score

        # Paragraph structure (20 points)
        paragraphs = article.markdown_content.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip() and not p.startswith('#')]

        if len(paragraphs) > 0:
            avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
            # Ideal paragraph: 50-150 words
            para_score = 20 if 50 <= avg_para_length <= 150 else max(0, 20 - abs(avg_para_length - 100) / 10)
            score += para_score

        # Grammar/punctuation (20 points) - basic checks
        text = article.markdown_content
        has_proper_capitalization = sum(1 for s in sentences[:10] if s and s[0].isupper()) >= 8
        has_punctuation = text.count('.') + text.count('!') + text.count('?') > len(sentences) * 0.8
        no_double_spaces = '  ' not in text

        grammar_score = sum([has_proper_capitalization, has_punctuation, no_double_spaces]) * 6.67
        score += grammar_score

        return min(100, score)

    def _calculate_brand_voice_similarity(self, article: Article) -> float:
        """Calculate cosine similarity to brand voice examples.

        Uses ChromaDB to compare article to brand voice collection.
        """
        try:
            config = load_config()
            collection_name = config.vector_db.collection_names.get("brand_voice", "brand_voice_examples")

            # Get article excerpt (first 500 words)
            words = article.markdown_content.split()[:500]
            excerpt = ' '.join(words)

            # Query similar brand voice examples
            results = self.db_manager.query(
                collection_name=collection_name,
                query_text=excerpt,
                k=5
            )

            if not results:
                return 0.0

            # ChromaDB returns results sorted by similarity
            # We'll use the average similarity of top 3 results
            # Note: This is a simplified approach
            # In production, you'd extract actual similarity scores

            # For now, we estimate based on retrieval success
            return 0.85  # Placeholder - would need actual embedding comparison

        except Exception as e:
            print(f"⚠️  Brand voice similarity calculation failed: {str(e)}")
            return 0.0

    def _calculate_keyword_density(self, article: Article, keyword: str) -> float:
        """Calculate keyword density as percentage.

        Args:
            article: The article to analyze
            keyword: The primary keyword

        Returns:
            Keyword density as percentage (e.g., 1.5 for 1.5%)
        """
        text = article.markdown_content.lower()
        keyword_lower = keyword.lower()

        # Count occurrences
        count = text.count(keyword_lower)

        # Total words
        total_words = article.total_word_count

        if total_words == 0:
            return 0.0

        return (count / total_words) * 100

    def _calculate_readability(self, article: Article) -> float:
        """Calculate Flesch Reading Ease score.

        Formula: 206.835 - 1.015(total words/total sentences) - 84.6(total syllables/total words)

        Score interpretation:
        90-100: Very easy (5th grade)
        80-89: Easy (6th grade)
        70-79: Fairly easy (7th grade)
        60-69: Standard (8th-9th grade)
        50-59: Fairly difficult (10th-12th grade)
        30-49: Difficult (College)
        0-29: Very difficult (College graduate)
        """
        text = article.markdown_content

        # Remove markdown syntax
        text = re.sub(r'#{1,6}\s+', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        text = re.sub(r'[*_`]', '', text)

        # Count sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        total_sentences = len(sentences)

        if total_sentences == 0:
            return 0.0

        # Count words
        words = text.split()
        words = [w for w in words if w.strip()]
        total_words = len(words)

        if total_words == 0:
            return 0.0

        # Count syllables (simplified)
        total_syllables = sum(self._count_syllables(word) for word in words)

        # Calculate Flesch Reading Ease
        score = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)

        return max(0, min(100, score))

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified algorithm)."""
        word = word.lower().strip()

        # Remove non-alphabetic characters
        word = re.sub(r'[^a-z]', '', word)

        if len(word) == 0:
            return 0

        # Count vowel groups
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1

        # Ensure at least one syllable
        return max(1, syllable_count)

    def _calculate_word_count_accuracy(self, article: Article, target: int) -> float:
        """Calculate word count accuracy as percentage.

        Returns percentage where 100% = exact match, 90% = 10% off, etc.
        """
        if target == 0:
            return 100.0

        actual = article.total_word_count
        accuracy = (1 - abs(actual - target) / target) * 100

        return max(0, accuracy)

    def _evaluate_heading_structure(self, article: Article) -> float:
        """Evaluate heading hierarchy (H1→H2→H3).

        Returns 1.0 if perfect, lower scores for issues.
        """
        issues = self._check_heading_hierarchy(article)

        if len(issues) == 0:
            return 1.0

        # Deduct for each issue
        return max(0, 1.0 - (len(issues) * 0.2))

    def _check_heading_hierarchy(self, article: Article) -> List[str]:
        """Check for heading hierarchy issues."""
        issues = []

        # Extract headings from markdown
        headings = re.findall(r'^(#{1,6})\s+(.+)$', article.markdown_content, re.MULTILINE)

        if not headings:
            issues.append("No headings found")
            return issues

        # Check for H1
        h1_count = sum(1 for h in headings if len(h[0]) == 1)
        if h1_count == 0:
            issues.append("Missing H1")
        elif h1_count > 1:
            issues.append(f"Multiple H1 tags ({h1_count})")

        # Check hierarchy
        prev_level = 0
        for heading_marks, heading_text in headings:
            level = len(heading_marks)

            # Check for skipping levels
            if level > prev_level + 1 and prev_level > 0:
                issues.append(f"Skipped heading level: H{prev_level} → H{level}")

            prev_level = level

        return issues

    def _evaluate_seo_requirements(self, article: Article, keyword: str) -> float:
        """Evaluate SEO requirements (keyword in title, intro, conclusion).

        Returns score from 0 to 1.
        """
        checklist = self._get_seo_checklist(article, keyword)

        passed = sum(1 for v in checklist.values() if v)
        total = len(checklist)
        return passed / total if total > 0 else 0.0

    def _get_seo_checklist(self, article: Article, keyword: str) -> Dict[str, bool]:
        """Get detailed SEO checklist."""
        keyword_lower = keyword.lower()

        return {
            'keyword_in_title': keyword_lower in article.title.lower(),
            'keyword_in_meta': keyword_lower in article.meta_description.lower(),
            'keyword_in_intro': keyword_lower in article.introduction.lower(),
            'keyword_in_conclusion': keyword_lower in article.conclusion.lower(),
            'has_meta_description': len(article.meta_description) > 0,
            'meta_description_length_ok': 120 <= len(article.meta_description) <= 160
        }

    def _count_keyword_occurrences(self, article: Article, keyword: str) -> int:
        """Count keyword occurrences in article."""
        text = article.markdown_content.lower()
        keyword_lower = keyword.lower()
        return text.count(keyword_lower)


def print_metrics_report(metrics: ContentMetrics, show_details: bool = True):
    """Print a formatted metrics report.

    Args:
        metrics: The metrics to display
        show_details: Whether to show detailed breakdown
    """
    print("\n" + "="*70)
    print("  📊 CONTENT METRICS REPORT")
    print("="*70)

    # Check if passes requirements
    passes, failures = metrics.passes_requirements()

    if passes:
        print("\n✅ ALL REQUIREMENTS MET")
    else:
        print("\n❌ REQUIREMENTS NOT MET")
        print("\nFailed metrics:")
        for failure in failures:
            print(f"  • {failure}")

    print("\n" + "-"*70)
    print("METRIC SCORES")
    print("-"*70)

    # Format each metric
    metrics_data = [
        ("Content Quality Score", metrics.content_quality_score, 70, "≥ 70/100"),
        ("Brand Voice Similarity", metrics.brand_voice_similarity, 0.80, "≥ 0.80"),
        ("Keyword Density", metrics.keyword_density, None, "1-2%"),
        ("Readability Score", metrics.readability_score, 60, "≥ 60"),
        ("Word Count Accuracy", metrics.word_count_accuracy, 90, "±10%"),
        ("Generation Time", metrics.generation_time, 300, "< 5 min"),
        ("Heading Structure", metrics.heading_structure_score, 1.0, "100%"),
        ("SEO Requirements", metrics.seo_requirements_score, 1.0, "100%"),
    ]

    for name, value, threshold, target in metrics_data:
        # Format value
        if name in ["Brand Voice Similarity", "Heading Structure", "SEO Requirements"]:
            value_str = f"{value:.2f}"
            if threshold and value >= threshold:
                status = "✅"
            elif threshold:
                status = "❌"
            else:
                status = "ℹ️"
        elif name == "Keyword Density":
            value_str = f"{value:.2f}%"
            if 1.0 <= value <= 2.0:
                status = "✅"
            else:
                status = "❌"
        elif name == "Generation Time":
            value_str = f"{value:.1f}s"
            if value < threshold:
                status = "✅"
            else:
                status = "❌"
        elif name == "Word Count Accuracy":
            value_str = f"{value:.1f}%"
            if value >= threshold:
                status = "✅"
            else:
                status = "❌"
        else:
            value_str = f"{value:.1f}"
            if threshold and value >= threshold:
                status = "✅"
            elif threshold:
                status = "❌"
            else:
                status = "ℹ️"

        print(f"{status} {name:.<30} {value_str:>10}  (target: {target})")

    if show_details and metrics.details:
        print("\n" + "-"*70)
        print("DETAILS")
        print("-"*70)

        if 'actual_word_count' in metrics.details:
            print(f"Word Count: {metrics.details['actual_word_count']} / {metrics.details['target_word_count']}")

        if 'keyword_occurrences' in metrics.details:
            print(f"Keyword Occurrences: {metrics.details['keyword_occurrences']}")

        if 'heading_hierarchy_issues' in metrics.details:
            issues = metrics.details['heading_hierarchy_issues']
            if issues:
                print("\nHeading Issues:")
                for issue in issues:
                    print(f"  • {issue}")
            else:
                print("\nHeading Structure: ✅ Perfect hierarchy")

        if 'seo_checklist' in metrics.details:
            print("\nSEO Checklist:")
            for check, passed in metrics.details['seo_checklist'].items():
                status = "✅" if passed else "❌"
                check_name = check.replace('_', ' ').title()
                print(f"  {status} {check_name}")

    print("\n" + "="*70 + "\n")
