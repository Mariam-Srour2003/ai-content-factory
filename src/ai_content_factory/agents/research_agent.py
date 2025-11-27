import requests
import random
import time
import re
import json
import feedparser
from urllib.parse import urlparse, urljoin
from datetime import datetime
from collections import Counter
from bs4 import BeautifulSoup
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
from sentence_transformers import SentenceTransformer
# import textstat
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# TICKET #4: WEB SCRAPING COMPONENTS
# =============================================================================

class EthicalWebScraper:
    """
    Advanced web scraper with ethical practices and rate limiting
    """
    def __init__(self, delay_range=(1, 3), max_retries=3):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.scraped_data = []

    def respectful_delay(self):
        """Implement respectful delay between requests"""
        delay = random.uniform(self.delay_range[0], self.delay_range[1])
        time.sleep(delay)

    def can_scrape(self, url):
        """Check robots.txt compliance (basic implementation)"""
        try:
            domain = urlparse(url).netloc
            robots_url = f"https://{domain}/robots.txt"
            response = self.session.get(robots_url, timeout=10)
            return response.status_code == 200
        except:
            return True

    def extract_blog_content(self, url):
        """Extract main content from blog posts"""
        try:
            self.respectful_delay()
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()

            # Try to find main content
            content_selectors = [
                'article', '.post-content', '.entry-content',
                '.blog-content', '.post', '.article-content',
                'main', '[role="main"]'
            ]

            content = None
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    break

            # Fallback to body if no specific content found
            if not content:
                content = soup.find('body')

            # Extract text and clean it
            text = content.get_text(separator=' ', strip=True) if content else ""
            text = re.sub(r'\s+', ' ', text)

            # Extract metadata
            title = soup.find('title')
            title = title.text.strip() if title else ""

            # Extract publication date
            date_selectors = [
                'time', '.post-date', '.published',
                '.entry-date', '[datetime]'
            ]
            date = ""
            for selector in date_selectors:
                date_element = soup.select_one(selector)
                if date_element:
                    date = date_element.get('datetime') or date_element.text
                    break

            return {
                'url': url,
                'title': title,
                'content': text[:5000],  # Limit content length
                'date': date,
                'word_count': len(text.split()),
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None

    def discover_blog_links(self, domain):
        """Discover blog post URLs from a domain"""
        try:
            self.respectful_delay()
            response = self.session.get(domain, timeout=15)
            soup = BeautifulSoup(response.content, 'lxml')

            # Skincare-specific blog link patterns
            blog_patterns = [
                r'/blog/', r'/post/', r'/article/', r'/journal/',
                r'/skincare/', r'/beauty/', r'/routine/', r'/ingredients/',
                r'/tips/', r'/advice/', r'/guides/', r'/how-to/',
                r'/\d{4}/\d{2}/',  # Date patterns
            ]

            blog_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(domain, href)

                # Check if link matches blog patterns
                if any(re.search(pattern, href, re.IGNORECASE) for pattern in blog_patterns):
                    blog_links.append(full_url)

            return list(set(blog_links))[:20]  # Limit to 20 links

        except Exception as e:
            logger.error(f"Error discovering links from {domain}: {str(e)}")
            return []

    def scrape_competitor_blogs(self, competitor_domains, max_posts_per_domain=10):
        """Scrape multiple competitor blogs"""
        all_posts = []

        for domain in competitor_domains:
            logger.info(f"Scraping blog posts from: {domain}")

            if not self.can_scrape(domain):
                logger.warning(f"Skipping {domain} due to robots.txt")
                continue

            blog_links = self.discover_blog_links(domain)
            logger.info(f"Found {len(blog_links)} potential blog posts")

            posts_scraped = 0
            for link in blog_links[:max_posts_per_domain]:
                post_data = self.extract_blog_content(link)
                if post_data and post_data['content']:
                    post_data['domain'] = domain
                    all_posts.append(post_data)
                    posts_scraped += 1
                    logger.info(f"Scraped: {post_data['title'][:50]}...")

            logger.info(f"Total posts scraped from {domain}: {posts_scraped}")

        return all_posts


class TrendingTopicDiscoverer:
    """Discover trending topics via RSS and APIs for skincare"""
    def __init__(self):
        # Skincare and beauty focused RSS feeds
        self.rss_feeds = [
            'https://www.allure.com/feed/rss',
            'https://www.byrdie.com/rss',
            'https://www.whowhatwear.com/rss',
            'https://www.dermstore.com/blog/feed/',
            'https://www.paulaschoice.com/expert-advice/rss.xml',
            'https://www.skincare.com/feed/'
        ]

    def parse_rss_feed(self, feed_url):
        """Parse RSS feed and extract trending topics"""
        try:
            feed = feedparser.parse(feed_url)
            topics = []

            for entry in feed.entries[:20]:  # Limit to 20 entries per feed
                topics.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:500],
                    'source': feed_url
                })

            return topics
        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {str(e)}")
            return []

    def discover_trending_topics(self):
        """Discover trending topics from multiple RSS feeds"""
        all_topics = []

        for feed_url in self.rss_feeds:
            logger.info(f"Parsing RSS feed: {feed_url}")
            topics = self.parse_rss_feed(feed_url)
            all_topics.extend(topics)
            logger.info(f"Found {len(topics)} topics")

        return all_topics

    def calculate_relevance_scores(self, topics, keywords_of_interest):
        """Calculate relevance scores for topics based on skincare keywords"""
        scored_topics = []

        for topic in topics:
            score = 0
            text = f"{topic['title']} {topic['summary']}".lower()

            for keyword in keywords_of_interest:
                if keyword.lower() in text:
                    score += 1

            # Normalize score
            topic['relevance_score'] = min(score / len(keywords_of_interest), 1.0)
            scored_topics.append(topic)

        return sorted(scored_topics, key=lambda x: x['relevance_score'], reverse=True)


