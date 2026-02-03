"""Type definitions for ProofGate SDK."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class ProofGateConfig(BaseModel):
    """Configuration for ProofGate client."""
    
    api_key: str = Field(..., description="API key from ProofGate dashboard (starts with pg_)")
    base_url: str = Field(
        default="https://www.proofgate.xyz/api",
        description="Base URL for API"
    )
    chain_id: int = Field(default=8453, description="Default chain ID (8453 = Base)")
    guardrail_id: Optional[str] = Field(
        default=None,
        description="Default guardrail ID to use for validations"
    )
    timeout: float = Field(default=30.0, description="Request timeout in seconds")


class ValidateRequest(BaseModel):
    """Request for transaction validation."""
    
    from_address: str = Field(..., alias="from", description="Sender address (your agent's wallet)")
    to: str = Field(..., description="Target contract address")
    data: str = Field(..., description="Transaction calldata")
    value: str = Field(default="0", description="Value in wei")
    guardrail_id: Optional[str] = Field(default=None, description="Guardrail ID (overrides default)")
    chain_id: Optional[int] = Field(default=None, description="Chain ID (overrides default)")

    class Config:
        populate_by_name = True


class ValidationCheck(BaseModel):
    """Individual check result from validation."""
    
    name: str = Field(..., description="Check name (e.g., 'allowed_contracts', 'daily_limit')")
    passed: bool = Field(..., description="Did this check pass?")
    details: str = Field(..., description="Human-readable details")
    severity: Literal["info", "warning", "critical"] = Field(
        ..., description="Severity level"
    )


class ValidateResponse(BaseModel):
    """Response from transaction validation."""
    
    validation_id: str = Field(..., alias="validationId", description="Unique validation ID")
    result: Literal["PASS", "FAIL", "PENDING"] = Field(..., description="Validation result")
    reason: str = Field(..., description="Human-readable reason")
    evidence_uri: str = Field(..., alias="evidenceUri", description="Evidence URI")
    safe: bool = Field(..., description="Is the transaction safe to execute?")
    checks: List[ValidationCheck] = Field(default_factory=list, description="Detailed check results")
    chain_id: int = Field(..., alias="chainId", description="Chain ID validated on")
    authenticated: bool = Field(default=False, description="Was API key authenticated?")
    tier: str = Field(default="free", description="User tier (free/pro)")
    backend: str = Field(default="local", description="Backend used (local/evidence-service)")
    on_chain_recorded: bool = Field(
        default=False, alias="onChainRecorded", description="Was proof recorded on-chain?"
    )

    class Config:
        populate_by_name = True


class AgentStats(BaseModel):
    """Validation statistics for an agent."""
    
    total_validations: int = Field(..., alias="totalValidations")
    passed_validations: int = Field(..., alias="passedValidations")
    failed_validations: int = Field(..., alias="failedValidations")
    pass_rate: float = Field(..., alias="passRate")

    class Config:
        populate_by_name = True


class AgentRegistration(BaseModel):
    """Registration info for an agent."""
    
    name: Optional[str] = None
    registered_at: str = Field(..., alias="registeredAt")

    class Config:
        populate_by_name = True


class AgentCheckResponse(BaseModel):
    """Response from agent check."""
    
    wallet: str = Field(..., description="Wallet address (lowercase)")
    is_registered: bool = Field(..., alias="isRegistered", description="Is this agent registered?")
    verification_status: Literal["verified", "registered", "unverified", "unknown"] = Field(
        ..., alias="verificationStatus", description="Verification status"
    )
    verification_message: str = Field(..., alias="verificationMessage", description="Human-readable message")
    trust_score: int = Field(..., alias="trustScore", description="Trust score (0-100)")
    tier: Literal["diamond", "gold", "silver", "bronze", "unverified"] = Field(
        ..., description="Trust tier"
    )
    tier_emoji: str = Field(..., alias="tierEmoji", description="Tier emoji")
    tier_name: str = Field(..., alias="tierName", description="Tier display name")
    stats: AgentStats = Field(..., description="Validation statistics")
    registration: Optional[AgentRegistration] = Field(
        default=None, description="Registration info (if registered)"
    )
    recommendation: str = Field(..., description="Safety recommendation")

    class Config:
        populate_by_name = True


class EvidenceTransaction(BaseModel):
    """Transaction details in evidence."""
    
    from_address: str = Field(..., alias="from")
    to: str
    data: str
    value: str

    class Config:
        populate_by_name = True


class EvidenceResult(BaseModel):
    """Validation result in evidence."""
    
    status: Literal["PASS", "FAIL", "PENDING"]
    reason: str
    safe: bool


class EvidenceAgent(BaseModel):
    """Agent info in evidence."""
    
    wallet: str
    name: Optional[str] = None
    verified: bool


class EvidenceProof(BaseModel):
    """Proof metadata in evidence."""
    
    authenticated: bool
    on_chain_recorded: bool = Field(..., alias="onChainRecorded")
    batch_id: Optional[str] = Field(default=None, alias="batchId")
    recorded_at: Optional[str] = Field(default=None, alias="recordedAt")

    class Config:
        populate_by_name = True


class EvidenceResponse(BaseModel):
    """Response from evidence retrieval."""
    
    validation_id: str = Field(..., alias="validationId", description="Validation ID")
    timestamp: str = Field(..., description="Timestamp")
    chain_id: int = Field(..., alias="chainId", description="Chain ID")
    transaction: EvidenceTransaction = Field(..., description="Transaction details")
    result: EvidenceResult = Field(..., description="Validation result")
    guardrail_id: Optional[str] = Field(default=None, alias="guardrailId", description="Guardrail used")
    agent: EvidenceAgent = Field(..., description="Agent info")
    proof: EvidenceProof = Field(..., description="Proof metadata")

    class Config:
        populate_by_name = True


class UsageResponse(BaseModel):
    """Response from usage check."""
    
    wallet: str
    tier: str
    validations_used: int
    validations_limit: int
    daily_spent_wei: str
