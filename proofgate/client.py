"""ProofGate SDK Client implementations."""

from typing import Optional, Dict, Any
import httpx

from proofgate.types import (
    ProofGateConfig,
    ValidateRequest,
    ValidateResponse,
    AgentCheckResponse,
    EvidenceResponse,
    UsageResponse,
)
from proofgate.exceptions import ProofGateError


class AsyncProofGate:
    """Async ProofGate SDK Client.
    
    Example:
        >>> from proofgate import AsyncProofGate
        >>> 
        >>> pg = AsyncProofGate(api_key="pg_your_key")
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
    """
    
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://www.proofgate.xyz/api",
        chain_id: int = 56,
        guardrail_id: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """Initialize ProofGate client.
        
        Args:
            api_key: API key from ProofGate dashboard (starts with pg_)
            base_url: Base URL for API (default: https://www.proofgate.xyz/api)
            chain_id: Default chain ID (default: 56 for BSC)
            guardrail_id: Default guardrail ID to use for validations
            timeout: Request timeout in seconds (default: 30.0)
        """
        if not api_key:
            raise ProofGateError(
                "API key is required. Get one at https://www.proofgate.xyz/dashboard",
                "MISSING_API_KEY",
            )
        
        if not api_key.startswith("pg_"):
            raise ProofGateError(
                'Invalid API key format. Keys start with "pg_"',
                "INVALID_API_KEY",
            )
        
        self.config = ProofGateConfig(
            api_key=api_key,
            base_url=base_url,
            chain_id=chain_id,
            guardrail_id=guardrail_id,
            timeout=timeout,
        )
        
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
            },
        )
    
    async def __aenter__(self) -> "AsyncProofGate":
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self.close()
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an API request."""
        try:
            response = await self._client.request(method, path, json=json)
            data = response.json()
            
            if not response.is_success:
                raise ProofGateError(
                    data.get("error") or data.get("message") or f"HTTP {response.status_code}",
                    "API_ERROR",
                    response.status_code,
                )
            
            return data
            
        except httpx.TimeoutException:
            raise ProofGateError("Request timeout", "TIMEOUT")
        except httpx.RequestError as e:
            raise ProofGateError(str(e), "NETWORK_ERROR")
    
    async def validate(
        self,
        from_address: str,
        to: str,
        data: str,
        value: str = "0",
        guardrail_id: Optional[str] = None,
        chain_id: Optional[int] = None,
    ) -> ValidateResponse:
        """Validate a transaction before execution.
        
        Args:
            from_address: Sender address (your agent's wallet)
            to: Target contract address
            data: Transaction calldata
            value: Value in wei (default: "0")
            guardrail_id: Guardrail ID (overrides default)
            chain_id: Chain ID (overrides default)
        
        Returns:
            Validation result
        
        Example:
            >>> result = await pg.validate(
            ...     from_address="0xAgent...",
            ...     to="0xUniswap...",
            ...     data="0x38ed1739...",  # swap calldata
            ... )
            >>> 
            >>> if result.safe:
            ...     # Execute the swap
            ...     pass
            >>> else:
            ...     print(f"Blocked: {result.reason}")
        """
        response = await self._request(
            "POST",
            "/validate",
            json={
                "from": from_address,
                "to": to,
                "data": data,
                "value": value,
                "guardrailId": guardrail_id or self.config.guardrail_id,
                "chainId": chain_id or self.config.chain_id,
            },
        )
        return ValidateResponse.model_validate(response)
    
    async def validate_or_throw(
        self,
        from_address: str,
        to: str,
        data: str,
        value: str = "0",
        guardrail_id: Optional[str] = None,
        chain_id: Optional[int] = None,
    ) -> ValidateResponse:
        """Validate and throw if unsafe (convenience method).
        
        Args:
            from_address: Sender address (your agent's wallet)
            to: Target contract address
            data: Transaction calldata
            value: Value in wei (default: "0")
            guardrail_id: Guardrail ID (overrides default)
            chain_id: Chain ID (overrides default)
        
        Returns:
            Validation result (only if safe)
        
        Raises:
            ProofGateError: If validation fails
        
        Example:
            >>> try:
            ...     await pg.validate_or_throw(from_address, to, data)
            ...     # Safe to execute
            ...     await wallet.send_transaction(to=to, data=data)
            ... except ProofGateError as e:
            ...     print(f"Blocked: {e.message}")
        """
        result = await self.validate(
            from_address=from_address,
            to=to,
            data=data,
            value=value,
            guardrail_id=guardrail_id,
            chain_id=chain_id,
        )
        
        if not result.safe:
            raise ProofGateError(
                result.reason,
                "VALIDATION_FAILED",
                validation_result=result,
            )
        
        return result
    
    async def check_agent(self, wallet: str) -> AgentCheckResponse:
        """Check an agent's trust score and verification status.
        
        Args:
            wallet: Agent wallet address
        
        Returns:
            Agent verification info
        
        Example:
            >>> agent = await pg.check_agent("0x123...")
            >>> 
            >>> if agent.verification_status == "verified":
            ...     print(f"Trusted agent: {agent.tier_emoji} {agent.trust_score}/100")
            >>> else:
            ...     print("Warning: Unverified agent")
        """
        response = await self._request("GET", f"/agents/check?wallet={wallet}")
        return AgentCheckResponse.model_validate(response)
    
    async def get_evidence(self, validation_id: str) -> EvidenceResponse:
        """Get evidence for a past validation.
        
        Args:
            validation_id: Validation ID
        
        Returns:
            Evidence details
        
        Example:
            >>> evidence = await pg.get_evidence("val_abc123")
            >>> print(evidence.transaction)
            >>> print(evidence.result)
        """
        response = await self._request("GET", f"/evidence/{validation_id}")
        return EvidenceResponse.model_validate(response)
    
    async def get_usage(self, wallet: str) -> UsageResponse:
        """Get validation usage stats for a wallet.
        
        Args:
            wallet: Wallet address
        
        Returns:
            Usage statistics
        """
        response = await self._request("GET", f"/validate?wallet={wallet}")
        return UsageResponse.model_validate(response)


class ProofGate:
    """Synchronous ProofGate SDK Client.
    
    Uses httpx sync client under the hood. For async applications,
    use AsyncProofGate instead.
    
    Example:
        >>> from proofgate import ProofGate
        >>> 
        >>> pg = ProofGate(api_key="pg_your_key")
        >>> 
        >>> result = pg.validate(
        ...     from_address="0xAgent...",
        ...     to="0xContract...",
        ...     data="0xa9059cbb...",
        ... )
        >>> 
        >>> if result.safe:
        ...     # Execute transaction
        ...     pass
    """
    
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://www.proofgate.xyz/api",
        chain_id: int = 56,
        guardrail_id: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """Initialize ProofGate client.
        
        Args:
            api_key: API key from ProofGate dashboard (starts with pg_)
            base_url: Base URL for API (default: https://www.proofgate.xyz/api)
            chain_id: Default chain ID (default: 56 for BSC)
            guardrail_id: Default guardrail ID to use for validations
            timeout: Request timeout in seconds (default: 30.0)
        """
        if not api_key:
            raise ProofGateError(
                "API key is required. Get one at https://www.proofgate.xyz/dashboard",
                "MISSING_API_KEY",
            )
        
        if not api_key.startswith("pg_"):
            raise ProofGateError(
                'Invalid API key format. Keys start with "pg_"',
                "INVALID_API_KEY",
            )
        
        self.config = ProofGateConfig(
            api_key=api_key,
            base_url=base_url,
            chain_id=chain_id,
            guardrail_id=guardrail_id,
            timeout=timeout,
        )
        
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
            },
        )
    
    def __enter__(self) -> "ProofGate":
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.close()
    
    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
    
    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an API request."""
        try:
            response = self._client.request(method, path, json=json)
            data = response.json()
            
            if not response.is_success:
                raise ProofGateError(
                    data.get("error") or data.get("message") or f"HTTP {response.status_code}",
                    "API_ERROR",
                    response.status_code,
                )
            
            return data
            
        except httpx.TimeoutException:
            raise ProofGateError("Request timeout", "TIMEOUT")
        except httpx.RequestError as e:
            raise ProofGateError(str(e), "NETWORK_ERROR")
    
    def validate(
        self,
        from_address: str,
        to: str,
        data: str,
        value: str = "0",
        guardrail_id: Optional[str] = None,
        chain_id: Optional[int] = None,
    ) -> ValidateResponse:
        """Validate a transaction before execution.
        
        Args:
            from_address: Sender address (your agent's wallet)
            to: Target contract address
            data: Transaction calldata
            value: Value in wei (default: "0")
            guardrail_id: Guardrail ID (overrides default)
            chain_id: Chain ID (overrides default)
        
        Returns:
            Validation result
        """
        response = self._request(
            "POST",
            "/validate",
            json={
                "from": from_address,
                "to": to,
                "data": data,
                "value": value,
                "guardrailId": guardrail_id or self.config.guardrail_id,
                "chainId": chain_id or self.config.chain_id,
            },
        )
        return ValidateResponse.model_validate(response)
    
    def validate_or_throw(
        self,
        from_address: str,
        to: str,
        data: str,
        value: str = "0",
        guardrail_id: Optional[str] = None,
        chain_id: Optional[int] = None,
    ) -> ValidateResponse:
        """Validate and throw if unsafe (convenience method).
        
        Args:
            from_address: Sender address (your agent's wallet)
            to: Target contract address
            data: Transaction calldata
            value: Value in wei (default: "0")
            guardrail_id: Guardrail ID (overrides default)
            chain_id: Chain ID (overrides default)
        
        Returns:
            Validation result (only if safe)
        
        Raises:
            ProofGateError: If validation fails
        """
        result = self.validate(
            from_address=from_address,
            to=to,
            data=data,
            value=value,
            guardrail_id=guardrail_id,
            chain_id=chain_id,
        )
        
        if not result.safe:
            raise ProofGateError(
                result.reason,
                "VALIDATION_FAILED",
                validation_result=result,
            )
        
        return result
    
    def check_agent(self, wallet: str) -> AgentCheckResponse:
        """Check an agent's trust score and verification status.
        
        Args:
            wallet: Agent wallet address
        
        Returns:
            Agent verification info
        """
        response = self._request("GET", f"/agents/check?wallet={wallet}")
        return AgentCheckResponse.model_validate(response)
    
    def get_evidence(self, validation_id: str) -> EvidenceResponse:
        """Get evidence for a past validation.
        
        Args:
            validation_id: Validation ID
        
        Returns:
            Evidence details
        """
        response = self._request("GET", f"/evidence/{validation_id}")
        return EvidenceResponse.model_validate(response)
    
    def get_usage(self, wallet: str) -> UsageResponse:
        """Get validation usage stats for a wallet.
        
        Args:
            wallet: Wallet address
        
        Returns:
            Usage statistics
        """
        response = self._request("GET", f"/validate?wallet={wallet}")
        return UsageResponse.model_validate(response)


def is_transaction_safe(
    api_key: str,
    from_address: str,
    to: str,
    data: str,
    value: str = "0",
) -> bool:
    """Quick validation helper.
    
    Args:
        api_key: ProofGate API key
        from_address: Sender address
        to: Target contract address
        data: Transaction calldata
        value: Value in wei (default: "0")
    
    Returns:
        Whether the transaction is safe
    
    Example:
        >>> from proofgate import is_transaction_safe
        >>> 
        >>> safe = is_transaction_safe(
        ...     "pg_xxx",
        ...     from_address=agent,
        ...     to=contract,
        ...     data=calldata,
        ... )
    """
    with ProofGate(api_key=api_key) as pg:
        result = pg.validate(
            from_address=from_address,
            to=to,
            data=data,
            value=value,
        )
        return result.safe
