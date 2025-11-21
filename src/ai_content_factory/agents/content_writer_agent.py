"""Content Writer Agent - Generates SEO-optimized blog posts."""

from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict

from ..config.config_loader import load_config
from ..database.chroma_manager import VectorStoreHybrid


# Type definitions for article structure
class ContentBrief(TypedDict):
    """Content brief structure."""
    primary_keyword: str
    secondary_keywords: List[str]
    target_word_count: int
    search_intent: str
    recommended_headings: List[str]
    meta_title: str
    meta_description: str


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


class ContentWriterAgent:
    """Agent responsible for generating SEO-optimized content in brand voice."""

    def __init__(self, llm_provider=None):
        """Initialize the Content Writer Agent.

        Args:
            llm_provider: Optional LLM provider (if None, needs to be set up separately)
        """
        self.config = load_config()
        self.db_manager = VectorStoreHybrid()
        self.llm = llm_provider
        self._brand_voice_cache = {}  # Cache for performance
        self.system_prompt = """You are an expert content writer specializing in SEO-optimized,
brand-voice content. Write in a direct, conversational, simple style that's easy to understand.

WRITING RULES:
- Use 8th-9th grade reading level (Flesch score 60-70)
- Keep sentences under 20 words
- Use simple words (avoid jargon unless explained)
- One idea per sentence
- Short paragraphs (2-3 sentences max)

Match this tone: "Skin is a complex organ. Your skincare doesn't have to be."""

        print("✓ Content Writer Agent initialized")
        print(f"  • Vector DB: {self.db_manager.persist_dir}")
        print(f"  • Collections available: {self.db_manager.list_collections()}")

    def _generate_with_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate text using the LLM provider.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt (uses default if None)
            temperature: Temperature for generation
        Returns:
            Generated text
        """
        if self.llm is None:
            raise RuntimeError(
                "LLM provider not set. Initialize ContentWriterAgent with an LLM provider, "
                "or set agent.llm to a provider that has a generate() method."
            )

        sys_prompt = system_prompt or self.system_prompt

        # Check if LLM has expected interface
        if hasattr(self.llm, 'generate'):
            return self.llm.generate(
                prompt=prompt,
                system_prompt=sys_prompt,
                temperature=temperature
            )
        elif hasattr(self.llm, '__call__'):
            # Fallback for callable LLMs
            return self.llm(f"{sys_prompt}\n\n{prompt}")
        else:
            raise RuntimeError(
                f"LLM provider {type(self.llm)} doesn't have generate() or __call__() method"
            )

    # ========================================================================
    # STEP 1: Brand Voice Retrieval (RAG)
    # ========================================================================

    def get_brand_voice_examples(
        self,
        topic: str,
        content_type: str = "blog_post",
        n_examples: int = 3
    ) -> str:
        """Retrieve similar brand voice examples from ChromaDB.

        This is RAG (Retrieval Augmented Generation) - we find existing
        examples of our brand voice to help the LLM match our style.

        Args:
            topic: The topic we're writing about
            content_type: Type of content (blog_post, product_description, etc.)
            n_examples: Number of examples to retrieve

        Returns:
            Formatted string with examples to include in prompt
        """
        # Check cache first
        cache_key = f"{topic}_{content_type}_{n_examples}"
        if cache_key in self._brand_voice_cache:
            return self._brand_voice_cache[cache_key]

        try:
            # Get the collection name from config
            collection_names = self.config.vector_db.collection_names
            collection_name = collection_names.get("brand_voice", "brand_voice_examples")

            # Check if collection exists
            available_collections = self.db_manager.list_collections()
            if collection_name not in available_collections:
                print(f"⚠️  Collection '{collection_name}' not found. Available: {available_collections}")
                return ""

            # Query ChromaDB for similar brand voice examples using the database manager
            results = self.db_manager.query(
                collection_name=collection_name,
                query_text=topic,
                k=n_examples
            )

            # Format examples for prompt
            if not results:
                print("⚠️  No brand voice examples found, using defaults")
                return ""

            examples_text = "\n\n".join([
                f"Example {i+1} - {doc.metadata.get('title', 'Untitled')}:\n{doc.page_content}"
                for i, doc in enumerate(results)
            ])

            print(f"✓ Retrieved {len(results)} brand voice examples")
            return examples_text

        except Exception as e:
            print(f"⚠️  Error retrieving brand voice: {str(e)}")
            return ""

    # ========================================================================
    # STEP 2: Outline Generation
    # ========================================================================

    def generate_outline(self, brief: ContentBrief) -> List[Dict[str, any]]:
        """Generate article outline from content brief.

        This creates the structure of the article - what sections to include,
        in what order, and how many words each should be.

        Args:
            brief: Content brief from SEO Strategy Agent

        Returns:
            List of sections with headings and target word counts
        """
        print("\n📝 Generating article outline...")

        # Validate and fix meta description first
        brief = self._validate_and_fix_meta(brief)

        # Get brand voice examples
        self.get_brand_voice_examples(
            topic=brief['primary_keyword'],
            content_type="blog_post"
        )        # Build prompt for outline generation with simpler approach
        # Calculate word distribution
        total_words = brief['target_word_count']
        intro_words = int(total_words * 0.12)  # 12%
        conclusion_words = int(total_words * 0.10)  # 10%
        body_words = total_words - intro_words - conclusion_words

        num_sections = len(brief['recommended_headings'])
        words_per_section = body_words // num_sections if num_sections > 0 else body_words

        # Create structured outline directly
        outline_sections = []
        for heading in brief['recommended_headings']:
            outline_sections.append({
                "heading": heading,
                "level": 2,
                "target_word_count": words_per_section,
                "key_points": [
                    f"Explain {heading.lower()}",
                    "Include examples",
                    "Use simple language"
                ]
            })

        # Fix heading hierarchy
        outline_sections = self._fix_heading_hierarchy(outline_sections)

        print(f"✓ Generated outline with {len(outline_sections)} sections")
        return outline_sections

    def _validate_and_fix_meta(self, brief: ContentBrief) -> ContentBrief:
        """Ensure meta description meets SEO requirements.

        Args:
            brief: Content brief to validate

        Returns:
            Updated brief with valid meta description
        """
        meta = brief['meta_description']
        keyword = brief['primary_keyword']

        # Check length (120-160 chars)
        if not (120 <= len(meta) <= 160):
            print(f"  ⚠️  Meta description length: {len(meta)} (target: 120-160)")
            if len(meta) < 120:
                # Expand
                meta = f"{meta} Learn about {keyword} and improve your skincare routine."
            elif len(meta) > 160:
                # Truncate smartly
                meta = meta[:157] + "..."
            brief['meta_description'] = meta

        # Check keyword presence
        if keyword.lower() not in meta.lower():
            print(f"  ⚠️  Adding keyword '{keyword}' to meta description")
            # Add keyword at the start if there's room
            if len(meta) < 140:
                meta = f"{keyword}: {meta}"
            else:
                # Replace some text with keyword
                meta = f"{keyword}. {meta[len(keyword)+2:]}"
            meta = meta[:160]  # Ensure we don't exceed limit
            brief['meta_description'] = meta

        return brief

    def _fix_heading_hierarchy(self, sections: List[Dict]) -> List[Dict]:
        """Ensure proper H1→H2→H3 progression.

        Args:
            sections: List of section outlines

        Returns:
            Fixed sections with proper hierarchy
        """
        if not sections:
            return sections

        fixed_sections = []
        prev_level = 1  # H1 is the title

        for section in sections:
            current_level = section.get('level', 2)

            # Can't skip levels (e.g., H1 → H3)
            if current_level > prev_level + 1:
                section['level'] = prev_level + 1
                print(f"  ⚠️  Fixed heading level: '{section['heading']}' → H{section['level']}")

            fixed_sections.append(section)
            prev_level = section['level']

        return fixed_sections

    # ========================================================================
    # STEP 3: Section Writing
    # ========================================================================

    def write_section(
        self,
        section_outline: Dict,
        brief: ContentBrief,
        previous_sections: List[str] = None
    ) -> ArticleSection:
        """Write a single section of the article.

        This is where the actual content gets created. We write one section
        at a time to maintain quality and coherence.

        Args:
            section_outline: Outline for this specific section
            brief: Overall content brief
            previous_sections: Previously written sections for context

        Returns:
            ArticleSection with written content
        """
        print(f"  ✍️  Writing: {section_outline['heading']}")

        # Build context from previous sections
        context = ""
        if previous_sections:
            context = "\n\n".join(previous_sections[-2:])  # Last 2 sections for context

        # Build section writing prompt
        target_words = section_outline['target_word_count']
        keyword = brief['primary_keyword']
        target_keyword_count = max(2, target_words // 200)  # 1 keyword per ~200 words

        section_prompt = f"""Write the following section for a blog post.

