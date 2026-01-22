from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, timedelta
from typing import List, Optional
from app import models, schemas


def create_paper(db: Session, paper: schemas.PaperCreate) -> models.Paper:
    db_paper = models.Paper(**paper.model_dump())
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper


def create_papers_batch(db: Session, papers: List[schemas.PaperCreate]) -> List[models.Paper]:
    db_papers = [models.Paper(**paper.model_dump()) for paper in papers]
    db.bulk_save_objects(db_papers, return_defaults=True)
    db.commit()
    return db_papers


def create_citation(db: Session, citation: schemas.CitationCreate) -> models.Citation:
    db_citation = models.Citation(**citation.model_dump())
    db.add(db_citation)
    db.commit()
    db.refresh(db_citation)
    return db_citation


def create_citations_batch(db: Session, citations: List[schemas.CitationCreate]) -> None:
    db_citations = [models.Citation(**citation.model_dump()) for citation in citations]
    db.bulk_save_objects(db_citations, return_defaults=False)
    db.commit()


def get_top_papers_by_topic(
    db: Session,
    topic: str,
    limit: int = 50
) -> List[dict]:
    # Calculate citation counts
    citation_counts = (
        db.query(
            models.Paper.id,
            models.Paper.title,
            models.Paper.topic,
            models.Paper.published_year,
            func.count(models.Citation.id).label("citation_count")
        )
        .join(
            models.Citation,
            models.Paper.id == models.Citation.target_paper_id
        )
        .filter(models.Paper.topic == topic)
        .group_by(
            models.Paper.id,
            models.Paper.title,
            models.Paper.topic,
            models.Paper.published_year
        )
        .subquery()
    )

    # Calculate recent citations (last 30 days) for growth rate
    thirty_days_ago = date.today() - timedelta(days=30)
    recent_citation_counts = (
        db.query(
            models.Paper.id,
            func.count(models.Citation.id).label("recent_citation_count")
        )
        .join(
            models.Citation,
            models.Paper.id == models.Citation.target_paper_id
        )
        .filter(
            and_(
                models.Paper.topic == topic,
                models.Citation.citation_date >= thirty_days_ago
            )
        )
        .group_by(models.Paper.id)
        .subquery()
    )

    # Join and calculate growth rate
    results = (
        db.query(
            citation_counts.c.id,
            citation_counts.c.title,
            citation_counts.c.topic,
            citation_counts.c.published_year,
            citation_counts.c.citation_count,
            func.coalesce(recent_citation_counts.c.recent_citation_count, 0).label("recent_citations")
        )
        .outerjoin(
            recent_citation_counts,
            citation_counts.c.id == recent_citation_counts.c.id
        )
        .order_by(citation_counts.c.citation_count.desc())
        .limit(limit)
        .all()
    )

    # Calculate growth rate (recent citations / total citations * 100)
    top_papers = []
    for result in results:
        growth_rate = 0.0
        if result.citation_count > 0:
            growth_rate = (result.recent_citations / result.citation_count) * 100

        top_papers.append({
            "id": result.id,
            "title": result.title,
            "topic": result.topic,
            "published_year": result.published_year,
            "citation_count": result.citation_count,
            "citation_growth_rate": round(growth_rate, 2)
        })

    return top_papers


def get_paper_count(db: Session) -> int:
    return db.query(models.Paper).count()


def get_citation_count(db: Session) -> int:
    return db.query(models.Citation).count()


def get_statistics(db: Session) -> dict:
    """Get comprehensive statistics about papers and citations."""
    from sqlalchemy import func, extract
    
    # Total counts
    total_papers = db.query(models.Paper).count()
    total_citations = db.query(models.Citation).count()
    
    # Topic distribution
    topic_distribution = (
        db.query(
            models.Paper.topic,
            func.count(models.Paper.id).label("count")
        )
        .group_by(models.Paper.topic)
        .order_by(func.count(models.Paper.id).desc())
        .all()
    )
    
    # Year distribution
    year_distribution = (
        db.query(
            models.Paper.published_year,
            func.count(models.Paper.id).label("count")
        )
        .group_by(models.Paper.published_year)
        .order_by(models.Paper.published_year.desc())
        .all()
    )
    
    # Average citations per paper
    avg_citations = 0
    if total_papers > 0:
        papers_with_citations = (
            db.query(
                models.Paper.id,
                func.count(models.Citation.id).label("citation_count")
            )
            .outerjoin(
                models.Citation,
                models.Paper.id == models.Citation.target_paper_id
            )
            .group_by(models.Paper.id)
            .all()
        )
        if papers_with_citations:
            total_citation_count = sum(p.citation_count for p in papers_with_citations)
            avg_citations = round(total_citation_count / total_papers, 2)
    
    # Most cited topics
    most_cited_topics = (
        db.query(
            models.Paper.topic,
            func.count(models.Citation.id).label("citation_count")
        )
        .join(
            models.Citation,
            models.Paper.id == models.Citation.target_paper_id
        )
        .group_by(models.Paper.topic)
        .order_by(func.count(models.Citation.id).desc())
        .limit(10)
        .all()
    )
    
    return {
        "total_papers": total_papers,
        "total_citations": total_citations,
        "average_citations_per_paper": avg_citations,
        "topic_distribution": [{"topic": t[0], "count": t[1]} for t in topic_distribution],
        "year_distribution": [{"year": y[0], "count": y[1]} for y in year_distribution],
        "most_cited_topics": [{"topic": t[0], "citation_count": t[1]} for t in most_cited_topics]
    }

