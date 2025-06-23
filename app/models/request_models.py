from pydantic import BaseModel, Field
from typing import Optional

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="The prompt for code generation")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt to guide the model")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Temperature for generation")
    max_tokens: int = Field(2048, ge=1, description="Maximum number of tokens to generate") 