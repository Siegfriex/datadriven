from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Any, Dict

class ResourceBase(BaseModel):
    context: str = Field(alias='@context', default='https://schema.org/')
    type: str = Field(alias='@type')
    id: str = Field(alias='@id')

    class Config:
        populate_by_name = True

class Coordinates3D(BaseModel):
    x: float
    y: float
    z: float
    radius: float
    computed_at: Optional[str] = None
    algorithm: Optional[str] = None

class Scores(BaseModel):
    inst_score: float = Field(ge=0, le=100)
    acad_score: float = Field(ge=0, le=100)
    media_score: float = Field(ge=0, le=100)
    network_score: float = Field(ge=0, le=100)
    composite_score: float = Field(ge=0, le=100)
    composite_confidence: Optional[float] = Field(None, ge=0, le=1)

class StructuralistAnalysis(BaseModel):
    dominant_capital: str = Field(..., pattern="^(institutional|academic|media|network)$")
    capital_composition: Dict[str, float]  # {institutional_ratio, academic_ratio, ...}
    structural_position: Dict[str, Any]  # {field_quadrant, ...}
    algorithm_version: str
    weights_applied: Dict[str, float]
    theoretical_basis: str
