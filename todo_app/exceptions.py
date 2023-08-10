"""
Custom HTTP exceptions
"""
from dataclasses import dataclass
from starlette.exceptions import HTTPException


@dataclass
class TODONotFoundException(HTTPException):
    status_code: int = 404
    detail: str = "Todo not found"


@dataclass
class AuthenticationFailed(HTTPException):
    status_code: int = 401
    detail: str = "Authentication Failed"
