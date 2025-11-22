"""PDF report generator using ReportLab."""
import os
from datetime import datetime
from typing import Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from .config import settings


class PDFReportGenerator:
    """Generate PDF reports for SEO audits."""
    
    def __init__(self):
        """Initialize PDF generator."""
        os.makedirs(settings.reports_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12
        ))
    
    def generate_report(self, report_data: Dict, filename: str = None) -> str:
        """
        Generate PDF report from report data.
        
        Args:
            report_data: Complete report data including SEO data, scores, and insights
            filename: Optional custom filename
            
        Returns:
            Path to generated PDF file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"seo_report_{timestamp}.pdf"
        
        filepath = os.path.join(settings.reports_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("SiteSage SEO Audit Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Report metadata
        url = report_data.get('url', 'N/A')
        created_at = report_data.get('created_at', datetime.now())
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        meta_data = [
            ['URL:', url],
            ['Generated:', created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Report ID:', str(report_data.get('id', 'N/A'))]
        ]
        
        meta_table = Table(meta_data, colWidths=[1.5*inch, 5*inch])
        meta_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # SEO Score Summary
        story.append(Paragraph("SEO Score Summary", self.styles['SectionHeader']))
        score = report_data.get('seo_score', 0)
        grade = self._get_grade(score)
        
        score_data = [
            ['Overall Score:', f"{score}/100"],
            ['Grade:', grade],
        ]
        
        score_table = Table(score_data, colWidths=[2*inch, 2*inch])
        score_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # AI Insights Summary
        ai_insights = report_data.get('ai_insights', {})
        if ai_insights and ai_insights.get('summary'):
            story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
            story.append(Paragraph(ai_insights['summary'], self.styles['BodyText']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Recommendations
        if ai_insights and ai_insights.get('recommendations'):
            story.append(Paragraph("Recommendations", self.styles['SectionHeader']))
            for i, rec in enumerate(ai_insights['recommendations'], 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['BodyText']))
                story.append(Spacer(1, 0.1 * inch))
            story.append(Spacer(1, 0.2 * inch))
        
        # Technical Details
        story.append(Paragraph("Technical Details", self.styles['SectionHeader']))
        seo_data = report_data.get('seo_data', {})
        
        tech_data = [
            ['Metric', 'Value'],
            ['Page Title', seo_data.get('title', 'N/A')[:80]],
            ['Meta Description', (seo_data.get('meta_description', 'N/A') or 'Missing')[:100]],
            ['H1 Tags', str(len(seo_data.get('h1_tags', [])))],
            ['H2 Tags', str(len(seo_data.get('h2_tags', [])))],
            ['Total Images', str(seo_data.get('total_images', 0))],
            ['Images Without Alt', str(seo_data.get('images_without_alt', 0))],
            ['Total Links', str(seo_data.get('total_links', 0))],
            ['Broken Links', str(seo_data.get('broken_links_count', 0))],
            ['Load Time', f"{seo_data.get('load_time', 0):.2f}s"],
        ]
        
        tech_table = Table(tech_data, colWidths=[2.5*inch, 4*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(tech_table)
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return 'A (Excellent)'
        elif score >= 80:
            return 'B (Good)'
        elif score >= 70:
            return 'C (Average)'
        elif score >= 60:
            return 'D (Poor)'
        else:
            return 'F (Critical Issues)'
