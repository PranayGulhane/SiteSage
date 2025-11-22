"""Tests for SEO scoring engine."""
import pytest
from app.seo_scorer import SEOScorer


@pytest.fixture
def scorer():
    """Create SEO scorer instance."""
    return SEOScorer()


@pytest.fixture
def sample_seo_data():
    """Sample SEO data for testing."""
    return {
        'title': 'Test Page Title',
        'meta_description': 'This is a test meta description that is of optimal length for SEO purposes.',
        'h1_tags': ['Main Heading'],
        'h2_tags': ['Subheading 1', 'Subheading 2'],
        'images': {
            'images': [
                {'src': 'image1.jpg', 'alt': 'Image 1', 'has_alt': True},
                {'src': 'image2.jpg', 'alt': '', 'has_alt': False}
            ],
            'total_images': 2,
            'images_without_alt': 1
        },
        'links': {
            'internal_links': [{'url': 'https://example.com/page1', 'text': 'Page 1'}],
            'external_links': [{'url': 'https://external.com', 'text': 'External'}],
            'all_links': [],
            'total_links': 2
        },
        'broken_links': [],
        'load_time': 1.5,
        'page_size': 500000
    }


def test_score_title_optimal(scorer):
    """Test title scoring with optimal length."""
    score = scorer._score_title('This is a good title between 30 and 60')
    assert score == 100.0


def test_score_title_missing(scorer):
    """Test title scoring with missing title."""
    score = scorer._score_title(None)
    assert score == 0.0


def test_score_title_too_short(scorer):
    """Test title scoring with short title."""
    score = scorer._score_title('Short')
    assert score < 100.0


def test_score_meta_description_optimal(scorer):
    """Test meta description scoring with optimal length."""
    desc = 'This is an optimal meta description that falls within the recommended range of 120 to 160 characters for best SEO results.'
    score = scorer._score_meta_description(desc)
    assert score == 100.0


def test_score_headings_complete(scorer):
    """Test headings scoring with proper structure."""
    score = scorer._score_headings(['H1 Tag'], ['H2 Tag 1', 'H2 Tag 2'])
    assert score == 100.0


def test_score_headings_missing_h1(scorer):
    """Test headings scoring without H1."""
    score = scorer._score_headings([], ['H2 Tag'])
    assert score < 100.0


def test_score_images(scorer):
    """Test image scoring."""
    images_data = {
        'total_images': 2,
        'images_without_alt': 1
    }
    score = scorer._score_images(images_data)
    assert score == 50.0  # 50% coverage


def test_calculate_overall_score(scorer, sample_seo_data):
    """Test overall score calculation."""
    result = scorer.calculate_score(sample_seo_data)
    assert 'overall_score' in result
    assert 'breakdown' in result
    assert 'grade' in result
    assert 'issues' in result
    assert 0 <= result['overall_score'] <= 100


def test_identify_issues_missing_title(scorer):
    """Test issue identification for missing title."""
    seo_data = {'title': None}
    scores = {}
    issues = scorer._identify_issues(seo_data, scores)
    assert any('Missing page title' in issue for issue in issues)


def test_get_grade(scorer):
    """Test grade assignment."""
    assert scorer._get_grade(95) == 'A'
    assert scorer._get_grade(85) == 'B'
    assert scorer._get_grade(75) == 'C'
    assert scorer._get_grade(65) == 'D'
    assert scorer._get_grade(50) == 'F'
