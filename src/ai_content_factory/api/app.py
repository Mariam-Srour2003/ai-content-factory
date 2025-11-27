"""
FastAPI application for AI Content Factory.
Provides REST API endpoints for content generation, analytics, and management.
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ..agents.content_writer_agent import ContentWriterAgent
from ..config.config_loader import load_config
from ..core.metrics import ContentMetricsEvaluator
from ..core.metrics_logger import MetricsLogger
from ..utils.logger import get_logger

from src.ai_content_factory.agents.research_agent import AdvancedResearchAgent


logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Content Factory",
    description="AI-powered content generation platform",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
config = load_config()
content_agent = None
metrics_evaluator = None
metrics_logger = None

# Content storage
CONTENT_STORAGE_FILE = Path("outputs/content_library.json")
CONTENT_STORAGE_FILE.parent.mkdir(exist_ok=True)

# Generation status tracking
generation_status: Dict[str, Dict] = {}


# ==================== Pydantic Models ====================

class ContentGenerationRequest(BaseModel):
    """Request model for content generation."""
    topic: str = Field(..., min_length=3, max_length=200)
    target_keyword: str = Field(..., min_length=2, max_length=100)
    word_count: int = Field(default=1500, ge=500, le=5000)
    content_type: str = Field(default="blog_post")
    target_audience: str = Field(default="general readers")


class ContentItem(BaseModel):
    """Model for a content item in the library."""
    id: str
    title: str
    status: str
    leads: int
    ranking: Optional[int]
    date: str
    topic: str
    keyword: str
    word_count: int
    content: str
    meta_description: str
    metrics: Optional[Dict] = None


class SettingsUpdate(BaseModel):
    """Model for settings updates."""
    llm_model: Optional[str] = None
    temperature: Optional[float] = None
    auto_publish: Optional[bool] = None
    generate_social: Optional[bool] = None
    require_fact_check: Optional[bool] = None

















# ==================== Pydantic Models ====================

class ContentGenerationRequest(BaseModel):
    """Request model for content generation."""
    topic: str = Field(..., min_length=3, max_length=200)
    target_keyword: str = Field(..., min_length=2, max_length=100)
    word_count: int = Field(default=1500, ge=500, le=5000)
    content_type: str = Field(default="blog_post")
    target_audience: str = Field(default="general readers")

# ADD THIS NEW MODEL
class TopicAnalysisRequest(BaseModel):
    """Request model for topic analysis."""
    domain_keywords: List[str] = None
    max_topics: int = Field(default=25, ge=5, le=100)

class ContentItem(BaseModel):
    """Model for a content item in the library."""
    id: str
    title: str
    status: str
    leads: int
    ranking: Optional[int]
    date: str
    topic: str
    keyword: str
    word_count: int
    content: str
    meta_description: str
    metrics: Optional[Dict] = None

class SettingsUpdate(BaseModel):
    """Model for settings updates."""
    llm_model: Optional[str] = None
    temperature: Optional[float] = None
    auto_publish: Optional[bool] = None
    generate_social: Optional[bool] = None
    require_fact_check: Optional[bool] = None

















# ==================== Helper Functions ====================

def load_content_library() -> List[Dict]:
    """Load content library from JSON file."""
    if CONTENT_STORAGE_FILE.exists():
        try:
            with open(CONTENT_STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading content library: {e}")
            return []
    return []


def save_content_library(content_list: List[Dict]):
    """Save content library to JSON file."""
    try:
        with open(CONTENT_STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(content_list, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving content library: {e}")


def initialize_components():
    """Initialize content generation components."""
    global content_agent, metrics_evaluator, metrics_logger

    try:
        content_agent = ContentWriterAgent()
        metrics_evaluator = ContentMetricsEvaluator()
        metrics_logger = MetricsLogger()
        logger.info("Components initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        raise


async def generate_content_task(
    task_id: str,
    request: ContentGenerationRequest
):
    """Background task for content generation."""
    try:
        generation_status[task_id] = {
            "status": "processing",
            "progress": 10,
            "message": "Initializing content generation..."
        }

        # Initialize if needed
        if content_agent is None:
            initialize_components()

        # Generate content
        start_time = time.time()

        generation_status[task_id]["progress"] = 30
        generation_status[task_id]["message"] = "Retrieving brand voice context..."

        article = await asyncio.to_thread(
            content_agent.generate_article,
            topic=request.topic,
            target_keyword=request.target_keyword,
            target_word_count=request.word_count,
            target_audience=request.target_audience,
            content_type=request.content_type
        )

        generation_status[task_id]["progress"] = 70
        generation_status[task_id]["message"] = "Evaluating content quality..."

        # Evaluate metrics
        generation_time = time.time() - start_time
        metrics = metrics_evaluator.evaluate_article(
            article=article,
            target_word_count=request.word_count,
            primary_keyword=request.target_keyword,
            generation_time=generation_time
        )

        # Log metrics
        metrics_logger.log_metrics(
            metrics=metrics,
            metadata={
                "topic": request.topic,
                "keyword": request.target_keyword,
                "word_count": request.word_count
            }
        )

        generation_status[task_id]["progress"] = 90
        generation_status[task_id]["message"] = "Saving content..."

        # Save to library
        content_item = {
            "id": task_id,
            "title": article.title,
            "status": "review",
            "leads": 0,
            "ranking": None,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "topic": request.topic,
            "keyword": request.target_keyword,
            "word_count": article.total_word_count,
            "content": article.markdown_content,
            "meta_description": article.meta_description,
            "metrics": metrics.to_dict()
        }

        content_library = load_content_library()
        content_library.insert(0, content_item)
        save_content_library(content_library)

        # Save markdown file
        output_file = Path("outputs") / f"{task_id}.md"
        output_file.write_text(article.markdown_content, encoding='utf-8')

        generation_status[task_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Content generated successfully!",
            "content_id": task_id,
            "content": content_item
        }

    except Exception as e:
        logger.error(f"Content generation error: {e}", exc_info=True)
        generation_status[task_id] = {
            "status": "error",
            "progress": 0,
            "message": f"Error: {str(e)}"
        }


# ==================== API Endpoints ====================

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    logger.info("Starting AI Content Factory API...")
    try:
        initialize_components()
    except Exception as e:
        logger.warning(f"Could not initialize all components: {e}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard HTML."""
    html_file = Path(__file__).parent / "static" / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return HTMLResponse("<h1>AI Content Factory API</h1><p>UI not found. Please build the frontend.</p>")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "content_agent": content_agent is not None,
            "metrics_evaluator": metrics_evaluator is not None,
            "metrics_logger": metrics_logger is not None
        }
    }


