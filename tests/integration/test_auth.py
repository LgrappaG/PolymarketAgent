"""Test Polymarket API authentication"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.execution.polymarket_connector import PolymarketConnector
from src.config import get_settings


async def test_auth():
    """Test if credentials are valid"""

    settings = get_settings()

    print(f"\n[*] Testing Polymarket API Authentication\n")
    print(f"API Key: {settings.polymarket_api_key[:20]}...")
    print(f"API Secret: {settings.polymarket_api_secret[:20]}...")
    print(f"API Passphrase: {settings.polymarket_api_passphrase[:20]}...\n")

    connector = PolymarketConnector(
        api_key=settings.polymarket_api_key,
        api_secret=settings.polymarket_api_secret,
        api_passphrase=settings.polymarket_api_passphrase,
    )
    await connector.initialize()

    # Test 1: Get markets (public endpoint - no auth needed)
    print("[1] GET /markets (public - no auth)...")
    try:
        markets = await connector.get_markets()
        print(f"    [+] SUCCESS: Got {len(markets.get('data', [])) if isinstance(markets, dict) else len(markets)} markets\n")
    except Exception as e:
        print(f"    [X] FAILED: {e}\n")

    # Test 2: Get open orders (requires auth)
    print("[2] GET /orders/open (requires auth)...")
    try:
        orders = await connector.get_open_orders()
        print(f"    [+] SUCCESS: Got {len(orders)} open orders")
        if len(orders) > 0:
            print(f"    Order sample: {orders[0]}\n")
        else:
            print(f"    (No open orders - auth is working!)\n")
    except Exception as e:
        print(f"    [X] FAILED: {e}")
        print(f"    This likely means credentials are invalid\n")

    # Test 3: Try placing an order (will fail but shows auth signature)
    print("[3] POST /orders (requires auth + signing)...")
    try:
        order = await connector.place_order(
            market_id="0x2d5ddf657e4a090bc22921bf6865bcdb741a7b96ce45eb583be041756fad04a0",
            side="BUY",
            price=0.50,
            size=1,
            order_type="LIMIT",
        )
        if order:
            print(f"    [+] Order response: {order}\n")
        else:
            print(f"    [X] Order failed\n")
    except Exception as e:
        print(f"    [X] Error: {e}\n")

    await connector.cleanup()


if __name__ == "__main__":
    asyncio.run(test_auth())
