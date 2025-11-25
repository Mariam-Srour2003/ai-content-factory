"""
LangChain/LangGraph-based Content Writer Agent
Refactored for multi-agent workflow compatibility using LangGraph state machines.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from ..config.config_loader import load_config
from ..database.chroma_manager import VectorStoreHybrid
from ..llm.ollama_provider import OllamaProvider
from ..utils.exceptions import ContentGenerationError
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Content generation constants
INTRO_WORD_RATIO = 0.12
CONCLUSION_WORD_RATIO = 0.10
BODY_WORD_RATIO = 0.78
WORDS_PER_SECTION = 250
MIN_SECTIONS = 3
MAX_SECTIONS = 7
KEYWORD_FREQUENCY = 300  # 1 keyword per N words (increased from 250 to target ~1.5% density)
DEFAULT_BRAND_VOICE = "Direct, educational, accessible. Example: 'Skin is a complex organ. Your skincare doesn't have to be.'"


# Type definitions for article structure (maintained for metrics compatibility)
@dataclass
class ArticleSection:
    """Represents a section of the article."""
    heading: str
    level: int
    content: str
    word_count: int


@dataclass
class Article:
    """Complete article structure."""
    title: str
    meta_description: str
    introduction: str
    sections: List[ArticleSection]
    conclusion: str
    call_to_action: str
    total_word_count: int
    markdown_content: str
    html_content: Optional[str] = None


# LangGraph State Definition
class ContentState(TypedDict):
    """State object passed between nodes in the content generation workflow."""

    # Input fields
    topic: str
    target_keyword: str
    target_word_count: int
    target_audience: str
    content_type: str

    # Intermediate state
    brand_voice_context: str
    outline: Dict[str, Any]
    sections: List[Dict[str, str]]  # List of sections (no operator.add)
    introduction: str
    conclusion: str
    cta: str

    # Final output
    article: str
    meta_description: str
    meta_keywords: List[str]

    # Control flow
    current_section_index: int
    total_sections: int
    error: Optional[str]


class ContentWriterAgent:
    """
    LangChain/LangGraph-based content writer agent for AI Content Factory.

    Uses LangGraph StateGraph to orchestrate multi-step content generation workflow:
    1. Retrieve brand voice context from ChromaDB
    2. Generate article outline
    3. Write introduction
    4. Write body sections (loop)
    5. Write conclusion
    6. Generate call-to-action
    7. Assemble final article
    8. Optimize for SEO

    Designed for integration into multi-agent workflows (SEO Strategy Agent, Editor Agent, etc.)
    """

    def __init__(self):
        """Initialize the content writer agent with LangGraph workflow."""
        self.config = load_config()
        self.chroma = VectorStoreHybrid()
        self.llm = OllamaProvider()  # OllamaProvider loads config internally

        # Build the LangGraph workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

        logger.info("ContentWriterAgent initialized with LangGraph workflow")

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph StateGraph workflow for content generation.

        Returns:
            StateGraph: Compiled workflow graph
        """
        workflow = StateGraph(ContentState)

        # Add nodes for each step
        workflow.add_node("retrieve_brand_voice", self._retrieve_brand_voice_node)
        workflow.add_node("generate_outline", self._generate_outline_node)
        workflow.add_node("write_introduction", self._write_introduction_node)
        workflow.add_node("write_section", self._write_section_node)
        workflow.add_node("write_conclusion", self._write_conclusion_node)
        workflow.add_node("generate_cta", self._generate_cta_node)
        workflow.add_node("assemble_article", self._assemble_article_node)
        workflow.add_node("optimize_seo", self._optimize_seo_node)

        # Define the workflow edges
        workflow.set_entry_point("retrieve_brand_voice")
        workflow.add_edge("retrieve_brand_voice", "generate_outline")
        workflow.add_edge("generate_outline", "write_introduction")
        workflow.add_edge("write_introduction", "write_section")

        # Conditional edge for section loop
        workflow.add_conditional_edges(
            "write_section",
            self._should_continue_sections,
            {
                "continue": "write_section",
                "done": "write_conclusion"
            }
        )

        workflow.add_edge("write_conclusion", "generate_cta")
        workflow.add_edge("generate_cta", "assemble_article")
        workflow.add_edge("assemble_article", "optimize_seo")
        workflow.add_edge("optimize_seo", END)

        return workflow

    def generate_article(
        self,
        topic: str,
        target_keyword: str,
        target_word_count: int = 1000,
        target_audience: str = "general readers",
        content_type: str = "blog_post",
        output_path: Optional[str] = None
    ) -> Article:
        """
        Generate a complete article using the LangGraph workflow.

        Args:
            topic: Article topic
            target_keyword: Primary SEO keyword
            target_word_count: Target word count (default 1000)
            target_audience: Target audience description
            content_type: Type of content (blog_post, guide, tutorial, etc.)
            output_path: Optional path to save the article markdown

        Returns:
            Article object containing all content and metadata
        """
        # Validate inputs
        if not topic or not isinstance(topic, str) or len(topic.strip()) == 0:
            raise ValueError("Topic must be a non-empty string")
        if not target_keyword or not isinstance(target_keyword, str) or len(target_keyword.strip()) == 0:
            raise ValueError("Target keyword must be a non-empty string")
        if target_word_count <= 0:
            raise ValueError(f"Target word count must be positive, got {target_word_count}")
        if target_word_count > 10000:
            logger.warning(f"Very large word count requested: {target_word_count}. Generation may take significant time.")

        # Sanitize inputs to prevent injection
        topic = topic.strip()[:500]  # Limit length
        target_keyword = target_keyword.strip()[:100]
        target_audience = target_audience.strip()[:200] if target_audience else "general readers"

        logger.info(f"Starting article generation - Topic: {topic[:50]}..., Keyword: {target_keyword}, Target: {target_word_count} words")

        # Initialize state
        initial_state: ContentState = {
            "topic": topic,
            "target_keyword": target_keyword,
            "target_word_count": target_word_count,
            "target_audience": target_audience,
            "content_type": content_type,
            "brand_voice_context": "",
            "outline": {},
            "sections": [],
            "introduction": "",
            "conclusion": "",
            "cta": "",
            "article": "",
            "meta_description": "",
            "meta_keywords": [],
            "current_section_index": 0,
            "total_sections": 0,
            "error": None
        }

        # Execute the workflow
        try:
            final_state = self.app.invoke(initial_state)

            if final_state.get("error"):
                logger.error(f"Error in workflow: {final_state['error']}")
                raise ContentGenerationError(final_state["error"])

            logger.info("Article generation completed successfully")

            # Convert state to Article object
            article = self._state_to_article(final_state)

            # Save to file if output path provided
            if output_path:
                self._save_article(article, output_path)

            return article

        except ContentGenerationError:
            # Already logged, just re-raise
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing workflow: {str(e)}", exc_info=True)
            raise ContentGenerationError(f"Article generation failed: {str(e)}") from e

    def _state_to_article(self, state: ContentState) -> Article:
        """
        Convert workflow state to Article dataclass.

        Args:
            state: Final workflow state

        Returns:
            Article object with all content
        """
        # Parse sections from state
        article_sections = []
        for section_data in state["sections"]:
            # Extract content without heading
            content = section_data["content"]
            lines = content.split('\n')
            heading_line = ""
            content_lines = []

            for line in lines:
                if line.startswith("## "):
                    heading_line = line.replace("## ", "").strip()
                elif line.strip():
                    content_lines.append(line)

            section_content = '\n'.join(content_lines).strip()

            article_sections.append(ArticleSection(
                heading=heading_line or section_data["title"],
                level=2,
                content=section_content,
                word_count=len(section_content.split())
            ))

        # Calculate total word count
        total_words = len(state["article"].split())

        return Article(
            title=state["topic"],
            meta_description=state["meta_description"],
            introduction=state["introduction"],
            sections=article_sections,
            conclusion=state["conclusion"],
            call_to_action=state["cta"],
            total_word_count=total_words,
            markdown_content=state["article"]
        )

    def _save_article(self, article: Article, output_path: str) -> None:
        """
        Save article to markdown file.

        Args:
            article: Article to save
            output_path: Path to save the file
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(article.markdown_content)
            f.write("\n\n---\n\n")
            f.write(f"**Meta Description:** {article.meta_description}\n")

        logger.info(f"Article saved to {output_path}")

    # ========== Workflow Node Functions ==========

    def _clean_meta_text(self, text: str) -> str:
        """Clean up meta-text artifacts from LLM output.

        Removes phrases like 'Okay, here's...', 'Here's a...', quotes, and other meta-commentary.

        Args:
            text: Raw LLM output

        Returns:
            Cleaned text
        """
        import re

        # Remove common meta-text patterns
        patterns = [
            r'^\s*Okay,?\s+here[\'\'\"s]+ (an? )?\w+.*?:\s*',  # "Okay, here's an introduction:"
            r'^\s*Here[\'\'\"s]+ (an? )?\w+.*?:\s*',  # "Here's a section:"
            r'^\s*[\"\']+(.*?)[\"\']+\s*$',  # Wrapping quotes
            r'\n\n---\n\n\*\*Word Count:\*\*.*',  # Word count notes
            r'^\s*\[.*?\]\s*',  # [Link to...]
        ]

        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)
        return text.strip()

    def _retrieve_brand_voice_node(self, state: ContentState) -> ContentState:
        """
        Node 1: Retrieve relevant brand voice context from ChromaDB.

        Uses semantic search to find brand voice samples similar to the topic.
        """
        try:
            logger.info("Retrieving brand voice context")

            # Get collection name from config
            collection_names = self.config.vector_db.collection_names
            collection_name = collection_names.get("brand_voice", "brand_voice_examples")

            # Check if collection exists
            available_collections = self.chroma.list_collections()
            if collection_name not in available_collections:
                logger.warning(f"Collection '{collection_name}' not found. Available: {available_collections}")
                state["brand_voice_context"] = ""
                return state

            # Query ChromaDB for similar brand voice samples
            results = self.chroma.query(
                collection_name=collection_name,
                query_text=state["topic"],
                k=3
            )

            # Format context from results
            if results:
                context_pieces = []
                for i, doc in enumerate(results):
                    title = doc.metadata.get('title', 'Untitled')
                    context_pieces.append(f"Example {i+1} - {title}:\n{doc.page_content}")

                state["brand_voice_context"] = "\n\n".join(context_pieces)
                logger.info(f"Retrieved {len(results)} brand voice examples")
            else:
                logger.warning(f"No brand voice found for topic: {state['topic']}. Using default.")
                state["brand_voice_context"] = DEFAULT_BRAND_VOICE

        except (KeyError, ValueError, RuntimeError) as e:
            logger.error(f"Brand voice retrieval failed: {str(e)}", exc_info=True)
            state["error"] = f"Brand voice retrieval failed: {str(e)}"
        except Exception as e:
            logger.critical(f"Unexpected error in brand voice retrieval: {str(e)}", exc_info=True)
            raise

        return state

    def _generate_outline_node(self, state: ContentState) -> ContentState:
        """
        Node 2: Generate article outline with sections.

        Creates a structured outline with section titles and word count allocations.
        """
        try:
            logger.info("Generating article outline")

            # Calculate word count distribution using constants
            intro_words = int(state["target_word_count"] * INTRO_WORD_RATIO)
            conclusion_words = int(state["target_word_count"] * CONCLUSION_WORD_RATIO)
            body_words = state["target_word_count"] - intro_words - conclusion_words

            # Determine number of sections
            num_sections = max(MIN_SECTIONS, min(MAX_SECTIONS, body_words // WORDS_PER_SECTION))
            words_per_section = body_words // num_sections

            system_prompt = """You are an expert content strategist. Create a clear, logical outline for a blog article.