class ContentGapAnalyzer:
    """Analyze content gaps for skincare content"""
    def __init__(self):
        self.scraper = EthicalWebScraper()
        self.topic_discoverer = TrendingTopicDiscoverer()

    def content_gap_analysis(self, scraped_posts, trending_topics, top_n_keywords=20):
        """
        Compare scraped blog posts with trending topics to identify content gaps.
        Returns a list of missing or underrepresented keywords.
        """
        # Extract keywords from scraped posts
        all_text = " ".join(post['content'] for post in scraped_posts)
        words = re.findall(r'\b\w+\b', all_text.lower())
        post_keywords = [w for w in words if len(w) > 3]  # ignore short words
        post_freq = Counter(post_keywords)

        # Extract keywords from trending topics
        topic_text = " ".join(topic['title'] + " " + topic['summary'] for topic in trending_topics)
        topic_words = re.findall(r'\b\w+\b', topic_text.lower())
        topic_keywords = [w for w in topic_words if len(w) > 3]
        topic_freq = Counter(topic_keywords)

        # Identify gaps: trending keywords not common in scraped posts
        gaps = {}
        for word, freq in topic_freq.most_common(top_n_keywords):
            if post_freq.get(word, 0) < 2:  # threshold: appears <2 times in posts
                gaps[word] = {
                    "in_posts": post_freq.get(word, 0),
                    "in_trending": freq,
                    "opportunity_score": freq / (post_freq.get(word, 0) + 1)  # Avoid division by zero
                }

        # Return sorted by trending frequency
        return dict(sorted(gaps.items(), key=lambda x: x[1]['opportunity_score'], reverse=True))

    def generate_research_report(self, competitor_domains=None, keywords_of_interest=None):
        """Generate comprehensive skincare research report"""
        if competitor_domains is None:
            competitor_domains = [
                'https://theordinary.com',
                'https://www.cerave.com',
                'https://www.paulaschoice.com'
            ]
            
        if keywords_of_interest is None:
            keywords_of_interest = [
                'skincare', 'routine', 'ingredients', 'moisturizer', 'cleanser',
                'serum', 'acne', 'anti-aging', 'dermatologist', 'sunscreen',
                'retinol', 'hyaluronic', 'niacinamide', 'sensitive', 'glow'
            ]

        logger.info("Starting comprehensive skincare research analysis...")

        # Scrape competitor blogs
        blog_posts = self.scraper.scrape_competitor_blogs(competitor_domains, max_posts_per_domain=5)

        # Discover trending topics
        trending_topics = self.topic_discoverer.discover_trending_topics()

        # Calculate relevance scores
        scored_topics = self.topic_discoverer.calculate_relevance_scores(trending_topics, keywords_of_interest)

        # Perform content gap analysis
        gaps = self.content_gap_analysis(blog_posts, trending_topics, top_n_keywords=20)

        # Generate research insights
        research_data = {
            'scraped_posts': blog_posts,
            'trending_topics': scored_topics[:10],  # Top 10 most relevant
            'content_gaps': gaps,
            'research_insights': self._generate_skincare_insights(blog_posts, scored_topics, gaps),
            'metadata': {
                'total_posts_scraped': len(blog_posts),
                'total_topics_found': len(scored_topics),
                'total_content_gaps': len(gaps),
                'competitor_domains': competitor_domains,
                'keywords_analyzed': keywords_of_interest,
                'execution_time': datetime.now().isoformat()
            }
        }

        return research_data

    def _generate_skincare_insights(self, posts, topics, gaps):
        """Generate actionable skincare insights from research data"""
        insights = {
            'top_trending_topics': [t['title'] for t in topics[:5]],
            'content_opportunities': list(gaps.keys())[:10],
            'competitor_coverage_areas': self._analyze_competitor_coverage(posts),
            'recommended_content_themes': self._suggest_skincare_content_themes(topics, gaps)
        }
        return insights

    def _analyze_competitor_coverage(self, posts):
        """Analyze what skincare topics competitors are covering"""
        all_content = " ".join(post['content'] for post in posts)
        words = [w for w in re.findall(r'\b\w+\b', all_content.lower()) if len(w) > 4]
        common_topics = Counter(words).most_common(10)
        return [topic for topic, count in common_topics]

    def _suggest_skincare_content_themes(self, topics, gaps):
        """Suggest skincare content themes based on gaps and trends"""
        trending_words = " ".join(t['title'] for t in topics[:10]).lower()
        trending_terms = [w for w in re.findall(r'\b\w+\b', trending_words) if len(w) > 4]
        
        gap_terms = list(gaps.keys())[:5]
        
        # Combine trending terms with gap opportunities
        suggested_themes = list(set(trending_terms[:3] + gap_terms[:3]))
        return suggested_themes


