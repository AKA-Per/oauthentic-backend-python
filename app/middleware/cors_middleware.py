from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Response

class ConditionalCorsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = str(request.url.path)
        allowed_paths = [
            "/user/auth_profile"
        ]
        state = next((p for p in allowed_paths if p in path), None)
        if state:
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Max-Age"] = "86400"
            if request.method == "OPTIONS":
                return response
            response = await call_next(request)
            return response
        else:
            return await call_next(request)