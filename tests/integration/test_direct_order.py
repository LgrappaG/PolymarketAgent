"""Direct order placement test"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.execution.polymarket_connector import PolymarketConnector
from src.config import get_settings

async def test_order_placement():
    """Test order placement directly"""

    print("\n[*] Testing direct order placement...\n")

    settings = get_settings()

    connector = PolymarketConnector(
        api_key=settings.polymarket_api_key,
        api_secret=settings.polymarket_api_secret,
        api_passphrase=settings.polymarket_api_passphrase,
    )
    await connector.initialize()

    # Test 1: Get markets
    print("[1] Fetching markets...")
    markets = await connector.get_markets()
    print(f"    Markets type: {type(markets)}")
    print(f"    Markets length: {len(markets) if isinstance(markets, (list, dict)) else 'N/A'}")

    if isinstance(markets, dict):
        print(f"    Markets is dict - keys: {markets.keys()}")
        # Extract from dict
        if "data" in markets:
            markets = markets["data"]
        elif "markets" in markets:
            markets = markets["markets"]

    print(f"    After extraction - type: {type(markets)}, len: {len(markets) if isinstance(markets, list) else 'N/A'}")

    if isinstance(markets, list) and len(markets) > 0:
        m = markets[0]
        print(f"    First market: {m.get('name')}")
        print(f"    Market ID: {m.get('id')}")
        market_id = m.get('id')
    else:
        print("    No markets available!")
        return

    # Test 2: Place order
    print("\n[2] Placing test order...")
    order = await connector.place_order(
        market_id=market_id,
        side="BUY",
        price=0.50,
        size=100,
        order_type="LIMIT"
    )

    if order:
        print(f"    [+] Order placed!")
        print(f"        ID: {order.get('id')}")
        print(f"        Status: {order.get('status')}")
        print(f"        Source: {order.get('source', 'real')}")
    else:
        print(f"    [X] Order failed (returned None)")

    await connector.cleanup()

if __name__ == "__main__":
    asyncio.run(test_order_placement())
