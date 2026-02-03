# proofgate

> Blockchain guardrails for AI agents. Validate transactions before execution.

[![PyPI version](https://badge.fury.io/py/proofgate.svg)](https://pypi.org/project/proofgate/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is ProofGate?

ProofGate validates blockchain transactions before your AI agent executes them. It prevents:

- 🚫 **Wallet drains** from prompt injection attacks
- 🚫 **Infinite approvals** to malicious contracts  
- 🚫 **Excessive spending** beyond daily limits
- 🚫 **High slippage** swaps that lose money

## Installation

```bash
pip install proofgate
```

## Quick Start

### Synchronous Usage

```python
from proofgate import ProofGate

# Initialize client
pg = ProofGate(api_key="pg_your_api_key")  # Get from proofgate.xyz/dashboard

# Validate before sending
result = pg.validate(
    from_address="0xYourAgentWallet",
    to="0xContractAddress",
    data="0xa9059cbb...",  # Transaction calldata
    value="0",
)

if result.safe:
    # ✅ Execute the transaction
    wallet.send_transaction(to=to, data=data, value=value)
else:
    # 🚫 Transaction blocked
    print(f"Blocked: {result.reason}")
```

### Async Usage

```python
from proofgate import AsyncProofGate

async def main():
    async with AsyncProofGate(api_key="pg_your_api_key") as pg:
        result = await pg.validate(
            from_address="0xYourAgentWallet",
            to="0xContractAddress",
            data="0xa9059cbb...",
        )
        
        if result.safe:
            # Execute transaction
            pass
```

## API Reference

### `ProofGate(config)` / `AsyncProofGate(config)`

Create a new ProofGate client.

```python
pg = ProofGate(
    api_key="pg_xxx",           # Required: Your API key
    chain_id=56,                 # Optional: Default chain (56 = BSC)
    guardrail_id="xxx",          # Optional: Default guardrail
    base_url="https://...",      # Optional: Custom API URL
    timeout=30.0,                # Optional: Request timeout (seconds)
)
```

### `pg.validate(request)`

Validate a transaction.

```python
result = pg.validate(
    from_address="0xAgent...",
    to="0xContract...",
    data="0x...",
    value="0",           # Optional
    guardrail_id="xxx",  # Optional: Override default
    chain_id=56,         # Optional: Override default
)

# Returns ValidateResponse with:
# - validation_id: str
# - result: "PASS" | "FAIL" | "PENDING"
# - reason: str
# - safe: bool
# - checks: List[ValidationCheck]
# - authenticated: bool
# - evidence_uri: str
```

### `pg.validate_or_throw(request)`

Validate and raise exception if unsafe.

```python
from proofgate import ProofGateError

try:
    pg.validate_or_throw(
        from_address=from_addr,
        to=to_addr,
        data=calldata,
    )
    # Safe to execute
except ProofGateError as e:
    print(f"Blocked: {e.message}")
```

### `pg.check_agent(wallet)`

Check an agent's trust score.

```python
agent = pg.check_agent("0x123...")

print(agent.trust_score)         # 85
print(agent.tier)                # "gold"
print(agent.verification_status) # "verified"
```

### `pg.get_evidence(validation_id)`

Get evidence for a past validation.

```python
evidence = pg.get_evidence("val_abc123")
print(evidence.transaction)
print(evidence.result)
```

## Guardrails

Guardrails define what your agent can do. Create them at [proofgate.xyz/guardrails](https://www.proofgate.xyz/guardrails).

Example guardrail rules:
- **Whitelist contracts**: Only Uniswap, Aave, Compound
- **Max approval**: 1,000 USDC per approval
- **Max slippage**: 1% on swaps
- **Daily limit**: $10,000 total spending

## Error Handling

```python
from proofgate import ProofGate, ProofGateError

try:
    pg.validate(from_address=from_addr, to=to_addr, data=calldata)
except ProofGateError as e:
    print(f"Code: {e.code}")          # "VALIDATION_FAILED"
    print(f"Message: {e.message}")    # "Infinite approval detected"
    print(f"Result: {e.validation_result}")
```

Error codes:
- `MISSING_API_KEY` - No API key provided
- `INVALID_API_KEY` - Key doesn't start with `pg_`
- `VALIDATION_FAILED` - Transaction failed validation
- `API_ERROR` - API returned an error
- `NETWORK_ERROR` - Network request failed
- `TIMEOUT` - Request timed out

## Type Hints

Full type hints included:

```python
from proofgate import (
    ProofGateConfig,
    ValidateRequest,
    ValidateResponse,
    ValidationCheck,
    AgentCheckResponse,
    EvidenceResponse,
)
```

## Get Your API Key

1. Go to [proofgate.xyz](https://www.proofgate.xyz)
2. Connect your wallet
3. Register your AI agent
4. Copy your API key (starts with `pg_`)

**Free tier:** 100 validations/month

## Links

- **Website:** [proofgate.xyz](https://www.proofgate.xyz)
- **Documentation:** [proofgate.xyz/docs](https://www.proofgate.xyz/docs)
- **Dashboard:** [proofgate.xyz/dashboard](https://www.proofgate.xyz/dashboard)
- **GitHub:** [github.com/ProofGate/proofgate-python](https://github.com/ProofGate/proofgate-python)

## License

MIT © [0xCR6](https://twitter.com/0xCR6)
