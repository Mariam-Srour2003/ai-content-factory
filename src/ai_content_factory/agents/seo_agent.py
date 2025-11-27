import random
import json
import numpy as np
from datetime import datetime
from collections import Counter
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import requests

class KeywordResearchTool:
    """
    Advanced keyword research with difficulty estimation and intent classification
    """

    def __init__(self):
        self.search_volume_db = self._initialize_volume_database()

    def _initialize_volume_database(self):
        """Initialize a mock search volume database"""
        volume_ranges = {
            'high': (10000, 100000),
            'medium': (1000, 10000),
            'low': (10, 1000)
        }
        return volume_ranges

    def estimate_search_volume(self, keyword):
        """Estimate search volume for keywords"""
        keyword_lower = keyword.lower()

        # Simple volume estimation based on keyword characteristics
        if any(word in keyword_lower for word in ['what', 'how', 'why', 'best', 'review']):
            volume_range = self.search_volume_db['high']
        elif len(keyword.split()) == 1:
            volume_range = self.search_volume_db['medium']
        else:
            volume_range = self.search_volume_db['low']

        return random.randint(volume_range[0], volume_range[1])

    def estimate_keyword_difficulty(self, keyword):
        """Estimate keyword difficulty (0-100 scale)"""
        factors = {
            'word_count': len(keyword.split()) * 5,  # Longer keywords are easier
            'has_question': 20 if any(word in keyword.lower() for word in ['what', 'how', 'why']) else 0,
            'has_commercial_intent': 25 if any(word in keyword.lower() for word in ['buy', 'price', 'review', 'best']) else 0,
            'competition_level': random.randint(30, 70)
        }

        # Lower score = easier to rank
        base_difficulty = 50
        difficulty = base_difficulty - sum(factors.values())

        return max(10, min(100, difficulty))

    def classify_search_intent(self, keyword):
        """Classify search intent"""
        keyword_lower = keyword.lower()

        # Informational intent
        info_indicators = ['what', 'how', 'why', 'guide', 'tutorial', 'learn']
        if any(indicator in keyword_lower for indicator in info_indicators):
            return 'informational'

        # Transactional intent
        transaction_indicators = ['buy', 'price', 'deal', 'discount', 'purchase']
        if any(indicator in keyword_lower for indicator in transaction_indicators):
            return 'transactional'

        # Commercial investigation
        commercial_indicators = ['best', 'review', 'compare', 'top']
        if any(indicator in keyword_lower for indicator in commercial_indicators):
            return 'commercial'

        # Navigational
        if len(keyword.split()) == 1 or any(word in keyword_lower for word in ['.com', 'website']):
            return 'navigational'

        return 'informational'

class KeywordGenerator:
    """Generate keyword variations and long-tail keywords"""

    def __init__(self):
        self.modifiers = {
            'question': ['what', 'how', 'why', 'when', 'where', 'which'],
            'commercial': ['buy', 'price', 'best', 'review', 'cheap', 'discount'],
            'informational': ['guide', 'tutorial', 'learn', 'examples', 'tips'],
            'location': ['near me', 'online', '2024', 'latest']
        }

    def generate_long_tail_variations(self, seed_keyword, max_variations=20):
        """Generate long-tail keyword variations"""
        variations = []
        seed_lower = seed_keyword.lower()

        # Add question modifiers
        for modifier in self.modifiers['question']:
            variations.append(f"{modifier} {seed_lower}")
            variations.append(f"{seed_lower} {modifier}")

        # Add commercial modifiers
        for modifier in self.modifiers['commercial']:
            variations.append(f"{modifier} {seed_lower}")
            variations.append(f"{seed_lower} {modifier}")

        # Add informational modifiers
        for modifier in self.modifiers['informational']:
            variations.append(f"{seed_lower} {modifier}")

        # Add location/time modifiers
        for modifier in self.modifiers['location']:
            variations.append(f"{seed_lower} {modifier}")

        return list(set(variations))[:max_variations]

