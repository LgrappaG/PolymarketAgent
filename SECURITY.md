# Security & Disclaimer

## ⚠️ CRITICAL: This is NOT Production Software

This project is **educational and testing software only**. It is **NOT suitable for production use** or handling real financial assets.

### Known Limitations

1. **Key Management:** Private keys are stored in plaintext `.env` files (acceptable for testing, NOT for production)
2. **No Audit:** Code has not undergone professional security audit
3. **No Insurance:** No liability coverage or insurance protecting users
4. **Experimental:** Claude AI decision-making is experimental and unproven for trading
5. **No Compliance:** No legal/compliance review for securities regulations
6. **Limited Testing:** Not tested under adverse market conditions or extreme volatility

### Production Deployment Would Require

If you wanted to build a real trading system similar to this:

- **Hardware Security Module (HSM)** for private key storage
- **Professional security audit** by qualified firm
- **Regulatory compliance review** (CFTC, SEC, etc.)
- **Insurance & liability coverage**
- **Institutional-grade monitoring** and alerting
- **Rate limiting & circuit breakers** for risk management
- **Formal user agreement** with risk disclaimers
- **24/7 operational support**

### Security Best Practices (For This Test Project)

- ✅ Never commit `.env.local` to version control
- ✅ Use `.env.example` as your template
- ✅ Keep `.env.local` in `.gitignore`
- ✅ Test with small amounts only if using real credentials
- ✅ Rotate API keys regularly
- ✅ Use separate API keys for testing vs. production
- ✅ Run in `PAPER` mode (simulated) for learning

### If You Find a Security Issue

Since this is educational software:

1. **Create a GitHub issue** describing the vulnerability (do not include details about how to exploit)
2. **Email the maintainer** if you prefer non-public disclosure
3. **Allow time for response** - this is not a security-focused project
4. **Do NOT publicly disclose** until maintainer has time to respond

### Do NOT Use This For

- ❌ Real financial trading with significant amounts
- ❌ Production deployment without major modifications
- ❌ Handling other people's funds or credentials
- ❌ Bypassing security features or risk controls
- ❌ Automated trading without proper regulatory compliance

### Warranty & Liability

```
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

The authors accept **no liability** for:
- Financial losses from trading
- Data breaches or credential exposure
- System failures or bugs
- Use in any production environment

Use at your own risk.

---

## Configuration Security

### Sensitive Data in `.env.local`

Never commit files containing:
- `ANTHROPIC_API_KEY` - Claude API credentials
- `PRIVATE_KEY` - Ethereum/blockchain wallet private key
- `POLYMARKET_API_KEY` - API credentials
- `NEWS_API_KEY` - Third-party API keys
- Any wallet addresses if combined with private keys

### Secure Patterns

✅ **Good:**
```bash
cp .env.example .env.local
# Edit .env.local locally (not in git)
# Use environment variables for CI/CD
```

❌ **Bad:**
```bash
git commit .env.local
git commit secrets/private_key.txt
echo "PRIVATE_KEY=0x..." in config
```

---

## Credential Rotation

For any keys committed accidentally:

1. **Immediately revoke** the key through the API provider
2. **Generate a new key**
3. **Update .env** locally
4. **Force push if in git history** (nuclear option - understand implications)
5. **Scan git history** for similar issues

```bash
# Search for potential leaks
git log --all -S "sk-ant-" --full-history
git log --all -S "0x" --full-history | grep -i "private"
```

---

## Contributing Security Advisories

If you find vulnerabilities:

- Do NOT create public issues
- Email maintainers privately first
- Include: vulnerability description, reproduction steps, proposed fix
- Allow 30 days for response
- Disclose publicly after patch is ready

---

For more details, see:
- `LICENSE` - MIT License with disclaimers
- `README.md` - "Security Notes" section
- `.env.example` - Safe environment template
