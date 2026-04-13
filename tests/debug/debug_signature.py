"""Debug Polymarket signature methods"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import hmac
import hashlib
import json
import base64
from datetime import datetime
from src.config import get_settings

settings = get_settings()

api_key = settings.polymarket_api_key
api_secret = settings.polymarket_api_secret
api_passphrase = settings.polymarket_api_passphrase

print("\n" + "="*100)
print("SIGNATURE DEBUGGING")
print("="*100)

print(f"\nAPI Key: {api_key}")
print(f"API Secret (raw): {api_secret}")
print(f"API Passphrase: {api_passphrase}")

# Test data
timestamp = str(int(datetime.now().timestamp() * 1000))
method = "POST"
path = "/orders"
data = {"market_id": "0x123", "side": "BUY", "price": 0.50, "size": 100}
body = json.dumps(data, sort_keys=True)

print(f"\nTest Message Components:")
print(f"  Timestamp: {timestamp}")
print(f"  Method: {method}")
print(f"  Path: {path}")
print(f"  Body: {body[:60]}...")

message = timestamp + method + path + body
print(f"\nFull Message: {message[:100]}...")

# METHOD 1: Using raw api_secret as hex (current)
print("\n" + "-"*100)
print("METHOD 1: Raw api_secret (current)")
print("-"*100)
sig1 = hmac.new(
    api_secret.encode(),
    message.encode(),
    hashlib.sha256,
).hexdigest()
print(f"Hex: {sig1[:40]}...")

sig1_b64 = base64.b64encode(
    hmac.new(
        api_secret.encode(),
        message.encode(),
        hashlib.sha256,
    ).digest()
).decode('utf-8')
print(f"Base64: {sig1_b64[:40]}...")

# METHOD 2: Decode api_secret from base64 first
print("\n" + "-"*100)
print("METHOD 2: Decode api_secret from base64 first")
print("-"*100)
try:
    api_secret_decoded = base64.b64decode(api_secret)
    print(f"Decoded secret: {api_secret_decoded.hex()[:40]}...")

    sig2_hex = hmac.new(
        api_secret_decoded,
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    print(f"Signature (hex): {sig2_hex[:40]}...")

    sig2_b64 = base64.b64encode(
        hmac.new(
            api_secret_decoded,
            message.encode(),
            hashlib.sha256,
        ).digest()
    ).decode('utf-8')
    print(f"Signature (base64): {sig2_b64[:40]}...")
except Exception as e:
    print(f"Failed: {e}")

# METHOD 3: Include passphrase in signature
print("\n" + "-"*100)
print("METHOD 3: Include passphrase in message")
print("-"*100)
message_with_passphrase = timestamp + method + path + body + api_passphrase
sig3 = hmac.new(
    api_secret.encode(),
    message_with_passphrase.encode(),
    hashlib.sha256,
).hexdigest()
print(f"Signature (hex): {sig3[:40]}...")

# METHOD 4: Use passphrase as secret
print("\n" + "-"*100)
print("METHOD 4: Use passphrase as signing secret")
print("-"*100)
sig4 = hmac.new(
    api_passphrase.encode(),
    message.encode(),
    hashlib.sha256,
).hexdigest()
print(f"Signature (hex): {sig4[:40]}...")

# METHOD 5: Try SHA1 instead of SHA256
print("\n" + "-"*100)
print("METHOD 5: SHA1 instead of SHA256")
print("-"*100)
sig5 = hmac.new(
    api_secret.encode(),
    message.encode(),
    hashlib.sha1,
).hexdigest()
print(f"Signature (hex): {sig5[:40]}...")

# METHOD 6: Check if body should be sorted differently
print("\n" + "-"*100)
print("METHOD 6: Different body formats")
print("-"*100)
body_raw = json.dumps(data)
body_no_spaces = json.dumps(data, separators=(',', ':'))

print(f"Body (normal): {body_raw}")
print(f"Body (compact): {body_no_spaces}")

sig6a = hmac.new(
    api_secret.encode(),
    (timestamp + method + path + body_raw).encode(),
    hashlib.sha256,
).hexdigest()
print(f"Signature with normal body: {sig6a[:40]}...")

sig6b = hmac.new(
    api_secret.encode(),
    (timestamp + method + path + body_no_spaces).encode(),
    hashlib.sha256,
).hexdigest()
print(f"Signature with compact body: {sig6b[:40]}...")

print("\n" + "="*100)
print("RECOMMENDATION:")
print("="*100)
print("""
Try in this order:
1. METHOD 2 (decode api_secret from base64) - Most likely for crypto exchange APIs
2. METHOD 4 (use passphrase as secret) - Passphrase often replaces secret
3. METHOD 6 (compact JSON body) - Body formatting matters
4. Add POLY-PASSPHRASE header if not already included

Also check Polymarket docs for:
- Exact message format (should have timestamp + method + path + body?)
- Whether signature should be hex or base64
- Whether all headers are included (POLY-API-KEY, POLY-NONCE, POLY-SIGNATURE, POLY-PASSPHRASE?)
""")
