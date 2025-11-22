"""SEO scoring engine for analyzing website quality."""
from typing import Dict, List


class SEOScorer:
    """Calculate SEO scores based on multiple factors."""
    
    # Scoring weights (total = 100)
    WEIGHTS = {
        'title': 15,
        'meta_description': 15,
        'headings': 20,
        'images': 20,
        'links': 15,
        'performance': 15
    }
    
    def calculate_score(self, seo_data: Dict) -> Dict:
        """
        Calculate overall SEO score and breakdown.
        
        Args:
            seo_data: Dictionary containing SEO data from crawler
            
        Returns:
            Dictionary with overall score and detailed breakdown
        """
        scores = {
            'title': self._score_title(seo_data.get('title')),
            'meta_description': self._score_meta_description(seo_data.get('meta_description')),
            'headings': self._score_headings(
                seo_data.get('h1_tags', []),
                seo_data.get('h2_tags', [])
            ),
            'images': self._score_images(seo_data.get('images', {})),
            'links': self._score_links(
                seo_data.get('links', {}),
                seo_data.get('broken_links', [])
            ),
            'performance': self._score_performance(
                seo_data.get('load_time'),
                seo_data.get('page_size')
            )
        }
        
        # Calculate weighted total
        total_score = sum(
            scores[category] * (self.WEIGHTS[category] / 100)
            for category in scores
        )
        
        return {
            'overall_score': round(total_score, 2),
            'breakdown': scores,
            'grade': self._get_grade(total_score),
            'issues': self._identify_issues(seo_data, scores)
        }
    
    def _score_title(self, title: str) -> float:
        """Score the page title (0-100)."""
        if not title:
            return 0.0
        
        score = 100.0
        title_length = len(title)
        
        # Optimal title length: 30-60 characters
        if title_length < 30:
            score -= 30
        elif title_length > 60:
            score -= 20
        
        return max(0.0, score)
    
    def _score_meta_description(self, description: str) -> float:
        """Score the meta description (0-100)."""
        if not description:
            return 0.0
        
        score = 100.0
        desc_length = len(description)
        
        # Optimal description length: 120-160 characters
        if desc_length < 120:
            score -= 30
        elif desc_length > 160:
            score -= 20
        
        return max(0.0, score)
    
    def _score_headings(self, h1_tags: List[str], h2_tags: List[str]) -> float:
        """Score heading structure (0-100)."""
        score = 100.0
        
        # Check H1 tags
        if not h1_tags:
            score -= 50  # Missing H1 is critical
        elif len(h1_tags) > 1:
            score -= 20  # Multiple H1s not ideal
        
        # Check H2 tags
        if not h2_tags:
            score -= 30  # Missing H2s is significant
        
        return max(0.0, score)
    
    def _score_images(self, images_data: Dict) -> float:
        """Score image optimization (0-100)."""
        total_images = images_data.get('total_images', 0)
        images_without_alt = images_data.get('images_without_alt', 0)
        
        if total_images == 0:
            return 70.0  # Neutral score if no images
        
        # Calculate percentage of images with alt tags
        alt_coverage = ((total_images - images_without_alt) / total_images) * 100
        
        return alt_coverage
    
    def _score_links(self, links_data: Dict, broken_links: List[Dict]) -> float:
        """Score link quality (0-100)."""
        total_links = links_data.get('total_links', 0)
        broken_count = len(broken_links)
        
        if total_links == 0:
            return 50.0  # Neutral score if no links
        
        # Calculate percentage of working links
        working_links_pct = ((total_links - broken_count) / total_links) * 100
        
        score = working_links_pct
        
        # Bonus for having internal links
        if links_data.get('internal_links'):
            score = min(100.0, score + 10)
        
        return score
    
    def _score_performance(self, load_time: float, page_size: int) -> float:
        """Score page performance (0-100)."""
        score = 100.0
        
        # Load time scoring
        if load_time:
            if load_time > 3.0:
                score -= 40
            elif load_time > 2.0:
                score -= 20
            elif load_time > 1.0:
                score -= 10
        
        # Page size scoring (penalize if > 2MB)
        if page_size:
            size_mb = page_size / (1024 * 1024)
            if size_mb > 2.0:
                score -= 30
            elif size_mb > 1.5:
                score -= 15
        
        return max(0.0, score)
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _identify_issues(self, seo_data: Dict, scores: Dict) -> List[str]:
        """Identify specific SEO issues."""
        issues = []
        
        # Title issues
        if not seo_data.get('title'):
            issues.append("Missing page title")
        elif len(seo_data.get('title', '')) > 60:
            issues.append("Page title too long (>60 characters)")
        
        # Meta description issues
        if not seo_data.get('meta_description'):
            issues.append("Missing meta description")
        
        # Heading issues
        h1_tags = seo_data.get('h1_tags', [])
        if not h1_tags:
            issues.append("Missing H1 heading")
        elif len(h1_tags) > 1:
            issues.append(f"Multiple H1 headings found ({len(h1_tags)})")
        
        # Image issues
        images_data = seo_data.get('images', {})
        if images_data.get('images_without_alt', 0) > 0:
            issues.append(
                f"{images_data['images_without_alt']} images missing alt text"
            )
        
        # Link issues
        broken_links = seo_data.get('broken_links', [])
        if broken_links:
            issues.append(f"{len(broken_links)} broken links detected")
        
        # Performance issues
        load_time = seo_data.get('load_time', 0)
        if load_time > 3.0:
            issues.append(f"Slow load time ({load_time:.2f}s)")
        
        return issues