Requirements:
- Direct, conversational, simple style
- Each section should cover one main point
- Section titles should be descriptive and engaging
- Logical flow from one section to the next

Respond with ONLY section titles, one per line, no numbering or formatting."""

            user_prompt = f"""Create an outline with exactly {num_sections} main sections for this article:

Topic: {state['topic']}
Keyword: {state['target_keyword']}
Audience: {state['target_audience']}

List {num_sections} section titles (one per line):"""

            response = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=300,
                temperature=0.7
            )

            # Parse section titles
            section_titles = [
                line.strip().lstrip('123456789.-) ')
                for line in response.strip().split('\n')
                if line.strip() and len(line.strip()) > 5
            ]

            # Ensure we have the right number of sections
            section_titles = section_titles[:num_sections]
            if len(section_titles) < num_sections:
                # Fill with generic titles if needed
                for i in range(len(section_titles), num_sections):
                    section_titles.append(f"Additional Insights on {state['target_keyword']}")

            state["outline"] = {
                "introduction": {
                    "word_count": intro_words
                },
                "sections": [
                    {
                        "title": title,
                        "word_count": words_per_section
                    }
                    for title in section_titles
                ],
                "conclusion": {
                    "word_count": conclusion_words
                }
            }

            state["total_sections"] = len(section_titles)
            logger.info(f"Generated outline with {state['total_sections']} sections")

        except (KeyError, ValueError, RuntimeError) as e:
            logger.error(f"Outline generation failed: {str(e)}", exc_info=True)
            state["error"] = f"Outline generation failed: {str(e)}"
        except Exception as e:
            logger.critical(f"Unexpected error in outline generation: {str(e)}", exc_info=True)
            raise

        return state

    def _write_introduction_node(self, state: ContentState) -> ContentState:
        """
        Node 3: Write the article introduction.

        Creates an engaging introduction with hook, context, and preview.
        """
        try:
            logger.info("Writing introduction")

            target_words = state["outline"]["introduction"]["word_count"]

            system_prompt = """Write simple, direct introductions.
