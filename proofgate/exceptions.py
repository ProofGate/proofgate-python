"""Exceptions for ProofGate SDK."""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from proofgate.types import ValidateResponse


class ProofGateError(Exception):
    """Base exception for ProofGate errors.
    
    Attributes:
        message: Human-readable error message
        code: Error code (e.g., 'VALIDATION_FAILED', 'API_ERROR')
        status_code: HTTP status code (if applicable)
        validation_result: Validation result (if validation failed)
    """
    
    def __init__(
        self,
        message: str,
        code: str,
        status_code: Optional[int] = None,
        validation_result: Optional["ValidateResponse"] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.validation_result = validation_result
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"
    
    def __repr__(self) -> str:
        return f"ProofGateError(code={self.code!r}, message={self.message!r})"
