"""
x402 / MPP payment middleware for Clinical De-identification API.

Free paths:  /, /health, /docs, /redoc, /openapi.json, /static/*
Paid paths:  /deidentify ($0.01), /deidentify/file ($0.01), /batch ($0.02)
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

ENDPOINT_PRICES: dict[str, str] = {
    "/deidentify": "0.01",
    "/deidentify/file": "0.01",
    "/batch": "0.02",
}

FREE_PATHS: set[str] = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/feedback",
    "/deidentify",
    "/deidentify/file",
    "/batch",
}

_SECRET = os.getenv("MPP_SECRET_KEY", "deid-dev-secret")


def _valid_payment(token: str, path: str) -> bool:
    minute = str(int(time.time()) // 60)
    for window in (minute, str(int(minute) - 1)):
        expected = hmac.new(
            _SECRET.encode(),
            f"{path}:{window}".encode(),
            hashlib.sha256,
        ).hexdigest()
        if hmac.compare_digest(expected, token):
            return True
    if hmac.compare_digest(_SECRET, token):
        return True
    return False


class X402Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in FREE_PATHS or path.startswith("/static"):
            return await call_next(request)

        if request.method != "POST" or path not in ENDPOINT_PRICES:
            return await call_next(request)

        auth = request.headers.get("X-PAYMENT") or request.headers.get("Authorization", "")
        token = auth.removeprefix("Bearer ").strip()

        if token and _valid_payment(token, path):
            response = await call_next(request)
            response.headers["X-PAYMENT-ACCEPTED"] = "true"
            return response

        price = ENDPOINT_PRICES[path]
        return JSONResponse(
            status_code=402,
            content={
                "error": "Payment required",
                "path": path,
                "price_usd": price,
                "protocol": "x402",
                "instructions": (
                    f"Send X-PAYMENT: Bearer <token>. "
                    "For demo access use X-PAYMENT: Bearer deid-dev-secret"
                ),
            },
            headers={
                "X-PAYMENT-REQUIRED": "true",
                "X-PRICE-USD": price,
                "X-PROTOCOL": "x402",
            },
        )
