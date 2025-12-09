from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.errors import ErrorResponse, ErrorDetail
import time
from datetime import datetime

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Fallback for unhandled exceptions
            error_content = ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="An unexpected error occurred",
                    details=str(e),
                    timestamp=datetime.utcnow(),
                    request_id=str(time.time()),
                    documentation="https://api.argo.art/docs/errors/INTERNAL_SERVER_ERROR"
                )
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_content.model_dump(mode='json')
            )
