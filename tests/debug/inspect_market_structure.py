"""Inspect actual market structure from Polymarket API"""

import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.execution.polymarket_connector import PolymarketConnector
from src.config import get_settings


async def inspect_market_structure():
    """Get and inspect actual market data structure"""

    settings = get_settings()
    connector = PolymarketConnector(
        api_key=settings.polymarket_api_key,
        api_secret=settings.polymarket_api_secret,
        api_passphrase=settings.polymarket_api_passphrase,
    )
    await connector.initialize()

    print("\n[*] Fetching markets from Polymarket API...\n")

    markets_response = await connector.get_markets(search="Biden")

    print(f"Response type: {type(markets_response)}")
    print(f"Response top-level keys (if dict): {markets_response.keys() if isinstance(markets_response, dict) else 'N/A'}\n")

    # Extract data
    if isinstance(markets_response, dict):
        markets = markets_response.get("data", [])
    else:
        markets = markets_response or []

    print(f"Total markets returned: {len(markets)}\n")

    if markets:
        print("="*100)
        print("FIRST MARKET OBJECT (Full Structure)")
        print("="*100)
        print(json.dumps(markets[0], indent=2, default=str))

        print("\n" + "="*100)
        print("SECOND AND THIRD MARKET OBJECTS")
        print("="*100)
        for idx in range(1, min(3, len(markets))):
            print(f"\nMarket[{idx}] keys: {list(markets[idx].keys()) if isinstance(markets[idx], dict) else 'Not a dict'}")
            if isinstance(markets[idx], dict):
                print(json.dumps(markets[idx], indent=2, default=str)[:500] + "...\n")

    await connector.cleanup()


if __name__ == "__main__":
    asyncio.run(inspect_market_structure())
