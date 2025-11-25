"""Test script to verify brand voice embeddings are working correctly."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_content_factory.agents.content_writer_agent import ContentWriterAgent
from ai_content_factory.core.metrics import ContentMetricsEvaluator
from ai_content_factory.core.metrics_logger import MetricsLogger
from ai_content_factory.utils.logger import get_logger

logger = get_logger(__name__)


def test_brand_voice_embeddings():
    """Test the brand voice embeddings with article generation."""
    print("\n" + "="*80)
    print("Testing Brand Voice Embeddings with Content Generation")
    print("="*80 + "\n")

    try:
        # Initialize agent
        print("📝 Initializing ContentWriterAgent...")
        agent = ContentWriterAgent()
        print("✅ Agent initialized successfully\n")

        # Initialize metrics system
        print("📊 Initializing metrics evaluator...")
        evaluator = ContentMetricsEvaluator()
        metrics_logger = MetricsLogger()
        print("✅ Metrics system initialized\n")

        # Test parameters
        topic = "Benefits of Vitamin C for Skin"
        keyword = "vitamin c serum"
        target_word_count = 800
        audience = "skincare enthusiasts"

        print("📄 Generating article...")
        print(f"   Topic: {topic}")
        print(f"   Keyword: {keyword}")
        print(f"   Target: {target_word_count} words")
        print(f"   Audience: {audience}\n")

        # Time the generation
        start_time = time.time()

        # Generate article with auto-save to outputs folder
        output_path = Path("outputs") / "brand_voice_test_article.md"
        article = agent.generate_article(
            topic=topic,
            target_keyword=keyword,
            target_word_count=target_word_count,
            target_audience=audience,
            content_type="blog_post",
            output_path=str(output_path)
        )

        generation_time = time.time() - start_time

        print(f"✅ Article generated in {generation_time:.1f}s\n")

        # Evaluate metrics
        print("📊 Evaluating article metrics...")
        metrics = evaluator.evaluate_article(
            article=article,
            target_word_count=target_word_count,
            primary_keyword=keyword,
            generation_time=generation_time
        )

        # Log metrics to files
        metrics_logger.log_metrics(metrics, metadata={
            'topic': topic,
            'keyword': keyword,
            'test_type': 'brand_voice_embeddings'
        })

        # Display results
        print("\n" + "="*80)
        print("📊 METRICS RESULTS")
        print("="*80)
        print(f"\n✨ Content Quality:        {metrics.content_quality_score:.1f}/100")
        print(f"🎯 Brand Voice Similarity: {metrics.brand_voice_similarity:.2f}")
        print(f"🔑 Keyword Density:        {metrics.keyword_density:.2f}%")
        print(f"📖 Readability (Flesch):   {metrics.readability_score:.1f}")
        print(f"📝 Word Count Accuracy:    {metrics.word_count_accuracy:.1f}%")
        print(f"⏱️  Generation Time:        {metrics.generation_time:.1f}s")
        print(f"📋 Heading Structure:      {metrics.heading_structure_score:.2f}")
        print(f"🔍 SEO Requirements:       {metrics.seo_requirements_score:.2f}")

        # Check if requirements met
        passes, failures = metrics.passes_requirements()
        print(f"\n{'='*80}")
        if passes:
            print("✅ ALL KPI REQUIREMENTS MET!")
        else:
            print("❌ SOME KPI REQUIREMENTS NOT MET:")
            for failure in failures:
                print(f"   • {failure}")

        print(f"\n{'='*80}")
        print("📁 FILES SAVED:")
        print(f"   • Article:       {output_path}")
        print("   • Metrics JSON:  metrics_logs/metrics_history.json")
        print("   • Metrics CSV:   metrics_logs/metrics_history.csv")

        print(f"\n{'='*80}")
        print("📖 Article Preview (first 500 chars):")
        print("-"*80)
        print(article.markdown_content[:500] + "...")
        print("-"*80)

        print(f"\n{'='*80}")
        print("✅ Brand Voice Embedding Test Complete!")
        print("="*80 + "\n")

        return passes

    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_brand_voice_embeddings()
    sys.exit(0 if success else 1)
