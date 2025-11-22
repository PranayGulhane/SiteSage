"""Main FastAPI application."""
import asyncio
from datetime import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from .config import settings
from .database import get_db, engine
from . import models
from .schemas import (
    URLSubmitRequest,
    ReportResponse,
    ReportListResponse,
    HealthResponse
)
from .crawler import WebCrawler
from .seo_scorer import SEOScorer
from .ai_service import AIInsightGenerator
from .pdf_generator import PDFReportGenerator

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Automated SEO Performance Analyzer"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
seo_scorer = SEOScorer()
pdf_generator = PDFReportGenerator()


@app.get("/", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = "disconnected"
        print(f"Database connection error: {e}")  # Log the error
    
    return {
        "status": "healthy",
        "version": settings.app_version,
        "database": db_status
    }


@app.post("/api/reports", response_model=ReportResponse, status_code=201)
async def create_report(
    request: URLSubmitRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submit a URL for SEO analysis.
    
    The analysis runs asynchronously in the background.
    """
    # Create initial report
    report = models.Report(
        url=str(request.url),
        status="pending"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Schedule background analysis
    background_tasks.add_task(analyze_url, report.id)
    
    return report


@app.get("/api/reports", response_model=List[ReportListResponse])
async def list_reports(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get list of all reports."""
    reports = db.query(models.Report)\
        .order_by(models.Report.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return reports


@app.get("/api/reports/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get detailed report by ID."""
    report = db.query(models.Report)\
        .filter(models.Report.id == report_id)\
        .first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@app.get("/api/reports/{report_id}/pdf")
async def download_pdf_report(report_id: int, db: Session = Depends(get_db)):
    """Download PDF report."""
    report = db.query(models.Report)\
        .filter(models.Report.id == report_id)\
        .first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.status != "completed":
        raise HTTPException(status_code=400, detail="Report not yet completed")
    
    # Generate PDF
    report_data = {
        'id': report.id,
        'url': report.url,
        'seo_score': report.seo_score,
        'created_at': report.created_at,
        'seo_data': {
            'title': report.seo_data.title if report.seo_data else None,
            'meta_description': report.seo_data.meta_description if report.seo_data else None,
            'h1_tags': report.seo_data.h1_tags if report.seo_data else [],
            'h2_tags': report.seo_data.h2_tags if report.seo_data else [],
            'total_images': report.seo_data.total_images if report.seo_data else 0,
            'images_without_alt': report.seo_data.images_without_alt if report.seo_data else 0,
            'total_links': report.seo_data.total_links if report.seo_data else 0,
            'broken_links_count': report.seo_data.broken_links_count if report.seo_data else 0,
            'load_time': report.seo_data.load_time if report.seo_data else 0,
        },
        'ai_insights': {
            'summary': report.ai_insights.summary if report.ai_insights else None,
            'recommendations': report.ai_insights.recommendations if report.ai_insights else []
        }
    }
    
    pdf_path = pdf_generator.generate_report(
        report_data,
        filename=f"report_{report_id}.pdf"
    )
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"sitesage_report_{report_id}.pdf"
    )


@app.delete("/api/reports/{report_id}", status_code=204)
async def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a report."""
    report = db.query(models.Report)\
        .filter(models.Report.id == report_id)\
        .first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(report)
    db.commit()
    
    return None


async def analyze_url(report_id: int):
    """
    Background task to analyze URL and generate insights.
    
    This function runs asynchronously after a report is created.
    """
    from .database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Get report
        report = db.query(models.Report).filter(models.Report.id == report_id).first()
        if not report:
            return
        
        # Update status
        report.status = "processing"
        db.commit()
        
        # Crawl URL
        async with WebCrawler() as crawler:
            seo_data = await crawler.crawl(report.url)
        
        # Calculate SEO score
        score_result = seo_scorer.calculate_score(seo_data)
        
        # Save SEO data
        seo_data_model = models.SEOData(
            report_id=report.id,
            title=seo_data.get('title'),
            meta_description=seo_data.get('meta_description'),
            h1_tags=seo_data.get('h1_tags', []),
            h2_tags=seo_data.get('h2_tags', []),
            images=seo_data.get('images', {}).get('images', []),
            total_images=seo_data.get('images', {}).get('total_images', 0),
            images_without_alt=seo_data.get('images', {}).get('images_without_alt', 0),
            internal_links=seo_data.get('links', {}).get('internal_links', []),
            external_links=seo_data.get('links', {}).get('external_links', []),
            broken_links=seo_data.get('broken_links', []),
            total_links=seo_data.get('links', {}).get('total_links', 0),
            broken_links_count=len(seo_data.get('broken_links', [])),
            load_time=seo_data.get('load_time'),
            page_size=seo_data.get('page_size')
        )
        db.add(seo_data_model)
        
        # Generate AI insights if API key is configured
        if settings.groq_api_key:
            try:
                ai_generator = AIInsightGenerator()
                ai_insights = await ai_generator.generate_insights(seo_data, score_result)
                
                ai_insights_model = models.AIInsight(
                    report_id=report.id,
                    summary=ai_insights.get('summary'),
                    recommendations=ai_insights.get('recommendations', []),
                    model_used=ai_insights.get('model_used')
                )
                db.add(ai_insights_model)
            except Exception as e:
                print(f"AI insight generation failed: {str(e)}")
                # Continue without AI insights
        
        # Update report
        report.seo_score = score_result['overall_score']
        report.status = "completed"
        report.completed_at = datetime.utcnow()
        
        db.commit()
        
    except Exception as e:
        # Handle errors
        report.status = "failed"
        report.error_message = str(e)
        db.commit()
        print(f"Error analyzing URL {report.url}: {str(e)}")
    
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