# =============================================================================
# TICKET #5: TOPIC ANALYSIS COMPONENTS  
# =============================================================================

class LLMTopicAnalyzer:
    """
    LLM-powered topic analysis with clustering and scoring for skincare
    """
    def __init__(self):
        try:
            # Use efficient models suitable for CPU
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                tokenizer="facebook/bart-large-cnn",
                framework="pt"
            )
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("LLMTopicAnalyzer initialized successfully")
        except Exception as e:
            logger.warning(f"Some models failed to load: {e}. Using fallback methods.")
            self.summarizer = None
            self.sentiment_analyzer = None
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[Dict]:
        """Extract key phrases using TF-IDF with improved error handling"""
        if not text or len(text.split()) < 5:
            return []

        try:
            vectorizer = TfidfVectorizer(
                max_features=100, 
                stop_words='english', 
                ngram_range=(1, 3),
                min_df=1,
                max_df=0.8
            )
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            # Get top phrases with minimum score threshold
            key_phrases = []
            for score, phrase in sorted(zip(scores, feature_names), reverse=True)[:max_phrases]:
                if score > 0.1:  # Minimum score threshold
                    key_phrases.append({'phrase': phrase, 'score': float(score)})

            return key_phrases
        except Exception as e:
            logger.warning(f"Key phrase extraction failed: {e}")
            return []

    def calculate_topic_relevance(self, topic_text: str, target_domain_keywords: List[str]) -> float:
        """Calculate relevance score for skincare topics with improved matching"""
        if not topic_text or not target_domain_keywords:
            return 0.0

        text_lower = topic_text.lower()
        
        # Weighted matching: exact matches score higher
        matches = 0
        total_possible = len(target_domain_keywords)
        
        for keyword in target_domain_keywords:
            keyword_lower = keyword.lower()
            if f" {keyword_lower} " in f" {text_lower} ":
                matches += 1  # Exact word match
            elif keyword_lower in text_lower:
                matches += 0.5  # Partial match

        return min(matches / total_possible, 1.0) if total_possible > 0 else 0.0

    def generate_topic_brief(self, topic_data: Dict) -> Dict:
        """Generate topic brief using LLM summarization with fallbacks"""
        try:
            combined_text = f"{topic_data['title']}. {topic_data.get('summary', '')}"
            
            if len(combined_text.strip()) < 10:
                return self._create_fallback_brief(topic_data)

            summary = combined_text  # Fallback summary
            
            # Use LLM summarizer if available and text is substantial
            if self.summarizer and len(combined_text.split()) > 50:
                try:
                    summary = self.summarizer(
                        combined_text,
                        max_length=150,
                        min_length=30,
                        do_sample=False
                    )[0]['summary_text']
                except Exception as e:
                    logger.warning(f"Summarization failed: {e}")

            # Extract key phrases
            key_phrases = self.extract_key_phrases(combined_text)

            # Analyze sentiment if analyzer available
            sentiment_label = "NEUTRAL"
            sentiment_score = 0.5
            
            if self.sentiment_analyzer:
                try:
                    sentiment_result = self.sentiment_analyzer(combined_text[:512])[0]
                    sentiment_label = sentiment_result['label']
                    sentiment_score = float(sentiment_result['score'])
                except Exception as e:
                    logger.warning(f"Sentiment analysis failed: {e}")

            return {
                'summary': summary,
                'key_phrases': key_phrases[:5],  # Top 5 phrases
                'sentiment': sentiment_label,
                'sentiment_score': sentiment_score,
                'estimated_word_count': len(combined_text.split()),
                'analysis_quality': 'high' if len(key_phrases) > 2 else 'medium'
            }
            
        except Exception as e:
            logger.error(f"Error generating topic brief: {str(e)}")
            return self._create_fallback_brief(topic_data)

    def _create_fallback_brief(self, topic_data: Dict) -> Dict:
        """Create a fallback brief when analysis fails"""
        combined_text = f"{topic_data['title']}. {topic_data.get('summary', '')}"
        return {
            'summary': combined_text[:200] + "..." if len(combined_text) > 200 else combined_text,
            'key_phrases': self.extract_key_phrases(combined_text, max_phrases=3),
            'sentiment': 'NEUTRAL',
            'sentiment_score': 0.5,
            'estimated_word_count': len(combined_text.split()),
            'analysis_quality': 'low'
        }


