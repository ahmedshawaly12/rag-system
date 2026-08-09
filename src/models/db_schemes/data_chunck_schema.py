from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class DataChunckSchema(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    chunck_text: str = Field(... , min_length=1)
    chunck_metadata: dict
    chunck_order: int = Field(..., gt=0)
    chunck_project_id: ObjectId

    class Config:
        arbitrary_types_allowed = True