"""
ProofGate SDK

Blockchain guardrails for AI agents. Validate transactions
before execution to prevent wallet drains, infinite approvals,
and other security risks.

Example:
    >>> from proofgate import ProofGate
    >>> 
    >>> pg = ProofGate(api_key="pg_your_key")
    >>> 
    >>> result = await pg.validate(
    ...     from_address="0xAgent...",
    ...     to="0xContract...",
    ...     data="0xa9059cbb...",
    ... )
    >>> 
    >>> if result.safe:
    ...     # Execute transaction
    ...     pass
    ... else:
    ...     print(f"Blocked: {result.reason}")
"""

from proofgate.client import ProofGate, AsyncProofGate
from proofgate.types import (
    ProofGateConfig,
    ValidateRequest,
    ValidateResponse,
    ValidationCheck,
    AgentCheckResponse,
    EvidenceResponse,
    UsageResponse,
)
from proofgate.exceptions import ProofGateError

__all__ = [
    "ProofGate",
    "AsyncProofGate",
    "ProofGateConfig",
    "ValidateRequest",
    "ValidateResponse",
    "ValidationCheck",
    "AgentCheckResponse",
    "EvidenceResponse",
    "UsageResponse",
    "ProofGateError",
]

__version__ = "0.1.0"
