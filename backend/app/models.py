from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    topic = Column(String, nullable=False, index=True)
    published_year = Column(Integer, nullable=False)

    citations_as_source = relationship(
        "Citation",
        foreign_keys="Citation.source_paper_id",
        back_populates="source_paper"
    )
    citations_as_target = relationship(
        "Citation",
        foreign_keys="Citation.target_paper_id",
        back_populates="target_paper"
    )


class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    source_paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    target_paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    citation_date = Column(Date, nullable=False)

    source_paper = relationship("Paper", foreign_keys=[source_paper_id], back_populates="citations_as_source")
    target_paper = relationship("Paper", foreign_keys=[target_paper_id], back_populates="citations_as_target")