class KeywordClusterer:
    """Cluster keywords by semantic similarity"""

    def __init__(self):
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

    def cluster_keywords(self, keywords, num_clusters=8):
        """Cluster keywords using semantic similarity"""
        if len(keywords) < num_clusters:
            num_clusters = len(keywords) // 2

        # Generate embeddings
        embeddings = self.sentence_model.encode(keywords)

        # Perform K-means clustering
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        clusters = kmeans.fit_predict(embeddings)

        # Organize keywords by cluster
        clustered_keywords = {}
        for i, (keyword, cluster_id) in enumerate(zip(keywords, clusters)):
            cluster_id = int(cluster_id)
            if cluster_id not in clustered_keywords:
                clustered_keywords[cluster_id] = []
            clustered_keywords[cluster_id].append({
                'keyword': keyword,
                'embedding': embeddings[i].tolist()
            })

        return clustered_keywords

    def analyze_clusters(self, clustered_keywords):
        """Analyze and label keyword clusters"""
        cluster_analysis = {}

        for cluster_id, keywords in clustered_keywords.items():
            # Extract common themes
            all_keywords_text = ' '.join([k['keyword'] for k in keywords])

            # Simple TF-IDF for cluster labeling
            vectorizer = TfidfVectorizer(max_features=10, stop_words='english')
            try:
                tfidf_matrix = vectorizer.fit_transform([all_keywords_text])
                feature_names = vectorizer.get_feature_names_out()
                scores = tfidf_matrix.toarray()[0]

                top_terms = []
                for score, term in sorted(zip(scores, feature_names), reverse=True)[:3]:
                    top_terms.append(term)

                cluster_label = ' & '.join(top_terms)
            except:
                cluster_label = f"Cluster_{cluster_id}"

            cluster_analysis[int(cluster_id)] = {
                'label': cluster_label,
                'keywords': keywords,
                'size': len(keywords)
            }

        return cluster_analysis

class KeywordPriorityScorer:
    """Score keywords by priority for content strategy"""

    def __init__(self):
        self.weights = {
            'search_volume': 0.25,
            'difficulty': 0.30,
            'relevance': 0.20,
            'intent_value': 0.25
        }

    def calculate_intent_value(self, intent):
        """Assign value to different search intents"""
        intent_values = {
            'transactional': 0.9,
            'commercial': 0.8,
            'informational': 0.7,
            'navigational': 0.5
        }
        return intent_values.get(intent, 0.6)

    def calculate_priority_score(self, keyword_data):
        """Calculate overall priority score"""
        scores = {
            'search_volume': min(keyword_data['search_volume'] / 100000, 1.0),
            'difficulty': 1 - (keyword_data['difficulty'] / 100),
            'relevance': keyword_data.get('relevance_score', 0.5),
            'intent_value': self.calculate_intent_value(keyword_data['intent'])
        }

        # Calculate weighted score
        priority_score = sum(scores[factor] * self.weights[factor] for factor in scores)

        return {
            **keyword_data,
            'priority_score': priority_score,
            'score_breakdown': scores
        }