Use short sentences (6-10 words average).
Simple words only. Break complex ideas into separate sentences.

Write complete content. No meta-commentary."""

            brand_examples = state.get('brand_voice_context', DEFAULT_BRAND_VOICE)

            user_prompt = f"""Write EXACTLY {target_words} words introducing: {state['target_keyword']}

Start with "{state['target_keyword']}" in first sentence. Use it 2 times total.
Short sentences. Simple words. Reach {target_words} words.
No explanations.

Brand voice:
{brand_examples}

BEGIN WRITING NOW:"""

            introduction = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=2000,
                temperature=0.45
            )

            # Clean up meta-text artifacts aggressively
            introduction = self._clean_meta_text(introduction)

            # Additional cleanup: remove first paragraph if it contains meta-text
            paragraphs = introduction.split('\n\n')
            if paragraphs and len(paragraphs) > 1:
                first_para = paragraphs[0].lower()
                if any(phrase in first_para for phrase in ['here\'s', 'okay', 'let me', 'aiming for', 'for the']):
                    introduction = '\n\n'.join(paragraphs[1:])

            state["introduction"] = introduction.strip()
            logger.info(f"Introduction written: {len(state['introduction'].split())} words")

        except (KeyError, ValueError, RuntimeError) as e:
            logger.error(f"Introduction writing failed: {str(e)}", exc_info=True)
            state["error"] = f"Introduction writing failed: {str(e)}"
        except Exception as e:
            logger.critical(f"Unexpected error in introduction: {str(e)}", exc_info=True)
            raise

        return state

    def _write_section_node(self, state: ContentState) -> ContentState:
        """
        Node 4: Write a single body section.

        This node is called multiple times in a loop to write all body sections.
        """
        try:
            section_index = state["current_section_index"]
            section_info = state["outline"]["sections"][section_index]

            logger.info(f"Writing section {section_index + 1}/{state['total_sections']}: {section_info['title']}")

            target_words = section_info["word_count"]

            system_prompt = """Write clear, simple content.
