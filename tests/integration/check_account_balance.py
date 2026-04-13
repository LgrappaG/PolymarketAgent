"""Check Polymarket account balance and status"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.execution.polymarket_connector import PolymarketConnector
from src.config import get_settings


async def check_account():
    """Check account balance and status"""

    settings = get_settings()
    connector = PolymarketConnector(
        api_key=settings.polymarket_api_key,
        api_secret=settings.polymarket_api_secret,
        api_passphrase=settings.polymarket_api_passphrase,
    )
    await connector.initialize()

    print("\n" + "="*100)
    print("POLYMARKET ACCOUNT STATUS")
    print("="*100 + "\n")

    print(f"Wallet Address: {settings.wallet_address}")
    print(f"API Key: {settings.polymarket_api_key}")
    print(f"Polygon RPC: {settings.polygon_rpc_url}\n")

    # Test 1: Get open orders (this works - means auth is partially OK)
    print("[1] Checking open orders...")
    try:
        orders = await connector.get_open_orders()
        print(f"    [+] Open orders: {len(orders)}")
        if orders:
            for o in orders[:3]:
                print(f"       - Order: {o.get('id')}, Status: {o.get('status')}")
    except Exception as e:
        print(f"    [X] Error: {e}\n")

    # Test 2: Get fills (this works - means auth is partially OK)
    print("\n[2] Checking recent fills...")
    try:
        fills = await connector.get_fills()
        print(f"    [+] Recent fills: {len(fills)}")
        if fills:
            for f in fills[:3]:
                print(f"       - Fill: {f.get('id')}, Amount: {f.get('size')}")
    except Exception as e:
        print(f"    [X] Error: {e}\n")

    print("\n" + "="*100)
    print("DIAGNOSIS")
    print("="*100 + "\n")

    print("""
POSSIBLE REASONS FOR 401 ON POST /orders:

1. [MOST LIKELY] Account has NO TRADING BALANCE
   • Polymarket account exists but no USDC deposited
   • Need to deposit funds to trading account first
   • Fix: Go to Polymarket.com → Deposit USDC

2. Account has balance but signature is wrong
   • GET requests work (we confirmed)
   • Only POST requests fail
   • Fix: Need Polymarket official API docs

3. API credentials are read-only (no trading permission)
   • Keys exist but can't place orders
   • Fix: Check Polymarket settings → API keys → enable trading

4. Trading account restricted/frozen
   • Account created but not fully activated
   • Fix: Complete KYC on Polymarket.com

NEXT STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Check Polymarket.com account:
   • Login with credentials
   • Check: Account balance, USDC available
   • Check: Trading permissions enabled

2. If no balance:
   • Deposit USDC to trading account
   • Wait for confirmation
   • Try order again

3. If signature still fails:
   • Contact Polymarket support
   • Ask for example POST /orders request with signature
   • Or use PAPER mode for testing
""")

    await connector.cleanup()


if __name__ == "__main__":
    asyncio.run(check_account())
