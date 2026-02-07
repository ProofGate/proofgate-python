# ProofGate Signer Service (Python)

A secure microservice that keeps your private keys **away from your LLM**.

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────┐
│   LLM / Agent   │────▶│  Signer Microservice │────▶│  Blockchain │
│  (NO priv key)  │     │  (has priv key)      │     │             │
└─────────────────┘     └──────────────────────┘     └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  ProofGate   │
                        │  Validates   │
                        └──────────────┘
```

## Setup

```bash
pip install -r requirements.txt

export PRIVATE_KEY=0x...
export PROOFGATE_API_KEY=pg_live_...

python main.py
```

## Endpoints

- `POST /execute` — Validate and execute a transaction
- `GET /address` — Get wallet address (safe to expose)
- `GET /health` — Health check

## Usage

```python
import requests

# From your LLM/agent (no private key here!)
result = requests.post("http://signer:3000/execute", json={
    "to": "0x...",
    "data": "0x...",
    "value": "0",
}).json()

if result["success"]:
    print(f"TX: {result['txHash']}")
else:
    print(f"Blocked: {result['error']}")
```

---

See [TypeScript example](https://github.com/ProofGate/proofgate-sdk/tree/main/examples/signer-service) for full documentation.