Short sentences (6-10 words).
Simple words. One idea per sentence.

No meta-commentary. Just content."""

            keyword = state['target_keyword']
            # Calculate keyword density using constant
            target_keyword_count = max(1, target_words // KEYWORD_FREQUENCY)

            brand_examples = state.get('brand_voice_context', DEFAULT_BRAND_VOICE)

            user_prompt = f"""Write EXACTLY {target_words} words about: {section_info['title']}

Include "{keyword}" {target_keyword_count} times naturally.
Short sentences. Simple words. Reach {target_words} words.
No explanations.

Brand voice:
{brand_examples[:300]}

BEGIN WRITING NOW:"""

            section_content = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=2500,
                temperature=0.45
            )

            # Clean up meta-text artifacts
            section_content = self._clean_meta_text(section_content)

            # Ensure proper heading format
            section_content = section_content.strip()
            if not section_content.startswith("## "):
                section_content = f"## {section_info['title']}\n\n{section_content}"

            # Validate word count
            actual_words = len(section_content.split())
            if actual_words < target_words * 0.5:
                logger.warning(f"Section {section_index + 1} too short: {actual_words}/{target_words} words")

            # Append to sections list
            state["sections"].append({
                "title": section_info["title"],
                "content": section_content
            })

            # Increment section counter
            state["current_section_index"] += 1

            logger.info(f"Section {section_index + 1} written: {actual_words} words (target: {target_words})")

        except (KeyError, ValueError, RuntimeError) as e:
            logger.error(f"Section writing failed: {str(e)}", exc_info=True)
            state["error"] = f"Section writing failed: {str(e)}"
        except Exception as e:
            logger.critical(f"Unexpected error in section writing: {str(e)}", exc_info=True)
            raise

        return state

    def _should_continue_sections(self, state: ContentState) -> str:
        """
        Conditional edge function: Determine if more sections need to be written.

        Returns:
            "continue" if more sections to write, "done" if all sections complete
        """
        if state["current_section_index"] < state["total_sections"]:
            return "continue"
        else:
            return "done"

    def _write_conclusion_node(self, state: ContentState) -> ContentState:
        """
        Node 5: Write the article conclusion.

        Creates a conclusion that summarizes key points and provides final thoughts.
        """
        try:
            logger.info("Writing conclusion")

            target_words = state["outline"]["conclusion"]["word_count"]

            # Get section titles for summary context
            [s["title"] for s in state["outline"]["sections"]]

            brand_examples = state.get('brand_voice_context', DEFAULT_BRAND_VOICE)

            system_prompt = """Write clear, simple conclusions.
