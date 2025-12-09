from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.common import ResourceBase, StructuralistAnalysis, Scores, Coordinates3D

class Collaboration(BaseModel):
    artist_id: str
    strength: float = Field(ge=0.0, le=1.0)

class InstitutionLink(BaseModel):
    institution_id: str
    name: str
    type: Optional[str] = None

class ExhibitionLink(BaseModel):
    exhibition_id: str
    name: str
    year: Optional[int] = None

class PropertyValue(BaseModel):
    type: str = Field(default="PropertyValue", alias="@type")
    value: str

class Artist(ResourceBase):
    # Schema.org Core
    identifier: PropertyValue
    name: str
    alternateName: Optional[str] = Field(None, alias="alternateName")
    # Frontend compatibility alias
    alternativeName: Optional[str] = Field(None, alias="alternativeName")
    
    birthDate: Optional[str] = None
    url: Optional[str] = None
    
    # ARGO Custom Fields (Root Level)
    segment_id: Optional[str] = None
    career_stage: Optional[str] = Field(None, pattern="^(early|mid|late)$")
    
    # Frontend Compatibility & Legacy
    # Option A: Maintain birth_year as int for frontend
    birth_year: Optional[int] = Field(None, alias="birth_year")
    artist_id: Optional[str] = None 
    
    # Analysis (Flattened to Root)
    scores: Scores
    coordinates_3d: Coordinates3D # Enforcing Pydantic Model type
    
    structuralist_analysis: Optional[StructuralistAnalysis] = None
    
    # Relationships
    collaborations: List[Collaboration] = []
    institutions: List[InstitutionLink] = []
    exhibitions: List[ExhibitionLink] = []
    
    # Deprecated but kept for backward compatibility
    collaborators: List[str] = [] 

    class Config:
        populate_by_name = True
