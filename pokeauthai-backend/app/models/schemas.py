from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from app.models.verdict import Verdict


class Card(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    name: str
    set_name: str | None = None
    set_code: str | None = None
    hp: int | None = None
    types: list[str] = Field(default_factory=list)
    rarity: str | None = None
    image_url: str | None = None
    card_number: str | None = None
    language: str | None = None


class OCRResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    card_name: str | None = None
    hp: int | None = None
    types: list[str] = Field(default_factory=list)
    ocr_confidence: float | None = None
    raw_text: str = ""


class MarketPrice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    source: str  # e.g., "Cardmarket", "TCGPlayer"
    currency: str
    low: float | None = None
    trend: float | None = None
    url: str | None = None


class ScanRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    # We use Form data for file upload in FastAPI, so this might not be fully populated via JSON
    # But kept here for structural reference based on PRD.
    pass


class ScanResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    session_id: str
    status: str
    verdict: Verdict | None = None
    # We will expand this with authenticity_match_score etc later as per PRD
    message: str | None = None


class QueryMarketRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    card_id: str
