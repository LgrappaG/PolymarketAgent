"""Test current signature with POST order"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.execution.polymarket_connector import PolymarketConnector
from src.config import get_settings


async def test_live_order():
    """Test live order placement"""

    settings = get_settings()
    connector = PolymarketConnector(
        api_key=settings.polymarket_api_key,
        api_secret=settings.polymarket_api_secret,
        api_passphrase=settings.polymarket_api_passphrase,
    )
    await connector.initialize()

    print("\n[TEST] Attempting live order placement...\n")

    # Try to place order
    order = await connector.place_order(
        market_id="0x2d5ddf657e4a090bc22921bf6865bcdb741a7b96ce45eb583be041756fad04a0",
        side="BUY",
        price=0.50,
        size=10,
        order_type="LIMIT",
    )

    if order:
        if order.get("source") == "mock_fallback":
            print(f"[!] Got MOCK order (401 fallback)\n")
            print(f"    Order ID: {order.get('id')}")
            print(f"    Status: {order.get('status')}")
            print(f"    Source: MOCK_FALLBACK (API returned 401)\n")
            print("[*] Signature method still needs fixing.")
            print("[*] However, system works with mock orders for testing!")
        else:
            print(f"[+] REAL order placed!\n")
            print(f"    Order ID: {order.get('id')}")
            print(f"    Status: {order.get('status')}\n")
    else:
        print("[X] Order placement failed\n")

    await connector.cleanup()


if __name__ == "__main__":
    asyncio.run(test_live_order())
