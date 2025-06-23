import httpx
from typing import Dict, Any, Optional
from .config import settings

class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_API_BASE_URL
        self.model = settings.OLLAMA_MODEL_NAME
        self.timeout = settings.REQUEST_TIMEOUT

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """
        Generate code using the DeepSeek Coder model
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"HTTP error occurred: {str(e)}")
            except Exception as e:
                raise Exception(f"An error occurred: {str(e)}")

    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        """
        url = f"{self.base_url}/api/tags"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"HTTP error occurred: {str(e)}")
            except Exception as e:
                raise Exception(f"An error occurred: {str(e)}")

ollama_client = OllamaClient() 