class SERPAnalyzer:
    """Analyze top SERP results to extract content patterns"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def extract_serp_features(self, keyword, max_results=10):
        """Extract features from top SERP results (simulated)"""
        simulated_results = []
        content_types = ['blog post', 'guide', 'product page', 'news article', 'video']

        for i in range(max_results):
            result = {
                'position': i + 1,
                'title': f"{keyword.title()} - Complete Guide {2024 - i}",
                'url': f"https://example.com/{keyword.replace(' ', '-')}-{i}",
                'content_type': random.choice(content_types),
                'word_count': random.randint(800, 3500),
                'has_video': random.choice([True, False]),
                'has_images': random.randint(3, 15),
                'readability_score': random.uniform(40, 80),
                'heading_structure': self._simulate_heading_structure()
            }
            simulated_results.append(result)

        return simulated_results

    def _simulate_heading_structure(self):
        """Simulate heading structure analysis"""
        headings = {
            'h1': ['Main Title'],
            'h2': ['Introduction', 'Key Features', 'Benefits', 'How to Use', 'Conclusion'],
            'h3': ['Getting Started', 'Advanced Tips', 'Common Mistakes'],
            'h4': ['Step by Step Guide', 'Pro Tips']
        }
        return headings

    def analyze_serp_patterns(self, serp_results):
        """Analyze common patterns across SERP results"""
        if not serp_results:
            return {}

        patterns = {
            'avg_word_count': np.mean([r.get('word_count', 0) for r in serp_results]),
            'common_content_types': dict(Counter([r.get('content_type', '') for r in serp_results])),
            'video_percentage': sum(1 for r in serp_results if r.get('has_video', False)) / len(serp_results),
            'avg_images': np.mean([r.get('has_images', 0) for r in serp_results]),
            'readability_avg': np.mean([r.get('readability_score', 0) for r in serp_results])
        }

        return patterns

class ContentBriefGenerator:
    """Generate comprehensive content briefs based on SERP analysis"""

    def __init__(self):
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate_headings_structure(self, keyword, serp_patterns):
        """Generate optimal heading structure"""
        base_headings = {
            'h1': [f"The Ultimate Guide to {keyword.title()}"],
            'h2': [
                f"What is {keyword.split()[0]}?",
                f"Benefits of {keyword}",
                f"How to Use {keyword.split()[0]}",
                "Key Features and Specifications",
                "Step-by-Step Implementation Guide",
                "Common Challenges and Solutions",
                "Best Practices and Tips",
                "Frequently Asked Questions"
            ]
        }

        base_headings['h3'] = [
            "Getting Started",
            "Advanced Techniques",
            "Performance Optimization",
            "Troubleshooting Common Issues"
        ]

        return base_headings

    def generate_meta_description(self, keyword, intent):
        """Generate optimized meta description"""
        templates = {
            'informational': f"Learn everything about {keyword} with our comprehensive guide. Discover best practices, tips, and step-by-step instructions.",
            'commercial': f"Compare the best {keyword} options available. Read our expert reviews and find the perfect solution for your needs.",
            'transactional': f"Buy the best {keyword} at competitive prices. Fast shipping and excellent customer service guaranteed."
        }

        return templates.get(intent, templates['informational'])

    def estimate_target_word_count(self, serp_patterns, keyword_difficulty):
        """Estimate optimal word count target"""
        base_count = serp_patterns.get('avg_word_count', 1500)

        if keyword_difficulty > 70:
            return int(base_count * 1.3)
        elif keyword_difficulty < 30:
            return int(base_count * 0.8)
        else:
            return int(base_count)

    def identify_internal_linking_opportunities(self, keyword, existing_content):
        """Identify internal linking opportunities"""
        opportunities = []

        related_terms = keyword.split()
        for term in related_terms:
            if len(term) > 3:
                opportunities.append({
                    'anchor_text': f"learn more about {term}",
                    'target_topic': term,
                    'relevance_score': random.uniform(0.6, 0.9)
                })

        return sorted(opportunities, key=lambda x: x['relevance_score'], reverse=True)[:5]

class ContentBriefExporter:
    """Export content briefs in various formats"""

    def generate_markdown_brief(self, brief_data):
        """Generate markdown format content brief"""
        markdown = f"""# Content Brief: {brief_data['target_keyword']}

## 📊 SEO Metrics
- **Priority Score**: {brief_data['priority_score']:.2f}
- **Search Volume**: {brief_data['search_volume']}
- **Difficulty**: {brief_data['difficulty']}/100
- **Search Intent**: {brief_data['intent']}

## 🎯 Target Word Count
**{brief_data['target_word_count']} words**

## 📝 Meta Description
{brief_data['meta_description']}

## 🏗️ Content Structure

### H1 Heading
{brief_data['headings']['h1'][0]}

### H2 Headings
"""

        for h2 in brief_data['headings']['h2']:
            markdown += f"- {h2}\n"

        markdown += "\n### H3 Headings\n"
        for h3 in brief_data['headings']['h3']:
            markdown += f"- {h3}\n"

        markdown += f"""
## 🔗 Internal Linking Opportunities
"""

        for link in brief_data['internal_links']:
            markdown += f"- **{link['anchor_text']}** -> {link['target_topic']} (Relevance: {link['relevance_score']:.2f})\n"

        markdown += f"""
## 📈 SERP Analysis Insights
- **Average Competitor Word Count**: {brief_data['serp_analysis']['avg_word_count']:.0f}
- **Recommended Content Depth**: {brief_data['content_depth']}
- **Readability Target**: {brief_data['serp_analysis']['readability_avg']:.1f}

## 💡 Key Recommendations
1. Focus on {brief_data['intent']} intent throughout the content
2. Include visual elements: target {brief_data['serp_analysis']['avg_images']:.1f} images
3. Optimize for readability score ~{brief_data['serp_analysis']['readability_avg']:.1f}
4. Cover all key aspects identified in competitor analysis