@app.post("/api/content/generate")
async def generate_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Start content generation task."""
    task_id = f"content_{int(time.time() * 1000)}"

    # Start background task
    background_tasks.add_task(generate_content_task, task_id, request)

    generation_status[task_id] = {
        "status": "queued",
        "progress": 0,
        "message": "Task queued for generation..."
    }

    return {
        "task_id": task_id,
        "status": "queued",
        "message": "Content generation started"
    }


@app.get("/api/content/status/{task_id}")
async def get_generation_status(task_id: str):
    """Get status of a content generation task."""
    if task_id not in generation_status:
        raise HTTPException(status_code=404, detail="Task not found")

    return generation_status[task_id]


@app.get("/api/content/library")
async def get_content_library():
    """Get all content from the library."""
    return load_content_library()


@app.get("/api/content/{content_id}")
async def get_content(content_id: str):
    """Get specific content by ID."""
    content_library = load_content_library()
    content = next((item for item in content_library if item["id"] == content_id), None)

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return content


@app.delete("/api/content/{content_id}")
async def delete_content(content_id: str):
    """Delete content from library."""
    content_library = load_content_library()
    updated_library = [item for item in content_library if item["id"] != content_id]

    if len(updated_library) == len(content_library):
        raise HTTPException(status_code=404, detail="Content not found")

    save_content_library(updated_library)

    # Try to delete the markdown file
    try:
        output_file = Path("outputs") / f"{content_id}.md"
        if output_file.exists():
            output_file.unlink()
    except Exception as e:
        logger.warning(f"Could not delete output file: {e}")

    return {"message": "Content deleted successfully"}


@app.put("/api/content/{content_id}/status")
async def update_content_status(content_id: str, status: str):
    """Update content status."""
    if status not in ["draft", "review", "published"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    content_library = load_content_library()
    content = next((item for item in content_library if item["id"] == content_id), None)

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content["status"] = status
    save_content_library(content_library)

    return {"message": f"Status updated to {status}"}


@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    """Get dashboard analytics data."""
    content_library = load_content_library()

    # Load metrics history
    metrics_file = Path("metrics_logs/metrics_history.json")
    metrics_history = []
    if metrics_file.exists():
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                metrics_history = json.load(f)
        except Exception as e:
            logger.error(f"Error loading metrics history: {e}")

    # Calculate metrics-based KPIs
    total_content = len(content_library)

    # Calculate average metrics from history
    avg_quality_score = 0
    avg_brand_voice = 0
    avg_readability = 0
    avg_generation_time = 0
    avg_keyword_density = 0
    avg_word_count_accuracy = 0
    avg_heading_structure = 0
    avg_seo_requirements = 0
    pass_rate = 0

    if metrics_history:
        n = len(metrics_history)
        avg_quality_score = sum(m.get('content_quality_score', 0) for m in metrics_history) / n
        avg_brand_voice = sum(m.get('brand_voice_similarity', 0) for m in metrics_history) / n
        avg_readability = sum(m.get('readability_score', 0) for m in metrics_history) / n
        avg_generation_time = sum(m.get('generation_time', 0) for m in metrics_history) / n
        avg_keyword_density = sum(m.get('keyword_density', 0) for m in metrics_history) / n
        avg_word_count_accuracy = sum(m.get('word_count_accuracy', 0) for m in metrics_history) / n
        avg_heading_structure = sum(m.get('heading_structure_score', 0) for m in metrics_history) / n
        avg_seo_requirements = sum(m.get('seo_requirements_score', 0) for m in metrics_history) / n
        # Compute pass rate using available metrics only (missing fields won't fail)
        passed = 0
        evaluable = 0
        for m in metrics_history:
            conditions = []
            # Core conditions
            if 'content_quality_score' in m:
                conditions.append(m.get('content_quality_score', 0) >= 70)
            if 'readability_score' in m:
                conditions.append(m.get('readability_score', 0) >= 60)
            if 'generation_time' in m:
                conditions.append(m.get('generation_time', 0) <= 300)
            # Optional conditions (evaluate if present)
            if 'brand_voice_similarity' in m:
                conditions.append(m.get('brand_voice_similarity', 0) >= 0.80)
            if 'keyword_density' in m:
                kd = m.get('keyword_density', 0)
                conditions.append(1.0 <= kd <= 2.0)
            if 'word_count_accuracy' in m:
                conditions.append(m.get('word_count_accuracy', 0) >= 90)
            if 'heading_structure_score' in m:
                # Use slightly softer threshold here for aggregate pass rate
                conditions.append(m.get('heading_structure_score', 0) >= 0.8)
            if 'seo_requirements_score' in m:
                conditions.append(m.get('seo_requirements_score', 0) >= 0.8)

            # Only count items where we had at least one condition to evaluate
            if conditions:
                evaluable += 1
                if all(conditions):
                    passed += 1

        pass_rate = (passed / evaluable) * 100 if evaluable else 0

    # Status breakdown
    status_counts = {
        "published": len([i for i in content_library if i.get("status") == "published"]),
        "review": len([i for i in content_library if i.get("status") == "review"]),
        "draft": len([i for i in content_library if i.get("status") == "draft"])
    }

    # Performance over time - use actual metrics
    performance_data = []
    recent_metrics = metrics_history[-10:] if len(metrics_history) > 10 else metrics_history

    for idx, metric in enumerate(recent_metrics):
        performance_data.append({
            "index": idx + 1,
            "quality_score": round(metric.get('content_quality_score', 0), 1),
            "brand_voice": round(metric.get('brand_voice_similarity', 0) * 100, 1),
            "readability": round(metric.get('readability_score', 0), 1),
            "generation_time": round(metric.get('generation_time', 2), 2)
        })

    return {
        "kpis": {
            "content_generated": total_content,
            "avg_quality_score": f"{avg_quality_score:.1f}",
            "avg_brand_voice": f"{avg_brand_voice * 100:.1f}%",
            "avg_generation_time": f"{avg_generation_time:.1f}s"
        },
        "metrics_summary": {
            "quality_score": round(avg_quality_score, 1),
            "brand_voice": round(avg_brand_voice * 100, 1),
            "readability": round(avg_readability, 1),
            "generation_time": round(avg_generation_time, 1)
        },
        "advanced_metrics": {
            "keyword_density": round(avg_keyword_density, 2),
            "word_count_accuracy": round(avg_word_count_accuracy, 1),
            "heading_structure": round(avg_heading_structure, 2),
            "seo_requirements": round(avg_seo_requirements, 2),
            "pass_rate": round(pass_rate, 1)
        },
        "status_breakdown": status_counts,
        "performance_data": performance_data,
        "top_topics": [
            {"topic": item.get("topic", "Unknown"), "leads": item.get("leads", 0)}
            for item in sorted(content_library, key=lambda x: x.get("leads", 0), reverse=True)[:5]
        ]
    }


@app.get("/api/metrics/history")
async def get_metrics_history():
    """Get historical metrics data."""
    metrics_file = Path("metrics_logs/metrics_history.json")

    if not metrics_file.exists():
        return []

    try:
        with open(metrics_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading metrics: {e}")
        return []


@app.get("/api/settings")
async def get_settings():
    """Get current settings."""
    return {
        "llm_model": config.llm.models.primary if config.llm.models else "qwen2.5:7B",
        "temperature": config.llm.temperature if config.llm else 0.7,
        "max_tokens": config.llm.max_tokens if config.llm else 2500,
        "auto_publish": False,
        "generate_social": False,
        "require_fact_check": False
    }


@app.put("/api/settings")
async def update_settings(settings: SettingsUpdate):
    """Update settings."""
    # In a real implementation, this would update the config file
    logger.info(f"Settings update requested: {settings}")
    return {"message": "Settings updated successfully"}


@app.get("/api/brand-voices")
async def get_brand_voices():
    """Get available brand voice options."""
    return [
        {"id": "professional", "name": "Professional", "description": "Formal and authoritative"},
        {"id": "friendly", "name": "Friendly", "description": "Warm and approachable"},
        {"id": "conversational", "name": "Conversational", "description": "Casual and engaging"},
        {"id": "technical", "name": "Technical", "description": "Detailed and precise"}
    ]


# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
































class TopicAnalysisRequest(BaseModel):
    """Request model for topic analysis."""
    domain_keywords: List[str] = None
    max_topics: int = Field(default=25, ge=5, le=100)

@app.post("/api/research/analyze-competitors")
async def analyze_competitors(competitor_domains: List[str] = None, keywords: List[str] = None):
    """Analyze competitor content and identify gaps"""
    try:
        analyzer = AdvancedResearchAgent(domain_keywords=keywords or ['ai', 'technology', 'digital', 'innovation'])
        research_data = analyzer.comprehensive_research_analysis(
            competitor_domains=competitor_domains,
            keywords_of_interest=keywords,
            max_topics=25
        )
        
        # Save research data
        research_file = "metrics_logs/research_data.json"
        with open(research_file, 'w', encoding='utf-8') as f:
            json.dump(research_data, f, indent=2, ensure_ascii=False)
            
        return {
            "status": "success",
            "data": research_data,
            "message": f"Research completed: {len(research_data['web_scraping_results']['scraped_posts'])} posts analyzed"
        }
    except Exception as e:
        logger.error(f"Research analysis failed: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/api/research/insights")
async def get_research_insights():
    """Get latest research insights"""
    try:
        research_file = "metrics_logs/research_data.json"
        if os.path.exists(research_file):
            with open(research_file, 'r', encoding='utf-8') as f:
                research_data = json.load(f)
            return {"status": "success", "data": research_data}
        else:
            return {"status": "error", "message": "No research data available"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/research/analyze-topics")
async def analyze_topics(
    request: TopicAnalysisRequest = None,
    domain_keywords: str = None,
    max_topics: int = 25
):
    """Perform advanced topic analysis - supports both JSON body and query params"""
    try:
        # Handle both JSON body and query parameters
        if request is None:
            # Parse from query parameters
            if domain_keywords:
                if isinstance(domain_keywords, str):
                    domain_keywords_list = [kw.strip() for kw in domain_keywords.split(',')]
                else:
                    domain_keywords_list = domain_keywords
            else:
                domain_keywords_list = ['skincare', 'beauty', 'routine', 'ingredients']
            
            request_data = {
                "domain_keywords": domain_keywords_list,
                "max_topics": max_topics
            }
        else:
            # Use the request body
            request_data = {
                "domain_keywords": request.domain_keywords or ['skincare', 'beauty', 'routine', 'ingredients'],
                "max_topics": request.max_topics or 25
            }
            
        research_agent = AdvancedResearchAgent(domain_keywords=request_data['domain_keywords'])
        analysis_result = research_agent.comprehensive_topic_analysis(max_topics=request_data['max_topics'])
        
        # Save analysis
        analysis_file = "metrics_logs/topic_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            
        return {
            "status": "success",
            "data": analysis_result,
            "message": f"Topic analysis completed: {len(analysis_result['analyzed_topics'])} topics analyzed"
        }
    except Exception as e:
        logger.error(f"Topic analysis failed: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/api/research/topic-recommendations")
async def get_topic_recommendations():
    """Get topic recommendations from latest analysis"""
    try:
        analysis_file = "metrics_logs/topic_analysis.json"
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            recommendations = {
                "top_priority_topics": analysis_data.get('top_priority_topics', [])[:5],
                "content_recommendations": analysis_data.get('content_recommendations', []),
                "clusters": analysis_data.get('cluster_analysis', {})
            }
            
            return {"status": "success", "data": recommendations}
        else:
            return {"status": "error", "message": "No topic analysis available"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/test/research-agent")
async def test_research_agent():
    """Test endpoint for research agent functionality"""
    try:
        from src.ai_content_factory.agents.research_agent import AdvancedResearchAgent
        
        # Quick initialization test
        agent = AdvancedResearchAgent()
        
        return {
            "status": "success",
            "message": "Research Agent initialized successfully",
            "components": {
                "web_scraper": hasattr(agent, 'scraper'),
                "topic_analyzer": hasattr(agent, 'topic_analyzer'),
                "gap_analyzer": hasattr(agent, 'gap_analyzer'),
                "clusterer": hasattr(agent, 'clusterer'),
                "ranker": hasattr(agent, 'ranker')
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