SECTION HEADING: {section_outline['heading']}
HEADING LEVEL: H{section_outline['level']}

STRICT WORD COUNT: Write EXACTLY {target_words} words (±20 words maximum).
Stop writing immediately when you reach {target_words} words.

PRIMARY KEYWORD: "{keyword}"
KEYWORD REQUIREMENT: Include "{keyword}" {target_keyword_count}-{target_keyword_count + 1} times naturally in this section.
- Use keyword in first or second sentence
- Include natural variations of the keyword
- Make it sound natural, never forced

SECONDARY KEYWORDS: {', '.join(brief['secondary_keywords'])}

KEY POINTS TO COVER:
{chr(10).join(f"- {point}" for point in section_outline.get('key_points', []))}

PREVIOUS CONTEXT (for continuity):
{context if context else "This is the first section."}

REQUIREMENTS:
- Write in brand voice: direct, conversational, simple and accessible
- Use 8th-9th grade reading level (simple words, short sentences)
- Keep sentences under 20 words each
- Use short paragraphs (2-3 sentences maximum)
- Include specific, relatable examples
- Explain any technical terms immediately in plain English
- Write EXACTLY {target_words} words - count carefully and stop at the limit

Write the section content now. Only the body text, no heading.
"""

        try:
            # Generate section content
            content = self._generate_with_llm(
                prompt=section_prompt,
                system_prompt=self.system_prompt,
                temperature=0.7
            )

            # Clean up content
            content = content.strip()
            word_count = len(content.split())

            # Validate keyword usage
            keyword_count = content.lower().count(brief['primary_keyword'].lower())
            if keyword_count < target_keyword_count:
                print(f"    ⚠️  Low keyword density: {keyword_count}/{target_keyword_count} occurrences")

            section = ArticleSection(
                heading=section_outline['heading'],
                level=section_outline['level'],
                content=content,
                word_count=word_count
            )

            print(f"    ✓ Wrote {word_count} words (target: {target_words})")
            return section

        except Exception as e:
            print(f"    ✗ Error writing section: {str(e)}")
            raise

    # ========================================================================
    # STEP 4: Introduction & Conclusion
    # ========================================================================

    def write_introduction(self, brief: ContentBrief, outline: List[Dict]) -> str:
        """Write engaging introduction.

        The intro needs to:
        - Hook the reader immediately
        - Set expectations for what they'll learn
        - Include primary keyword naturally
        - Match brand voice

        Args:
            brief: Content brief
            outline: Article outline for context

        Returns:
            Introduction text
        """
        print("  ✍️  Writing introduction...")

        brand_examples = self.get_brand_voice_examples(
            topic=brief['primary_keyword'],
            content_type="blog_post_intro",
            n_examples=2
        )

        intro_prompt = f"""Write an engaging introduction for this blog post.