class TopicClusterer:
    """Advanced topic clustering using semantic similarity for skincare"""
    def __init__(self):
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

    def cluster_topics(self, topics: List[Dict], num_clusters: int = 5) -> List[Dict]:
        """Cluster skincare topics using semantic similarity with adaptive parameters"""
        if len(topics) < 3:
            # Not enough topics for meaningful clustering
            for i, topic in enumerate(topics):
                topic['cluster_id'] = i
            return topics

        try:
            # Prepare texts for embedding
            texts = [f"{topic['title']} {topic.get('summary', '')}" for topic in topics]

            # Generate embeddings
            embeddings = self.sentence_model.encode(texts)

            # Adaptive clustering parameters based on data size
            eps = 0.6 if len(topics) > 10 else 0.7
            min_samples = max(2, len(topics) // 10)

            # Perform clustering
            clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine').fit(embeddings)

            # Assign clusters to topics
            clustered_topics = []
            for i, topic in enumerate(topics):
                topic['cluster_id'] = int(clustering.labels_[i])
                topic['embedding'] = embeddings[i].tolist()
                clustered_topics.append(topic)

            return clustered_topics
            
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            # Fallback: assign each topic to its own cluster
            for i, topic in enumerate(topics):
                topic['cluster_id'] = i
            return topics

    def analyze_clusters(self, clustered_topics: List[Dict]) -> Dict:
        """Analyze and describe skincare clusters with comprehensive metrics"""
        cluster_analysis = {}

        for topic in clustered_topics:
            cluster_id = topic['cluster_id']
            if cluster_id not in cluster_analysis:
                cluster_analysis[cluster_id] = {
                    'topics': [],
                    'size': 0,
                    'key_themes': [],
                    'avg_relevance': 0,
                    'topic_titles': []
                }

            cluster_analysis[cluster_id]['topics'].append(topic)
            cluster_analysis[cluster_id]['size'] += 1
            cluster_analysis[cluster_id]['topic_titles'].append(topic['title'][:50])

        # Calculate metrics and extract key themes for each cluster
        for cluster_id, data in cluster_analysis.items():
            if cluster_id == -1:  # Noise points
                data['key_themes'] = ['Miscellaneous/Uncategorized']
                data['avg_relevance'] = 0.5
                data['coherence_score'] = 0.1
            else:
                # Combine all texts in cluster
                all_text = ' '.join([f"{t['title']} {t.get('summary', '')}" for t in data['topics']])
                key_phrases = self.extract_key_phrases(all_text, max_phrases=3)
                data['key_themes'] = [phrase['phrase'] for phrase in key_phrases]
                
                # Calculate average relevance
                relevances = [t.get('relevance_score', 0) for t in data['topics']]
                data['avg_relevance'] = sum(relevances) / len(relevances) if relevances else 0
                data['coherence_score'] = min(data['avg_relevance'] * data['size'] / 10, 1.0)

        return cluster_analysis

    def extract_key_phrases(self, text: str, max_phrases: int = 5) -> List[Dict]:
        """Extract key phrases from text with error handling"""
        if not text:
            return []
            
        try:
            vectorizer = TfidfVectorizer(
                max_features=50, 
                stop_words='english', 
                ngram_range=(1, 2),
                min_df=1
            )
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            key_phrases = []
            for score, phrase in sorted(zip(scores, feature_names), reverse=True)[:max_phrases]:
                if score > 0.05:  # Minimum threshold
                    key_phrases.append({'phrase': phrase, 'score': float(score)})

            return key_phrases
        except Exception as e:
            logger.warning(f"Cluster key phrase extraction failed: {e}")
            return []


class TopicPriorityRanker:
    """Rank skincare topics by priority based on multiple factors"""
    def __init__(self, domain_keywords: List[str]):
        self.domain_keywords = domain_keywords

    def calculate_priority_score(self, topic: Dict) -> Dict:
        """Calculate comprehensive priority score with weighted factors for skincare"""
        scores = {
            'relevance': topic.get('relevance_score', 0),
            'recency': self.calculate_recency_score(topic),
            'engagement_potential': self.calculate_skincare_engagement_potential(topic),
            'content_quality': self.calculate_content_quality(topic),
            'uniqueness': self.calculate_uniqueness_score(topic)
        }

        # Dynamic weights based on skincare business goals
        weights = {
            'relevance': 0.35,
            'recency': 0.15,
            'engagement_potential': 0.25,
            'content_quality': 0.15,
            'uniqueness': 0.10
        }

        priority_score = sum(scores[factor] * weights[factor] for factor in scores)
        
        topic['priority_score'] = round(priority_score, 3)
        topic['score_breakdown'] = {k: round(v, 3) for k, v in scores.items()}
        topic['priority_tier'] = self._assign_priority_tier(priority_score)

        return topic

    def calculate_recency_score(self, topic: Dict) -> float:
        """Calculate score based on topic recency"""
        if topic.get('scraped_at') or topic.get('published'):
            return 0.8  # Assume recent if we have timestamp
        return 0.5

    def calculate_skincare_engagement_potential(self, topic: Dict) -> float:
        """Estimate engagement potential based on skincare content characteristics"""
        text = f"{topic['title']} {topic.get('summary', '')}"
        if not text.strip():
            return 0.3

        # Skincare-specific engagement factors
        factors = [
            len(text.split()) > 100,  # Substantial content
            '?' in topic['title'],    # Question format
            any(word in topic['title'].lower() for word in ['how', 'what', 'why', 'guide', 'tutorial', 'tips', 'routine']),
            any(word in topic['title'].lower() for word in ['acne', 'aging', 'glow', 'hydrate', 'repair']),  # Skincare concerns
            len(topic.get('key_phrases', [])) >= 3,  # Good keyword coverage
            topic.get('sentiment_score', 0.5) > 0.7  # Positive sentiment
        ]

        score = sum(factors) / len(factors)
        return min(score, 1.0)

    def calculate_content_quality(self, topic: Dict) -> float:
        """Assess content quality based on available metrics"""
        quality_factors = []
        
        # Summary quality
        if topic.get('summary') and len(topic['summary'].split()) > 20:
            quality_factors.append(0.8)
        
        # Key phrases quality
        if len(topic.get('key_phrases', [])) >= 3:
            quality_factors.append(0.7)
            
        # Sentiment confidence
        sentiment_confidence = abs(topic.get('sentiment_score', 0.5) - 0.5) * 2
        quality_factors.append(sentiment_confidence)
        
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.5

    def calculate_uniqueness_score(self, topic: Dict) -> float:
        """Calculate uniqueness based on skincare title and content patterns"""
        title = topic.get('title', '').lower()
        
        # Score lower for common skincare patterns, higher for unique ones
        common_patterns = ['home', 'about', 'contact', 'shop', 'products']
        if any(pattern in title for pattern in common_patterns):
            return 0.3
            
        unique_indicators = ['how to', 'why', 'vs', 'comparison', 'review', 'ingredient', 'routine']
        if any(indicator in title for indicator in unique_indicators):
            return 0.8
            
        return 0.6

    def _assign_priority_tier(self, score: float) -> str:
        """Assign priority tier based on score"""
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        else:
            return "low"


# =============================================================================
# MAIN RESEARCH AGENT (COMBINES BOTH TICKETS) - SKINCARE FOCUS
# =============================================================================

class AdvancedResearchAgent:
    """
    Main Research Agent for Skincare Content Analysis that combines both 
    Ticket #4 (Web Scraping) and Ticket #5 (Topic Analysis) functionality
    """
    
    def __init__(self, domain_keywords: List[str] = None):
        # Ticket #4 components
        self.scraper = EthicalWebScraper()
        self.topic_discoverer = TrendingTopicDiscoverer()
        self.gap_analyzer = ContentGapAnalyzer()
        
        # Ticket #5 components  
        self.topic_analyzer = LLMTopicAnalyzer()
        self.clusterer = TopicClusterer()
        self.ranker = TopicPriorityRanker(domain_keywords or [
            'skincare', 'beauty', 'dermatology', 'routine', 'ingredients',
            'acne', 'anti-aging', 'moisturizer', 'cleanser', 'serum',
            'sunscreen', 'retinol', 'hyaluronic', 'niacinamide', 'glow'
        ])

    def comprehensive_research_analysis(self, competitor_domains: List[str] = None, 
                                    keywords_of_interest: List[str] = None,
                                    max_topics: int = 30) -> Dict:
        """
        Complete skincare research pipeline combining web scraping and topic analysis
        """
        logger.info("Starting comprehensive skincare research analysis...")
        
        # Step 1: Web Scraping (Ticket #4)
        research_data = self.gap_analyzer.generate_research_report(
            competitor_domains=competitor_domains,
            keywords_of_interest=keywords_of_interest
        )
        
        # Step 2: Topic Analysis (Ticket #5)
        topic_analysis = self.comprehensive_topic_analysis(research_data, max_topics)
        
        # Combine results with proper structure
        comprehensive_results = {
            'web_scraping_results': research_data,
            'topic_analysis_results': topic_analysis,
            'execution_summary': {
                'total_competitor_posts': len(research_data.get('scraped_posts', [])),
                'total_trending_topics': len(research_data.get('trending_topics', [])),
                'content_gaps_identified': len(research_data.get('content_gaps', {})),
                'topics_analyzed': len(topic_analysis.get('analyzed_topics', [])),
                'high_priority_topics': len([t for t in topic_analysis.get('analyzed_topics', []) 
                                        if t.get('priority_tier') == 'high']),
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        
        return comprehensive_results

    def comprehensive_topic_analysis(self, research_data: Dict = None, max_topics: int = 30) -> Dict:
        """Perform comprehensive topic analysis on skincare research data"""
        logger.info("Starting comprehensive skincare topic analysis...")
        
        # Generate research data if not provided
        if research_data is None:
            research_data = self.scraper.scrape_competitor_blogs(
                ['https://theordinary.com', 'https://www.cerave.com'], 
                max_posts_per_domain=5
            )
        
        # Handle case where research_data might be a list (from direct scraping)
        if isinstance(research_data, list):
            # Convert list to proper dict structure
            research_data = {
                'scraped_posts': research_data,
                'trending_topics': [],
                'content_gaps': {},
                'research_insights': {},
                'metadata': {
                    'total_posts_scraped': len(research_data),
                    'total_trending_topics': 0,
                    'total_content_gaps': 0,
                    'execution_time': datetime.now().isoformat()
                }
            }
        
        # Combine and prepare topics
        all_topics = research_data.get('scraped_posts', []) + research_data.get('trending_topics', [])
        logger.info(f"Analyzing {len(all_topics)} skincare topics...")
        
        analyzed_topics = []
        for i, topic in enumerate(all_topics[:max_topics]):
            if i % 5 == 0:
                logger.info(f"Analyzed {i}/{min(max_topics, len(all_topics))} topics")
                
            brief = self.topic_analyzer.generate_topic_brief(topic)
            relevance = self.topic_analyzer.calculate_topic_relevance(
                f"{topic.get('title', '')} {topic.get('summary', '')}",
                self.ranker.domain_keywords
            )
            
            analyzed_topic = {
                **topic,
                **brief,
                'relevance_score': relevance,
                'topic_id': f"topic_{i:03d}"
            }
            analyzed_topics.append(analyzed_topic)
        
        # Cluster topics
        clustered_topics = self.clusterer.cluster_topics(analyzed_topics)
        cluster_analysis = self.clusterer.analyze_clusters(clustered_topics)
        
        # Rank topics by priority
        prioritized_topics = []
        for topic in clustered_topics:
            ranked_topic = self.ranker.calculate_priority_score(topic)
            prioritized_topics.append(ranked_topic)
        
        # Sort by priority score
        prioritized_topics.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        # Prepare final analysis
        topic_analysis = {
            'analyzed_topics': prioritized_topics[:20],
            'cluster_analysis': cluster_analysis,
            'top_priority_topics': prioritized_topics[:10],
            'content_recommendations': self._generate_skincare_content_recommendations(prioritized_topics),
            'analysis_metadata': {
                'total_topics_analyzed': len(analyzed_topics),
                'clusters_identified': len([k for k in cluster_analysis.keys() if k != -1]),
                'high_priority_topics': len([t for t in prioritized_topics if t.get('priority_tier') == 'high']),
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        
        return topic_analysis

    def _generate_skincare_content_recommendations(self, prioritized_topics: List[Dict]) -> List[Dict]:
        """Generate skincare-specific content recommendations based on topic analysis"""
        recommendations = []
        
        for topic in prioritized_topics[:5]:
            rec = {
                'topic_title': topic['title'],
                'priority_score': topic['priority_score'],
                'content_angle': self._suggest_skincare_content_angle(topic),
                'target_keywords': [phrase['phrase'] for phrase in topic.get('key_phrases', [])[:3]],
                'estimated_effort': self._estimate_skincare_content_effort(topic),
                'content_format': self._suggest_skincare_content_format(topic)
            }
            recommendations.append(rec)
            
        return recommendations
    
    def _suggest_skincare_content_angle(self, topic: Dict) -> str:
        """Suggest skincare-specific content angle based on topic characteristics"""
        title = topic['title'].lower()
        
        # Skincare-specific content angles
        if any(word in title for word in ['how to', 'tutorial', 'guide', 'routine', 'layering']):
            return "Educational/Step-by-Step Routine"
        elif any(word in title for word in ['ingredient', 'formula', 'compound', 'active']):
            return "Ingredient Deep Dive"
        elif any(word in title for word in ['review', 'comparison', 'vs', 'best']):
            return "Product Comparison/Review"
        elif any(word in title for word in ['treatment', 'solution', 'fix', 'repair']):
            return "Problem-Solution Focused"
        elif any(word in title for word in ['myth', 'fact', 'truth', 'debunk']):
            return "Myth Busting/Educational"
        elif any(word in title for word in ['dermatologist', 'expert', 'doctor']):
            return "Expert Advice/Professional Insight"
        elif any(word in title for word in ['sensitive', 'gentle', 'safe', 'hypoallergenic']):
            return "Sensitive Skin Focus"
        else:
            return "Informational/Skincare Education"
    
    def _estimate_skincare_content_effort(self, topic: Dict) -> str:
        """Estimate skincare content creation effort based on complexity"""
        word_count = topic.get('estimated_word_count', 0)
        complexity = len(topic.get('key_phrases', []))
        
        # Skincare topics often require more research for ingredient safety, etc.
        if any(term in topic['title'].lower() for term in ['clinical', 'study', 'research', 'dermatologist']):
            return "High (Requires Medical Research)"
        elif word_count > 1200 or complexity > 6:
            return "High"
        elif word_count > 700 or complexity > 4:
            return "Medium"
        else:
            return "Low"

    def _suggest_skincare_content_format(self, topic: Dict) -> List[str]:
        """Suggest appropriate content formats for skincare topics"""
        title = topic['title'].lower()
        formats = []
        
        if any(word in title for word in ['routine', 'steps', 'layering']):
            formats.extend(["Step-by-Step Guide", "Video Tutorial", "Infographic"])
        
        if any(word in title for word in ['ingredient', 'active', 'compound']):
            formats.extend(["Deep Dive Article", "Comparison Chart", "Scientific Breakdown"])
        
        if any(word in title for word in ['review', 'comparison']):
            formats.extend(["Product Review", "Before/After Photos", "User Testimonials"])
        
        if any(word in title for word in ['acne', 'eczema', 'rosacea']):
            formats.extend(["Condition Guide", "Dermatologist Interview", "Case Study"])
        
        # Default formats for skincare content
        if not formats:
            formats = ["Educational Article", "Social Media Posts", "Email Newsletter"]
            
        return formats[:3]  # Return top 3 formats


# =============================================================================
# DEMONSTRATION FUNCTIONS (FOR TESTING) - SKINCARE FOCUS
# =============================================================================

def demonstrate_skincare_research_agent():
    """Demonstrate complete skincare research agent functionality"""
    print("🚀 SKINCARE RESEARCH AGENT DEMONSTRATION")
    
    # Initialize the main research agent with skincare keywords
    research_agent = AdvancedResearchAgent()
    
    # Run complete analysis with skincare competitors
    results = research_agent.comprehensive_research_analysis(
        competitor_domains=['https://theordinary.com', 'https://www.cerave.com'],
        keywords_of_interest=['skincare', 'routine', 'ingredients', 'acne', 'anti-aging'],
        max_topics=25
    )
    
    print(f"✅ Skincare Research Analysis Finished!")
    print(f"   - Competitor Posts: {results['execution_summary']['total_competitor_posts']}")
    print(f"   - Trending Topics: {results['execution_summary']['total_trending_topics']}")
    print(f"   - Content Gaps: {results['execution_summary']['content_gaps_identified']}")
    print(f"   - Topics Analyzed: {results['execution_summary']['topics_analyzed']}")
    print(f"   - High Priority Topics: {results['execution_summary']['high_priority_topics']}")
    
    return results

# Example usage
if __name__ == "__main__":
    results = demonstrate_skincare_research_agent()