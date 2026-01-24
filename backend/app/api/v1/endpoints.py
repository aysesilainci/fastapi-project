from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import redis
import json
import os
import logging
from datetime import date, timedelta
import random

from app import crud, schemas
from app.database import get_db
from app.models import Paper, Citation

logger = logging.getLogger(__name__)

router = APIRouter()

# Redis connection
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@router.post("/generate")
def generate_citations(db: Session = Depends(get_db)):
    """
    Generate at least 1,000,000 synthetic citation records.
    Uses batch inserts for performance.
    """
    logger.info("Starting citation generation...")
    
    # Generate papers first
    topics = ["AI", "Machine Learning", "Deep Learning", "NLP", "Computer Vision", 
              "Robotics", "Data Science", "Statistics", "Mathematics", "Physics"]
    
    papers = []
    batch_size = 1000
    total_papers = 10000  # Generate 10k papers to have enough for citations
    
    logger.info(f"Generating {total_papers} papers...")
    for i in range(total_papers):
        paper = schemas.PaperCreate(
            title=f"Research Paper {i+1}",
            topic=random.choice(topics),
            published_year=random.randint(2000, 2024)
        )
        papers.append(paper)
        
        if len(papers) >= batch_size:
            crud.create_papers_batch(db, papers)
            papers = []
            logger.info(f"Created {i+1} papers...")
    
    if papers:
        crud.create_papers_batch(db, papers)
    
    # Get all paper IDs
    all_papers = db.query(Paper).all()
    paper_ids = [p.id for p in all_papers]
    
    if not paper_ids:
        raise HTTPException(status_code=500, detail="No papers created")
    
    # Generate citations
    logger.info("Generating citations...")
    citations = []
    target_citations = 1000000
    batch_size = 5000
    
    start_date = date(2000, 1, 1)
    end_date = date.today()
    days_between = (end_date - start_date).days
    
    for i in range(target_citations):
        source_id = random.choice(paper_ids)
        target_id = random.choice(paper_ids)
        
        # Avoid self-citations
        while source_id == target_id:
            target_id = random.choice(paper_ids)
        
        random_days = random.randint(0, days_between)
        citation_date = start_date + timedelta(days=random_days)
        
        citation = schemas.CitationCreate(
            source_paper_id=source_id,
            target_paper_id=target_id,
            citation_date=citation_date
        )
        citations.append(citation)
        
        if len(citations) >= batch_size:
            crud.create_citations_batch(db, citations)
            citations = []
            if (i + 1) % 100000 == 0:
                logger.info(f"Created {i+1} citations...")
    
    if citations:
        crud.create_citations_batch(db, citations)
    
    paper_count = crud.get_paper_count(db)
    citation_count = crud.get_citation_count(db)
    
    logger.info(f"Generation complete: {paper_count} papers, {citation_count} citations")
    
    return {
        "message": "Citation generation completed",
        "papers_created": paper_count,
        "citations_created": citation_count
    }


@router.get("/top-papers", response_model=List[schemas.TopPaperResponse])
def get_top_papers(
    topic: str = Query(..., description="Topic to filter papers"),
    limit: int = Query(50, ge=1, le=100, description="Number of top papers to return"),
    db: Session = Depends(get_db)
):
    """
    Get most cited papers for a topic with citation growth rate.
    Uses Redis caching with 60 second TTL.
    """
    from fastapi import Response
    
    # Create cache key based on topic and limit
    cache_key = f"top_papers:{topic}:{limit}"
    cache_status = "MISS"
    
    # Try to get from cache
    try:
        cached_result = redis_client.get(cache_key)
        if cached_result:
            logger.info(f"Cache HIT for key: {cache_key}")
            cache_status = "HIT"
            response_data = json.loads(cached_result)
            # Create response with cache header
            from fastapi.responses import JSONResponse
            response = JSONResponse(content=response_data)
            response.headers["X-Cache-Status"] = cache_status
            response.headers["X-Cache-Key"] = cache_key
            return response
    except Exception as e:
        logger.warning(f"Redis cache read error: {e} - falling back to database")
    
    # Cache miss - query from database
    logger.info(f"Cache MISS for key: {cache_key} - querying database")
    top_papers = crud.get_top_papers_by_topic(db, topic=topic, limit=limit)
    
    # Store in cache with 60 second TTL
    try:
        redis_client.setex(cache_key, 60, json.dumps(top_papers))
        logger.info(f"Stored result in cache with key: {cache_key}, TTL: 60s")
    except Exception as e:
        logger.warning(f"Redis cache write error: {e} - continuing without cache")
    
    # Return response with cache header
    from fastapi.responses import JSONResponse
    response = JSONResponse(content=top_papers)
    response.headers["X-Cache-Status"] = cache_status
    response.headers["X-Cache-Key"] = cache_key
    return response


@router.delete("/clear")
def clear_database(db: Session = Depends(get_db)):
    """
    Clear all papers and citations from the database.
    Also clears Redis cache.
    """
    logger.warning("Clearing all database data...")
    
    # Clear database
    result = crud.clear_all_data(db)
    
    # Clear Redis cache
    try:
        # Get all cache keys matching our pattern
        cache_keys = redis_client.keys("top_papers:*")
        if cache_keys:
            redis_client.delete(*cache_keys)
            logger.info(f"Cleared {len(cache_keys)} cache keys from Redis")
    except Exception as e:
        logger.warning(f"Error clearing Redis cache: {e}")
    
    logger.info(f"Database cleared: {result['papers_deleted']} papers, {result['citations_deleted']} citations")
    
    return {
        "message": "Database cleared successfully",
        **result
    }


@router.get("/health")
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy"}


@router.get("/stats")
def get_statistics(db: Session = Depends(get_db)):
    """
    Get comprehensive statistics about papers and citations.
    """
    return crud.get_statistics(db)


@router.delete("/cache/{topic}/{limit}")
def clear_cache(topic: str, limit: int):
    """
    Clear cache for a specific topic and limit.
    """
    cache_key = f"top_papers:{topic}:{limit}"
    try:
        redis_client.delete(cache_key)
        logger.info(f"Cache cleared for key: {cache_key}")
        return {"message": "Cache cleared", "cache_key": cache_key}
    except Exception as e:
        logger.warning(f"Error clearing cache: {e}")
        return {"message": "Error clearing cache", "error": str(e)}


@router.get("/top-papers-db", response_model=List[schemas.TopPaperResponse])
def get_top_papers_from_db(
    topic: str = Query(..., description="Topic to filter papers"),
    limit: int = Query(50, ge=1, le=100, description="Number of top papers to return"),
    db: Session = Depends(get_db)
):
    """
    Get top papers directly from database (bypass cache).
    This endpoint always queries the database and does not use cache.
    """
    from fastapi.responses import JSONResponse
    
    cache_key = f"top_papers:{topic}:{limit}"
    logger.info(f"Direct database query (bypassing cache) for key: {cache_key}")
    
    top_papers = crud.get_top_papers_by_topic(db, topic=topic, limit=limit)
    
    response = JSONResponse(content=top_papers)
    response.headers["X-Cache-Status"] = "BYPASS"
    response.headers["X-Cache-Key"] = cache_key
    response.headers["X-Source"] = "DATABASE"
    
    return response