TOPIC: {brief['primary_keyword']}
META TITLE: {brief['meta_title']}
SEARCH INTENT: {brief['search_intent']}

THE ARTICLE WILL COVER:
{chr(10).join(f"- {section['heading']}" for section in outline)}

BRAND VOICE EXAMPLES (match this style):
{brand_examples if brand_examples else "Direct, educational, accessible. Example: 'Skin is a complex organ. Your skincare doesn't have to be.'"}

REQUIREMENTS:
- Start with a strong, direct opening sentence (under 15 words)
- Use simple, conversational language (8th grade reading level)
- Include primary keyword "{brief['primary_keyword']}" 2-3 times naturally
- Keep sentences under 20 words
- 3-4 short paragraphs (2-3 sentences each)
- Write EXACTLY 150-200 words
- End with a smooth transition to main content

Write the introduction now.
"""

        intro = self._generate_with_llm(
            prompt=intro_prompt,
            system_prompt=self.system_prompt,
            temperature=0.7
        )

        print(f"    ✓ Wrote introduction ({len(intro.split())} words)")
        return intro.strip()

    def write_conclusion(
        self,
        brief: ContentBrief,
        sections: List[ArticleSection]
    ) -> str:
        """Write conclusion that summarizes key points.

        Args:
            brief: Content brief
            sections: All written sections for context

        Returns:
            Conclusion text
        """
        print("  ✍️  Writing conclusion...")

        # Summarize key points from sections
        key_points = "\n".join([
            f"- {section.heading}: {section.content[:100]}..."
            for section in sections[:5]  # First 5 sections
        ])

        conclusion_prompt = f"""Write a conclusion for this blog post.

