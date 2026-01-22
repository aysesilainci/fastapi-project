from pydantic import BaseModel
from typing import Optional
from datetime import date


class PaperBase(BaseModel):
    title: str
    topic: str
    published_year: int


class PaperCreate(PaperBase):
    pass


class Paper(PaperBase):
    id: int

    class Config:
        from_attributes = True


class CitationBase(BaseModel):
    source_paper_id: int
    target_paper_id: int
    citation_date: date


class CitationCreate(CitationBase):
    pass


class Citation(CitationBase):
    id: int

    class Config:
        from_attributes = True


class TopPaperResponse(BaseModel):
    id: int
    title: str
    topic: str
    published_year: int
    citation_count: int
    citation_growth_rate: float

    class Config:
        from_attributes = True