Short sentences (8-12 words).
Summarize key points.

No meta-commentary."""

            # Get section summaries for context
            key_points = "\n".join([
                f"- {s['title']}"
                for s in state["sections"][:3]  # First 3 sections
            ])

            brand_examples = state.get('brand_voice_context', DEFAULT_BRAND_VOICE)

            user_prompt = f"""Write EXACTLY {target_words} words concluding this article about {state['target_keyword']}.

Key points:
{key_points}

Mention "{state['target_keyword']}" once.
Write {target_words} words total.
No explanations.

Brand voice:
{brand_examples[:200]}

BEGIN WRITING NOW:"""

            conclusion = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1500,
                temperature=0.45
            )

            # Clean up meta-text artifacts
            conclusion = self._clean_meta_text(conclusion)
            state["conclusion"] = conclusion.strip()
            logger.info(f"Conclusion written: {len(state['conclusion'].split())} words")

        except (KeyError, ValueError, RuntimeError) as e:
            logger.error(f"Conclusion writing failed: {str(e)}", exc_info=True)
            state["error"] = f"Conclusion writing failed: {str(e)}"
        except Exception as e:
            logger.critical(f"Unexpected error in conclusion: {str(e)}", exc_info=True)
            raise

        return state

    def _generate_cta_node(self, state: ContentState) -> ContentState:
        """
        Node 6: Generate call-to-action.

        Creates a brief, compelling CTA encouraging reader engagement.
        """
        try:
            logger.info("Generating call-to-action")

            system_prompt = """Write 2 short call-to-action sentences.
Friendly tone. Under 12 words each."""

            user_prompt = f"""Write 2 sentences inviting readers to explore {state['target_keyword']}.

Just the 2 sentences. No explanations.

