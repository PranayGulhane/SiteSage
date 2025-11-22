"""Database models for SiteSage."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Report(Base):
    """SEO audit report model."""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False, index=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    seo_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    seo_data = relationship("SEOData", back_populates="report", uselist=False, cascade="all, delete-orphan")
    ai_insights = relationship("AIInsight", back_populates="report", uselist=False, cascade="all, delete-orphan")
    

class SEOData(Base):
    """SEO data extracted from URL."""
    __tablename__ = "seo_data"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), unique=True)
    
    # Page metadata
    title = Column(String(500), nullable=True)
    meta_description = Column(Text, nullable=True)
    
    # Headings
    h1_tags = Column(JSON, nullable=True)  # List of H1 texts
    h2_tags = Column(JSON, nullable=True)  # List of H2 texts
    
    # Images
    images = Column(JSON, nullable=True)  # List of {src, alt, has_alt}
    total_images = Column(Integer, default=0)
    images_without_alt = Column(Integer, default=0)
    
    # Links
    internal_links = Column(JSON, nullable=True)
    external_links = Column(JSON, nullable=True)
    broken_links = Column(JSON, nullable=True)
    total_links = Column(Integer, default=0)
    broken_links_count = Column(Integer, default=0)
    
    # Performance
    load_time = Column(Float, nullable=True)  # in seconds
    page_size = Column(Integer, nullable=True)  # in bytes
    
    # Raw HTML (optional, for debugging)
    # html_content = Column(Text, nullable=True)
    
    # Relationship
    report = relationship("Report", back_populates="seo_data")


class AIInsight(Base):
    """AI-generated insights and recommendations."""
    __tablename__ = "ai_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), unique=True)
    
    # AI-generated content
    summary = Column(Text, nullable=True)  # 2-3 paragraph SEO summary
    recommendations = Column(JSON, nullable=True)  # List of 3-5 optimization suggestions
    
    # Metadata
    model_used = Column(String(100), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    report = relationship("Report", back_populates="ai_insights")
