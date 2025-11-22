"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, HttpUrl, Field


class URLSubmitRequest(BaseModel):
    """Request schema for submitting a URL to analyze."""
    url: HttpUrl = Field(..., description="URL to analyze")


class SEODataResponse(BaseModel):
    """Response schema for SEO data."""
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_tags: List[str] = []
    h2_tags: List[str] = []
    total_images: int = 0
    images_without_alt: int = 0
    total_links: int = 0
    broken_links_count: int = 0
    load_time: Optional[float] = None
    page_size: Optional[int] = None
    
    class Config:
        from_attributes = True


class AIInsightResponse(BaseModel):
    """Response schema for AI insights."""
    summary: Optional[str] = None
    recommendations: List[str] = []
    model_used: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReportResponse(BaseModel):
    """Response schema for a report."""
    id: int
    url: str
    status: str
    seo_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    seo_data: Optional[SEODataResponse] = None
    ai_insights: Optional[AIInsightResponse] = None
    
    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """Response schema for list of reports."""
    id: int
    url: str
    status: str
    seo_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    database: str