BEGIN:"""

            cta = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=300,
                temperature=0.6
            )

            state["cta"] = cta.strip()
            logger.info("Call-to-action generated")

        except (KeyError, ValueError, RuntimeError) as e:
            logger.error(f"CTA generation failed: {str(e)}", exc_info=True)
            state["error"] = f"CTA generation failed: {str(e)}"
        except Exception as e:
            logger.critical(f"Unexpected error in CTA generation: {str(e)}", exc_info=True)
            raise

        return state

    def _assemble_article_node(self, state: ContentState) -> ContentState:
        """
        Node 7: Assemble all components into final article.

        Combines introduction, sections, conclusion, and CTA into complete article.
        """
        try:
            logger.info("Assembling article")

            # Build article parts
            parts = []

            # Title (H1)
            title = state["topic"]
            if not title.startswith("# "):
                title = f"# {title}"
            parts.append(title)
            parts.append("")  # Blank line

            # Add meta description if available
            if "meta_description" in state and state["meta_description"]:
                parts.append(f"*{state['meta_description']}*")
                parts.append("")  # Blank line

            # Introduction
            parts.append(state["introduction"])
            parts.append("")

            # Body sections
            for section in state["sections"]:
                parts.append(section["content"])
                parts.append("")

            # Conclusion
            parts.append("## Conclusion")
            parts.append("")
            parts.append(state["conclusion"])
            parts.append("")

            # Call-to-action
            parts.append("---")
            parts.append("")
            parts.append(state["cta"])

            # Join all parts
            state["article"] = "\n".join(parts)

            word_count = len(state["article"].split())
            logger.info(f"Article assembled: {word_count} words")

        except (KeyError, ValueError, RuntimeError) as e:
            logger.error(f"Article assembly failed: {str(e)}", exc_info=True)
            state["error"] = f"Article assembly failed: {str(e)}"
        except Exception as e:
            logger.critical(f"Unexpected error in article assembly: {str(e)}", exc_info=True)
            raise

        return state

    def _optimize_seo_node(self, state: ContentState) -> ContentState:
        """
        Node 8: Optimize article for SEO.

        Generates meta description and keywords, validates heading structure.
        """
        try:
            logger.info("Optimizing for SEO")

            # Generate meta description
            meta_prompt = f"""Write a meta description for this article.

Requirements:
- Start with: "{state['target_keyword']}"
- Length: 140-155 characters total
- Enticing and clear

Just write the description. No explanations.

Meta description:"""

            meta_description = self.llm.generate(
                prompt=meta_prompt,
                system_prompt="You are an SEO expert writing meta descriptions.",
                max_tokens=100,
                temperature=0.6
            )

            meta_description = meta_description.strip().strip('"')

            # Ensure keyword is at the start for better SEO
            if not meta_description.lower().startswith(state["target_keyword"].lower()):
                meta_description = f"{state['target_keyword']}: {meta_description}"

            # Validate length (120-160 chars) - target middle of range
            if len(meta_description) < 120:
                meta_description = meta_description + f" Learn everything about {state['target_keyword']}."
            if len(meta_description) > 160:
                meta_description = meta_description[:157] + "..."

            state["meta_description"] = meta_description

            # Generate meta keywords (5-10 related keywords)
            keywords_prompt = f"""Generate 5-10 SEO keywords for this article:

Topic: {state['topic']}
Primary Keyword: {state['target_keyword']}

List keywords (comma-separated):"""

            keywords_response = self.llm.generate(
                prompt=keywords_prompt,
                system_prompt="You are an SEO expert generating keywords.",
                max_tokens=100,
                temperature=0.7
            )

            # Parse keywords
            keywords = [
                kw.strip().strip('"\'')
                for kw in keywords_response.split(',')
                if kw.strip()
            ]

            # Ensure primary keyword is first
            if state["target_keyword"] not in keywords:
                keywords.insert(0, state["target_keyword"])

            state["meta_keywords"] = keywords[:10]

            # Validate heading hierarchy (H1 -> H2 -> H3, no skipping)
            lines = state["article"].split('\n')
            fixed_lines = []
            last_heading_level = 1  # Start with H1

            for line in lines:
                if line.startswith('#'):
                    # Count heading level
                    level = len(line) - len(line.lstrip('#'))

                    # Fix skipped levels (e.g., H1 -> H3 becomes H1 -> H2)
                    if level > last_heading_level + 1:
                        level = last_heading_level + 1
                        line = '#' * level + line.lstrip('#')

                    last_heading_level = level

                fixed_lines.append(line)

            state["article"] = '\n'.join(fixed_lines)

            logger.info("SEO optimization complete")
            logger.info(f"Meta description: {len(state['meta_description'])} chars")
            logger.info(f"Meta keywords: {len(state['meta_keywords'])} keywords")

        except (KeyError, ValueError, RuntimeError) as e:
            logger.error(f"SEO optimization failed: {str(e)}", exc_info=True)
            state["error"] = f"SEO optimization failed: {str(e)}"
        except Exception as e:
            logger.critical(f"Unexpected error in SEO optimization: {str(e)}", exc_info=True)
            raise

        return state


# Convenience function for backwards compatibility
def create_content_writer_agent() -> ContentWriterAgent:
    """Factory function to create a ContentWriterAgent instance."""
    return ContentWriterAgent()
