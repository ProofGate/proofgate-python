"""
ProofGate Signer Service Example (Python)

A secure microservice that sits between your LLM and the blockchain.
The LLM never has access to the private key.

Architecture:
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
"""

import os
from flask import Flask, request, jsonify
from web3 import Web3
from eth_account import Account
from proofgate import ProofGate

# ============================================
# CONFIGURATION
# ============================================

PORT = int(os.environ.get("PORT", 3000))
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
PROOFGATE_API_KEY = os.environ.get("PROOFGATE_API_KEY")
RPC_URL = os.environ.get("RPC_URL", "https://mainnet.base.org")

if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY environment variable required")

if not PROOFGATE_API_KEY:
    raise ValueError("PROOFGATE_API_KEY environment variable required")

# ============================================
# SETUP
# ============================================

# Initialize ProofGate client
proofgate = ProofGate(api_key=PROOFGATE_API_KEY, chain_id=8453)

# Initialize Web3 and account (private key ONLY here, not in LLM)
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = Account.from_key(PRIVATE_KEY)

app = Flask(__name__)

# ============================================
# ENDPOINTS
# ============================================

@app.route("/execute", methods=["POST"])
def execute():
    """
    Receives a transaction request from the LLM,
    validates it via ProofGate, and executes if safe.
    """
    data = request.json
    to_address = data.get("to")
    tx_data = data.get("data", "0x")
    value = data.get("value", "0")
    guardrail_id = data.get("guardrailId")

    print(f"Transaction request received")
    print(f"  To: {to_address}")
    print(f"  Value: {value}")
    print(f"  Data: {tx_data[:20]}...")

    try:
        # ========================================
        # STEP 1: Validate with ProofGate
        # ========================================
        print("  → Validating with ProofGate...")
        
        validation = proofgate.validate(
            from_address=account.address,
            to=to_address,
            data=tx_data,
            value=value,
            guardrail_id=guardrail_id,
        )

        print(f"  → Validation result: {validation.result}")

        # ========================================
        # STEP 2: Reject if unsafe
        # ========================================
        if not validation.safe:
            print(f"  ✗ Transaction BLOCKED: {validation.reason}")
            return jsonify({
                "success": False,
                "error": f"Transaction blocked by ProofGate: {validation.reason}",
                "validation": {
                    "result": validation.result,
                    "reason": validation.reason,
                    "checks": validation.checks,
                },
            }), 400

        # ========================================
        # STEP 3: Sign and execute if safe
        # ========================================
        print("  → Transaction validated, signing and executing...")

        # Build transaction
        tx = {
            "to": Web3.to_checksum_address(to_address),
            "data": tx_data,
            "value": w3.to_wei(value, "ether") if value != "0" else 0,
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(account.address),
            "chainId": 8453,
        }

        # Sign and send
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash_hex = tx_hash.hex()

        print(f"  ✓ Transaction sent: {tx_hash_hex}")

        return jsonify({
            "success": True,
            "txHash": tx_hash_hex,
            "validation": {
                "result": validation.result,
                "reason": validation.reason,
                "checks": validation.checks,
            },
        })

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@app.route("/address", methods=["GET"])
def get_address():
    """
    Returns the wallet address (so LLM can use it in transactions).
    Does NOT expose the private key.
    """
    return jsonify({"address": account.address})


@app.route("/health", methods=["GET"])
def health():
    """Health check."""
    return jsonify({
        "status": "healthy",
        "address": account.address,
        "chain": "base",
    })


# ============================================
# START SERVER
# ============================================

if __name__ == "__main__":
    print(f"\n🔐 ProofGate Signer Service (Python)")
    print(f"   Wallet: {account.address}")
    print(f"   Chain:  Base (8453)")
    print(f"   Port:   {PORT}")
    print(f"\n   The LLM can call /execute without ever seeing the private key.\n")
    
    app.run(host="0.0.0.0", port=PORT)