TOPIC: {brief['primary_keyword']}

KEY POINTS COVERED:
{key_points}

REQUIREMENTS:
- Summarize the main takeaway in simple terms
- Include primary keyword "{brief['primary_keyword']}" once naturally
- Use simple language (8th grade level)
- Keep sentences under 20 words
- Be actionable (what should reader do next?)
- 2-3 short paragraphs (2-3 sentences each)
- Write EXACTLY 100-150 words
- Don't introduce new information
- Match brand voice: direct, helpful, conversational

Write the conclusion now.
"""

        conclusion = self._generate_with_llm(
            prompt=conclusion_prompt,
            system_prompt=self.system_prompt,
            temperature=0.7
        )

        print(f"    ✓ Wrote conclusion ({len(conclusion.split())} words)")
        return conclusion.strip()

    # ========================================================================
    # STEP 5: Call-to-Action (CTA)
    # ========================================================================

    def generate_cta(self, brief: ContentBrief) -> str:
        """Generate relevant call-to-action.

        CTAs should:
        - Be relevant to the content
        - Not be pushy or salesy
        - Provide clear next step
        - Match brand voice

        Args:
            brief: Content brief

        Returns:
            CTA text
        """
        cta_prompt = f"""Generate a subtle, helpful call-to-action for this blog post.

TOPIC: {brief['primary_keyword']}
BRAND: Clean, science-backed skincare

REQUIREMENTS:
- Helpful, not pushy
- Relevant to the content
- 1-2 sentences max
- Examples:
  * "Ready to simplify your routine? Browse our essentials."
  * "Want personalized recommendations? Take our skin quiz."
  * "Questions? Our team is here to help."

