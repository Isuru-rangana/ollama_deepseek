from pydantic import BaseModel
from typing import Dict, Any, Optional

class GenerateResponse(BaseModel):
    generated_code: str
    model: str
    total_duration: int

class ModelInfoResponse(BaseModel):
    model_name: str
    status: str
    details: Dict[str, Any] 