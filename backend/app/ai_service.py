"""AI service for generating SEO insights using LangChain and Groq."""
from typing import Dict, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from .config import settings


class AIInsightGenerator:
    """Generate AI-powered SEO insights and recommendations."""
    
    def __init__(self):
        """Initialize the AI service with Groq."""
        self.llm = ChatGroq(
            groq_api_key=settings.groq_api_key,
            model_name=settings.groq_model,
            temperature=0.7
        )
    
    async def generate_insights(self, seo_data: Dict, score_data: Dict) -> Dict:
        """
        Generate SEO insights and recommendations.
        
        Args:
            seo_data: Raw SEO data from crawler
            score_data: SEO score and breakdown
            
        Returns:
            Dictionary with summary and recommendations
        """
        # Generate summary
        summary = await self._generate_summary(seo_data, score_data)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(seo_data, score_data)
        
        return {
            'summary': summary,
            'recommendations': recommendations,
            'model_used': settings.groq_model
        }
    
    async def _generate_summary(self, seo_data: Dict, score_data: Dict) -> str:
        """Generate 2-3 paragraph SEO summary."""
        prompt = ChatPromptTemplate.from_template("""
You are an expert SEO consultant. Based on the following SEO audit data, 
write a comprehensive 2-3 paragraph summary of the website's SEO performance.

SEO Score: {score}/100 (Grade: {grade})
URL Title: {title}
Meta Description: {meta_desc}
H1 Headings: {h1_count}
H2 Headings: {h2_count}
Total Images: {total_images}
Images Without Alt: {images_without_alt}
Total Links: {total_links}
Broken Links: {broken_links}
Load Time: {load_time}s
Key Issues: {issues}

Write a professional, actionable summary that:
1. Highlights the overall SEO health
2. Identifies the most critical issues
3. Explains the impact on search engine rankings

Keep it concise, professional, and actionable.
""")
        
        chain = prompt | self.llm
        
        response = await chain.ainvoke({
            'score': score_data['overall_score'],
            'grade': score_data['grade'],
            'title': seo_data.get('title', 'Missing'),
            'meta_desc': seo_data.get('meta_description', 'Missing'),
            'h1_count': len(seo_data.get('h1_tags', [])),
            'h2_count': len(seo_data.get('h2_tags', [])),
            'total_images': seo_data.get('images', {}).get('total_images', 0),
            'images_without_alt': seo_data.get('images', {}).get('images_without_alt', 0),
            'total_links': seo_data.get('links', {}).get('total_links', 0),
            'broken_links': len(seo_data.get('broken_links', [])),
            'load_time': round(seo_data.get('load_time', 0), 2),
            'issues': ', '.join(score_data.get('issues', []))
        })
        
        return response.content
    
    async def _generate_recommendations(self, seo_data: Dict, score_data: Dict) -> List[str]:
        """Generate 3-5 specific optimization recommendations."""
        prompt = ChatPromptTemplate.from_template("""
You are an expert SEO consultant. Based on the following SEO audit data,
provide exactly 5 specific, actionable optimization recommendations.

SEO Score: {score}/100
Score Breakdown:
- Title: {title_score}/100
- Meta Description: {meta_score}/100
- Headings: {headings_score}/100
- Images: {images_score}/100
- Links: {links_score}/100
- Performance: {performance_score}/100

Key Issues: {issues}

Provide 5 specific recommendations in the following format:
1. [Recommendation]
2. [Recommendation]
3. [Recommendation]
4. [Recommendation]
5. [Recommendation]

Each recommendation should be:
- Specific and actionable
- Prioritized by impact
- Technical yet understandable
- One sentence each

Focus on the lowest-scoring categories and most critical issues.
""")
        
        chain = prompt | self.llm
        
        breakdown = score_data.get('breakdown', {})
        response = await chain.ainvoke({
            'score': score_data['overall_score'],
            'title_score': round(breakdown.get('title', 0), 1),
            'meta_score': round(breakdown.get('meta_description', 0), 1),
            'headings_score': round(breakdown.get('headings', 0), 1),
            'images_score': round(breakdown.get('images', 0), 1),
            'links_score': round(breakdown.get('links', 0), 1),
            'performance_score': round(breakdown.get('performance', 0), 1),
            'issues': ', '.join(score_data.get('issues', []))
        })
        
        # Parse recommendations from response
        recommendations = []
        for line in response.content.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullets
                clean_line = line.lstrip('0123456789.-•) ').strip()
                if clean_line:
                    recommendations.append(clean_line)
        
        return recommendations[:5]  # Return max 5
