"""
Basic Setup Example

This example shows:
- Load configuration
- Initialize Claude agent
- Collect market data
- Generate basic analysis

Run with: python examples/basic_setup.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.agents.claude_agent import ClaudeAgent
from src.data.datastore import DataStore


def main():
    """Run basic setup example."""

    print("=" * 60)
    print("PolymarketAgent - Basic Setup Example")
    print("=" * 60)

    # 1. Load Configuration
    print("\n1. Loading configuration...")
    try:
        settings = Settings()
        print(f"   ✓ Configuration loaded")
        print(f"   - Mode: {settings.execution_mode}")
        print(f"   - Initial balance: ${settings.initial_balance}")
        print(f"   - Position size limit: {settings.max_position_size * 100}%")
    except Exception as e:
        print(f"   ✗ Error loading configuration: {e}")
        print("   → Make sure .env.local exists (copy from .env.example)")
        return

    # 2. Initialize Claude Agent
    print("\n2. Initializing Claude agent...")
    try:
        agent = ClaudeAgent(settings=settings)
        print(f"   ✓ Agent initialized")
        print(f"   - Claude model available")
    except Exception as e:
        print(f"   ✗ Error initializing agent: {e}")
        print("   → Make sure ANTHROPIC_API_KEY is set in .env.local")
        return

    # 3. Initialize Data Store
    print("\n3. Initializing data collectors...")
    try:
        datastore = DataStore(newsapi_key=settings.news_api_key or "demo")
        print(f"   ✓ Data store initialized")
        print(f"   - Available collectors: polls, sports, crypto, news")
    except Exception as e:
        print(f"   ✗ Error initializing datastore: {e}")
        return

    # 4. Show System Status
    print("\n4. System Status: ✓ Ready")
    print("\n" + "-" * 60)
    print("Next steps:")
    print("- Run: python examples/custom_strategy.py")
    print("- Run: python examples/data_collection_example.py")
    print("- See: tests/demos/demo.py for more examples")
    print("-" * 60)

    print("\n✅ Basic setup complete!")
    print("\nTo use the agent:")
    print("  from src.agents.claude_agent import ClaudeAgent")
    print("  from src.config import Settings")
    print("")
    print("  settings = Settings()")
    print("  agent = ClaudeAgent(settings=settings)")
    print("  result = agent.analyze_market(...)")


if __name__ == "__main__":
    main()
