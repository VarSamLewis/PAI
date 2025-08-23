from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List, Optional, Dict
import datetime

class Resource(BaseModel):
    Name: str
    ID: str 
    Description: str
    ContentType: Optional[str] = None
    Content: str
    Size: float
    LastModified: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    Filetype: Optional[str] = None
    Tags: Optional[List[str]] = None
    
    @field_validator('LastModified')
    def validate_iso_date(cls, v):
        try:
            datetime.datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('LastModified must be a valid ISO format date')


class ResourceCollection(BaseModel):
    """Collection of resources"""
    resources: List[Resource] = []
