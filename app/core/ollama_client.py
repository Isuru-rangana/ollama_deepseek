import logging
import json
from typing import Dict, Any, Optional
from .config import settings
from .connection import ConnectionManager

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, model: str):
        self.model = model
        self.connection_manager = ConnectionManager()

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Generate code using the Ollama API with retry and circuit breaker
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            client = await self.connection_manager.get_client()
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            
            # Accumulate the response text from the stream
            response_text = ""
            total_duration = 0
            
            # Process each line in the response
            for line in response.text.strip().split('\n'):
                if not line:
                    continue
                    
                # Parse the JSON response
                chunk = json.loads(line)
                if chunk.get("response"):
                    response_text += chunk["response"]
                if chunk.get("total_duration"):
                    total_duration = chunk["total_duration"]
                
            return {
                "response": response_text,
                "model": self.model,
                "total_duration": total_duration
            }
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model
        """
        try:
            client = await self.connection_manager.get_client()
            response = await client.post("/api/show", json={"name": self.model})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            raise

ollama_client = OllamaClient(model=settings.MODEL_NAME) 