Write the CTA now.
"""

        cta = self._generate_with_llm(
            prompt=cta_prompt,
            system_prompt=self.system_prompt,
            temperature=0.8
        )

        return cta.strip()

    # ========================================================================
    # STEP 6: Content Assembly
    # ========================================================================

    def assemble_article(
        self,
        brief: ContentBrief,
        introduction: str,
        sections: List[ArticleSection],
        conclusion: str,
        cta: str
    ) -> Article:
        """Assemble all components into final article.

        This combines everything into the final Article object with both
        Markdown and HTML versions.

        Args:
            brief: Content brief
            introduction: Written introduction
            sections: All written sections
            conclusion: Written conclusion
            cta: Call-to-action

        Returns:
            Complete Article object
        """
        print("\n📦 Assembling final article...")

        # Calculate total word count
        total_words = (
            len(introduction.split()) +
            sum(section.word_count for section in sections) +
            len(conclusion.split())
        )

        # Build Markdown version
        markdown_parts = [
            f"# {brief['meta_title']}\n",
            introduction,
            ""
        ]

        for section in sections:
            heading_marker = "#" * (section.level + 1)  # +1 because title is H1
            markdown_parts.append(f"{heading_marker} {section.heading}\n")
            markdown_parts.append(section.content)
            markdown_parts.append("")

        markdown_parts.append(conclusion)
        markdown_parts.append("")
        markdown_parts.append(f"---\n\n{cta}")

        markdown_content = "\n".join(markdown_parts)

        # Create article object
        article = Article(
            title=brief['meta_title'],
            meta_description=brief['meta_description'],
            introduction=introduction,
            sections=sections,
            conclusion=conclusion,
            call_to_action=cta,
            total_word_count=total_words,
            markdown_content=markdown_content,
            html_content=None  # We'll add HTML conversion later if needed
        )

        print(f"✓ Article assembled: {total_words} words total")
        return article

    # ========================================================================
    # STEP 7: SEO Optimization
    # ========================================================================

    def optimize_for_seo(
        self,
        article: Article,
        brief: ContentBrief
    ) -> Article:
        """Ensure content is SEO-optimized.

        Checks:
        - Keyword density (1-2%)
        - Keyword in title, intro, conclusion
        - Proper heading hierarchy
        - Internal linking opportunities

        Args:
            article: Generated article
            brief: Content brief with keywords

        Returns:
            Optimized article
        """
        print("\n🔍 Optimizing for SEO...")

        full_text = f"{article.introduction} {' '.join(s.content for s in article.sections)} {article.conclusion}"
        full_text_lower = full_text.lower()

        # Check keyword density
        primary_keyword = brief['primary_keyword'].lower()
        keyword_count = full_text_lower.count(primary_keyword)
        keyword_density = (keyword_count / article.total_word_count) * 100

        print(f"  • Primary keyword '{primary_keyword}': {keyword_count} times ({keyword_density:.2f}%)")

        # Check keyword in key places
        has_in_title = primary_keyword in article.title.lower()
        has_in_intro = primary_keyword in article.introduction.lower()
        has_in_conclusion = primary_keyword in article.conclusion.lower()

        print(f"  • Keyword in title: {'✓' if has_in_title else '✗'}")
        print(f"  • Keyword in intro: {'✓' if has_in_intro else '✗'}")
        print(f"  • Keyword in conclusion: {'✓' if has_in_conclusion else '✗'}")

        # Check heading hierarchy
        heading_levels = [section.level for section in article.sections]
        proper_hierarchy = all(
            heading_levels[i] <= heading_levels[i+1] + 1
            for i in range(len(heading_levels) - 1)
        )
        print(f"  • Heading hierarchy: {'✓' if proper_hierarchy else '⚠️  check manually'}")

        # If SEO needs improvement, we'd rewrite sections here
        # For now, we'll just report

        print("✓ SEO optimization check complete")
        return article

    # ========================================================================
    # STEP 8: Full Workflow Orchestration
    # ========================================================================

    def generate_article(self, brief: ContentBrief) -> Article:
        """Generate a complete article from a content brief.

        This orchestrates the entire content generation workflow:
        1. Generate outline
        2. Write introduction
        3. Write all sections
        4. Write conclusion
        5. Generate CTA
        6. Assemble article
        7. Optimize for SEO

        Args:
            brief: Content brief with topic, keywords, etc.

        Returns:
            Complete, SEO-optimized article
        """
        print(f"\n{'='*60}")
        print(f"🚀 Starting content generation for: {brief['primary_keyword']}")
        print(f"{'='*60}")

        # Step 1: Generate outline
        outline = self.generate_outline(brief)

        # Step 2: Write introduction
        introduction = self.write_introduction(brief, outline)

        # Step 3: Write all sections
        print("\n📝 Writing article sections...")
        sections = []
        previous_content = []

        for section_outline in outline:
            section = self.write_section(
                section_outline=section_outline,
                brief=brief,
                previous_sections=previous_content
            )
            sections.append(section)
            previous_content.append(section.content)

        # Step 4: Write conclusion
        conclusion = self.write_conclusion(brief, sections)

        # Step 5: Generate CTA
        cta = self.generate_cta(brief)

        # Step 6: Assemble article
        article = self.assemble_article(
            brief=brief,
            introduction=introduction,
            sections=sections,
            conclusion=conclusion,
            cta=cta
        )

        # Step 7: Optimize for SEO
        article = self.optimize_for_seo(article, brief)

        print(f"\n{'='*60}")
        print("✅ Article generation complete!")
        print(f"   • Total words: {article.total_word_count}")
        print(f"   • Sections: {len(article.sections)}")
        print(f"{'='*60}\n")

        return article
