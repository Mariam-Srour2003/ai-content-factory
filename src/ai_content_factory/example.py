# this code is for 
#to run this file in terminal use uv run src/ai_content_factory/example.py 

# src/ai_content_factory/example.py
from ai_content_factory.agents.brand_voice_agent import BrandVoiceAgent
from ai_content_factory.mypackages.tone_analyzer import ToneAnalyzer

# Sample content to analyze
inputs = [
    "Please ensure that all reports are submitted before the deadline. We expect thorough and detailed analysis.",
    "Hey, let's catch up over coffee tomorrow and chat about the project. It should be fun!",
    "This system keeps crashing, and it's getting worse every day. We really need a solution urgently!",
    "I'm really excited about the direction we're heading in this project! The team is doing great work!",
    "The meeting will take place at 3 PM tomorrow in the main conference room. Please be on time.",
    "Keep up the great work! We're almost there, just a little more effort and we'll succeed!",
]

# Path to the example content file
example_content_path = 'data/brand_voice_examples.json'

# Define tone labels for zero-shot classification
tone_labels = ['formal', 'casual', 'technical', 'urgent']

print("=" * 80)
print("COMPARING TONE ANALYSIS MODELS")
print("=" * 80)

for i, content in enumerate(inputs, 1):
    print(f"\n{'='*60}")
    print(f"EXAMPLE {i}:")
    print(f"Text: {content}")
    print(f"{'='*60}")
    
    # Initialize both tone analyzers
    zero_shot_analyzer = ToneAnalyzer(candidate_labels=tone_labels, model_type='zero-shot')
    sentiment_analyzer = ToneAnalyzer(model_type='sentiment')
    
    # Get tone predictions from both models
    zero_shot_tone = zero_shot_analyzer.analyze(content)
    sentiment_tone = sentiment_analyzer.analyze(content)
    
    # Run brand voice agent (uses zero-shot by default)
    agent = BrandVoiceAgent(content=content, example_content_path=example_content_path)
    agent_results = agent.run()
    
    print(f"\nMODEL COMPARISON:")
    print(f"  Zero-Shot Classification: {zero_shot_tone}")
    print(f"  Sentiment Analysis: {sentiment_tone}")
    print(f"  Brand Voice Consistency: {agent_results['is_consistent']}")
    
    # Show detailed scores for zero-shot classification
    print(f"\nDETAILED ZERO-SHOT SCORES:")
    detailed_result = zero_shot_analyzer.analyzer(content, candidate_labels=tone_labels)
    for label, score in zip(detailed_result['labels'], detailed_result['scores']):
        print(f"    {label}: {score:.3f}")
    
    # Show detailed sentiment scores
    print(f"\nDETAILED SENTIMENT SCORES:")
    sentiment_result = sentiment_analyzer.analyzer(content)
    if isinstance(sentiment_result, list):
        for result in sentiment_result:
            print(f"    {result['label']}: {result['score']:.3f}")
    else:
        print(f"    {sentiment_result['label']}: {sentiment_result['score']:.3f}")

print(f"\n{'='*80}")
print("SUMMARY: Zero-shot classification is better for detecting specific tones")
print("like 'formal', 'casual', 'technical', while sentiment analysis detects")
print("overall sentiment (POSITIVE/NEGATIVE).")
print("=" * 80)