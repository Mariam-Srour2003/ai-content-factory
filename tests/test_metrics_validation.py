"""
Comprehensive Test Suite for Content Writer Agent Metrics Validation

Tests all 8 KPI requirements:
1. Content Quality Score ≥ 70/100
2. Brand Voice Similarity ≥ 0.80
3. Keyword Density 1-2%
4. Readability Score ≥ 60
5. Word Count Accuracy ±10%
6. Generation Time < 5 min
7. Heading Structure 100%
8. SEO Requirements 100%
"""

import sys
import time
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_content_factory.agents.content_writer_agent import ContentWriterAgent
from ai_content_factory.core.metrics import ContentMetricsEvaluator
from ai_content_factory.core.metrics_logger import MetricsLogger


class TestContentWriterMetrics(unittest.TestCase):
    """Test suite for validating content writer agent metrics."""

    @classmethod
    def setUpClass(cls):
        """Initialize agent and metrics evaluator once for all tests."""
        cls.agent = ContentWriterAgent()
        cls.evaluator = ContentMetricsEvaluator()
        cls.logger = MetricsLogger()

    def _generate_and_evaluate(
        self,
        topic: str,
        keyword: str,
        target_word_count: int = 800,
        audience: str = "general readers"
    ):
        """Helper method to generate article and evaluate metrics."""
        start_time = time.time()

        article = self.agent.generate_article(
            topic=topic,
            target_keyword=keyword,
            target_word_count=target_word_count,
            target_audience=audience,
            content_type="blog_post"
        )

        generation_time = time.time() - start_time

        metrics = self.evaluator.evaluate_article(
            article=article,
            target_word_count=target_word_count,
            primary_keyword=keyword,
            generation_time=generation_time
        )

        # Log metrics
        self.logger.log_metrics(
            metrics,
            metadata={
                'topic': topic,
                'keyword': keyword,
                'target_word_count': target_word_count,
                'audience': audience
            }
        )

        return article, metrics

    def test_content_quality_score(self):
        """Test KPI #1: Content Quality Score ≥ 70/100"""
        print("\n🧪 Testing KPI #1: Content Quality Score...")

        article, metrics = self._generate_and_evaluate(
            topic="Benefits of Green Tea",
            keyword="green tea benefits",
            target_word_count=800
        )

        self.assertGreaterEqual(
            metrics.content_quality_score,
            70,
            f"Content quality score {metrics.content_quality_score:.1f} below minimum 70"
        )
        print(f"✅ Content Quality Score: {metrics.content_quality_score:.1f}/100 (≥70)")

    def test_brand_voice_similarity(self):
        """Test KPI #2: Brand Voice Similarity ≥ 0.80"""
        print("\n🧪 Testing KPI #2: Brand Voice Similarity...")

        article, metrics = self._generate_and_evaluate(
            topic="Skincare Routine for Beginners",
            keyword="skincare routine",
            target_word_count=800
        )

        self.assertGreaterEqual(
            metrics.brand_voice_similarity,
            0.80,
            f"Brand voice similarity {metrics.brand_voice_similarity:.2f} below minimum 0.80"
        )
        print(f"✅ Brand Voice Similarity: {metrics.brand_voice_similarity:.2f} (≥0.80)")

    def test_keyword_density(self):
        """Test KPI #3: Keyword Density 1-2%"""
        print("\n🧪 Testing KPI #3: Keyword Density...")

        article, metrics = self._generate_and_evaluate(
            topic="Best Anti-Aging Serums",
            keyword="anti-aging serum",
            target_word_count=800
        )

        self.assertGreaterEqual(
            metrics.keyword_density,
            1.0,
            f"Keyword density {metrics.keyword_density:.2f}% below minimum 1%"
        )
        self.assertLessEqual(
            metrics.keyword_density,
            2.0,
            f"Keyword density {metrics.keyword_density:.2f}% above maximum 2%"
        )
        print(f"✅ Keyword Density: {metrics.keyword_density:.2f}% (1-2%)")

    def test_readability_score(self):
        """Test KPI #4: Readability Score ≥ 60"""
        print("\n🧪 Testing KPI #4: Readability Score...")

        article, metrics = self._generate_and_evaluate(
            topic="How to Use Retinol Safely",
            keyword="retinol guide",
            target_word_count=800
        )

        self.assertGreaterEqual(
            metrics.readability_score,
            60,
            f"Readability score {metrics.readability_score:.1f} below minimum 60"
        )
        print(f"✅ Readability Score: {metrics.readability_score:.1f} (≥60)")

    def test_word_count_accuracy(self):
        """Test KPI #5: Word Count Accuracy ±10%"""
        print("\n🧪 Testing KPI #5: Word Count Accuracy...")

        article, metrics = self._generate_and_evaluate(
            topic="Benefits of Hyaluronic Acid",
            keyword="hyaluronic acid",
            target_word_count=1000
        )

        self.assertGreaterEqual(
            metrics.word_count_accuracy,
            90,
            f"Word count accuracy {metrics.word_count_accuracy:.1f}% below minimum 90%"
        )
        self.assertLessEqual(
            metrics.word_count_accuracy,
            110,
            f"Word count accuracy {metrics.word_count_accuracy:.1f}% above maximum 110%"
        )
        print(f"✅ Word Count Accuracy: {metrics.word_count_accuracy:.1f}% (90-110%)")

    def test_generation_time(self):
        """Test KPI #6: Generation Time < 5 min"""
        print("\n🧪 Testing KPI #6: Generation Time...")

        article, metrics = self._generate_and_evaluate(
            topic="Natural Remedies for Acne",
            keyword="acne remedies",
            target_word_count=800
        )

        self.assertLess(
            metrics.generation_time,
            300,
            f"Generation time {metrics.generation_time:.1f}s exceeds maximum 300s"
        )
        print(f"✅ Generation Time: {metrics.generation_time:.1f}s (<300s)")

    def test_heading_structure(self):
        """Test KPI #7: Heading Structure 100%"""
        print("\n🧪 Testing KPI #7: Heading Structure...")

        article, metrics = self._generate_and_evaluate(
            topic="Complete Guide to Sunscreen",
            keyword="sunscreen guide",
            target_word_count=800
        )

        self.assertEqual(
            metrics.heading_structure_score,
            1.0,
            f"Heading structure score {metrics.heading_structure_score:.2f} not perfect"
        )
        print(f"✅ Heading Structure: {metrics.heading_structure_score:.2f} (1.0)")

    def test_seo_requirements(self):
        """Test KPI #8: SEO Requirements 100%"""
        print("\n🧪 Testing KPI #8: SEO Requirements...")

        article, metrics = self._generate_and_evaluate(
            topic="Best Moisturizers for Dry Skin",
            keyword="moisturizer dry skin",
            target_word_count=800
        )

        self.assertEqual(
            metrics.seo_requirements_score,
            1.0,
            f"SEO requirements score {metrics.seo_requirements_score:.2f} not perfect"
        )
        print(f"✅ SEO Requirements: {metrics.seo_requirements_score:.2f} (1.0)")

    def test_all_kpis_simultaneously(self):
        """Test all KPIs together in a single article generation."""
        print("\n🧪 Testing ALL KPIs simultaneously...")

        article, metrics = self._generate_and_evaluate(
            topic="Complete Skincare Routine Guide",
            keyword="skincare routine",
            target_word_count=1200,
            audience="skincare enthusiasts"
        )

        passes, failures = metrics.passes_requirements()

        if not passes:
            print("\n❌ Some KPIs failed:")
            for failure in failures:
                print(f"   • {failure}")

        self.assertTrue(
            passes,
            f"Article failed to meet all requirements: {failures}"
        )
        print("✅ ALL KPIs PASSED!")


def run_tests_with_report():
    """Run tests and generate comprehensive report."""
    print("\n" + "="*80)
    print("  CONTENT WRITER AGENT - METRICS VALIDATION TEST SUITE")
    print("="*80)

    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestContentWriterMetrics)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80)
    print(f"\nTests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED - Agent meets all KPI requirements!")
    else:
        print("\n❌ SOME TESTS FAILED - Review failures above")

    # Display metrics history
    logger = MetricsLogger()
    stats = logger.get_summary_stats()

    if stats:
        print("\n" + "="*80)
        print("  HISTORICAL METRICS SUMMARY")
        print("="*80)
        print(f"\nTotal Articles Generated: {stats['total_articles']}")
        print(f"Overall Pass Rate: {stats['pass_rate']:.1f}%")

        print("\nAverage Scores:")
        for metric, values in stats.items():
            if isinstance(values, dict) and 'average' in values:
                print(f"  • {metric.replace('_', ' ').title()}: {values['average']:.2f}")

    return result


if __name__ == "__main__":
    result = run_tests_with_report()
    sys.exit(0 if result.wasSuccessful() else 1)
