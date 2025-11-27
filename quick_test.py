#!/usr/bin/env python3
"""Quick test for Research Agent"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.ai_content_factory.agents.research_agent import AdvancedResearchAgent
    agent = AdvancedResearchAgent()
    print("✅ Research Agent loaded successfully!")
    print("🎉 You're good to continue!")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()