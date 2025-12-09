from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.common import ResourceBase

class Institution(ResourceBase):
    name: str
    location: Optional[str] = Field(None, alias="location")
    type: Optional[str] = Field(None, alias="argo:type")
    
    class Config:
        populate_by_name = True

class Exhibition(ResourceBase):
    name: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    location: Optional[str] = None

    class Config:
        populate_by_name = True

class Transaction(ResourceBase):
    price: float = Field(alias="argo:price")
    date: str = Field(alias="date")
    artwork_title: str = Field(alias="argo:artwork_title")
    
    class Config:
        populate_by_name = True

class Cluster(ResourceBase):
    name: str = Field(alias="name")
    size: int = Field(alias="argo:size")
    description: Optional[str] = Field(None, alias="description")

    class Config:
        populate_by_name = True