---
*Generated on {brief_data['generated_date']}*
"""
        return markdown

class SEOStrategyAgent:
    """
    Main SEO Strategy Agent combining keyword research and content brief generation
    """

    def __init__(self):
        self.keyword_research = KeywordResearchTool()
        self.keyword_generator = KeywordGenerator()
        self.keyword_clusterer = KeywordClusterer()
        self.priority_scorer = KeywordPriorityScorer()
        self.serp_analyzer = SERPAnalyzer()
        self.brief_generator = ContentBriefGenerator()
        self.brief_exporter = ContentBriefExporter()

    def research_keywords(self, seed_topics: List[str], max_keywords_per_topic: int = 20):
        """Perform comprehensive keyword research"""
        all_keywords = []

        for seed_topic in seed_topics:
            # Generate keyword variations
            variations = self.keyword_generator.generate_long_tail_variations(
                seed_topic, 
                max_variations=max_keywords_per_topic
            )

            for keyword in variations:
                # Research each keyword
                search_volume = self.keyword_research.estimate_search_volume(keyword)
                difficulty = self.keyword_research.estimate_keyword_difficulty(keyword)
                intent = self.keyword_research.classify_search_intent(keyword)

                keyword_data = {
                    'keyword': keyword,
                    'seed_topic': seed_topic,
                    'search_volume': search_volume,
                    'difficulty': difficulty,
                    'intent': intent,
                    'word_count': len(keyword.split()),
                    'relevance_score': random.uniform(0.6, 0.95)
                }

                all_keywords.append(keyword_data)

        # Calculate priority scores
        prioritized_keywords = []
        for keyword_data in all_keywords:
            scored_keyword = self.priority_scorer.calculate_priority_score(keyword_data)
            prioritized_keywords.append(scored_keyword)

        # Sort by priority
        prioritized_keywords.sort(key=lambda x: x['priority_score'], reverse=True)

        # Cluster keywords
        keyword_texts = [k['keyword'] for k in prioritized_keywords[:100]]
        clustered_keywords = self.keyword_clusterer.cluster_keywords(keyword_texts)
        cluster_analysis = self.keyword_clusterer.analyze_clusters(clustered_keywords)

        return {
            'keywords': prioritized_keywords[:50],
            'cluster_analysis': cluster_analysis,
            'total_keywords_generated': len(all_keywords),
            'search_intent_breakdown': dict(Counter([k['intent'] for k in prioritized_keywords])),
            'research_timestamp': datetime.now().isoformat()
        }

    def generate_content_briefs(self, top_keywords: List[Dict], max_briefs: int = 5):
        """Generate content briefs for top keywords"""
        content_briefs = []

        for i, keyword_data in enumerate(top_keywords[:max_briefs]):
            # Analyze SERP for this keyword
            serp_results = self.serp_analyzer.extract_serp_features(keyword_data['keyword'])
            serp_patterns = self.serp_analyzer.analyze_serp_patterns(serp_results)

            # Generate content brief components
            headings = self.brief_generator.generate_headings_structure(
                keyword_data['keyword'],
                serp_patterns
            )

            meta_description = self.brief_generator.generate_meta_description(
                keyword_data['keyword'],
                keyword_data['intent']
            )

            target_word_count = self.brief_generator.estimate_target_word_count(
                serp_patterns,
                keyword_data['difficulty']
            )

            internal_links = self.brief_generator.identify_internal_linking_opportunities(
                keyword_data['keyword'],
                []
            )

            # Compile complete brief
            content_brief = {
                'target_keyword': keyword_data['keyword'],
                'priority_score': keyword_data['priority_score'],
                'search_volume': keyword_data['search_volume'],
                'difficulty': keyword_data['difficulty'],
                'intent': keyword_data['intent'],
                'target_word_count': target_word_count,
                'meta_description': meta_description,
                'headings': headings,
                'internal_links': internal_links,
                'serp_analysis': serp_patterns,
                'content_depth': 'Comprehensive' if target_word_count > 2000 else 'Standard',
                'generated_date': datetime.now().isoformat(),
                'brief_id': f"brief_{i+1:03d}"
            }

            # Generate markdown version
            markdown_brief = self.brief_exporter.generate_markdown_brief(content_brief)
            content_brief['markdown_version'] = markdown_brief

            content_briefs.append(content_brief)

        return {
            'content_briefs': content_briefs,
            'total_briefs_generated': len(content_briefs),
            'generation_timestamp': datetime.now().isoformat()
        }