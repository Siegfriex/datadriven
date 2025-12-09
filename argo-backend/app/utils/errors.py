from datetime import datetime
from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid

# Error Code Mapping
ERROR_CODE_MAP = {
    400: "INVALID_PARAMETER",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    429: "RATE_LIMIT_EXCEEDED",
    500: "INTERNAL_ERROR",
    503: "SERVICE_UNAVAILABLE"
}

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[str] = None
    timestamp: datetime
    request_id: Optional[str] = None
    documentation: Optional[str] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail

def create_error_response(
    code: str, 
    message: str, 
    status_code: int = 400, 
    details: Optional[str] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Standardized Error Response generating a JSONResponse object.
    Automatically maps status codes to standard ARGO error codes if not provided.
    """
    final_code = code if code != "ERROR_CODE" else ERROR_CODE_MAP.get(status_code, "UNKNOWN_ERROR")
    
    error_content = ErrorResponse(
        error=ErrorDetail(
            code=final_code,
            message=message,
            details=details,
            timestamp=datetime.utcnow(),
            request_id=request_id or str(uuid.uuid4()),
            documentation=f"https://api.argo.art/docs/errors/{final_code}"
        )
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_content.model_dump(mode='json')
    )
