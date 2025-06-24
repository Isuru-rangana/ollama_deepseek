from tenacity import retry, stop_after_attempt, wait_exponential
from fastapi import HTTPException
import httpx
import logging
from typing import Optional, Dict, Any
from .config import settings

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self._failed_attempts = 0
        self.MAX_FAILED_ATTEMPTS = 3
        self.is_circuit_open = False

    async def get_client(self) -> httpx.AsyncClient:
        if not self.client or self.client.is_closed:
            self.client = httpx.AsyncClient(
                base_url=settings.OLLAMA_API_BASE_URL,
                timeout=settings.REQUEST_TIMEOUT
            )
        return self.client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def make_request(self, method: str, url: str, **kwargs) -> Dict[Any, Any]:
        if self.is_circuit_open:
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable. Circuit breaker is open."
            )

        try:
            client = await self.get_client()
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            self._failed_attempts = 0
            return response.json()
        except Exception as e:
            self._failed_attempts += 1
            if self._failed_attempts >= self.MAX_FAILED_ATTEMPTS:
                self.is_circuit_open = True
                logger.error("Circuit breaker opened due to multiple failures")
            raise HTTPException(status_code=500, detail=str(e))

    async def close(self):
        if self.client:
            await self.client.aclose()

connection_manager = ConnectionManager() 