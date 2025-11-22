"""Tests for web crawler."""
import pytest
from app.crawler import WebCrawler


@pytest.mark.asyncio
async def test_extract_title():
    """Test title extraction from BeautifulSoup."""
    from bs4 import BeautifulSoup
    
    html = "<html><head><title>Test Title</title></head><body></body></html>"
    soup = BeautifulSoup(html, 'lxml')
    
    async with WebCrawler() as crawler:
        title = crawler._extract_title(soup)
        assert title == "Test Title"


@pytest.mark.asyncio
async def test_extract_meta_description():
    """Test meta description extraction."""
    from bs4 import BeautifulSoup
    
    html = '<html><head><meta name="description" content="Test description"></head><body></body></html>'
    soup = BeautifulSoup(html, 'lxml')
    
    async with WebCrawler() as crawler:
        desc = crawler._extract_meta_description(soup)
        assert desc == "Test description"


@pytest.mark.asyncio
async def test_extract_headings():
    """Test heading extraction."""
    from bs4 import BeautifulSoup
    
    html = "<html><body><h1>Heading 1</h1><h2>Heading 2</h2><h2>Heading 3</h2></body></html>"
    soup = BeautifulSoup(html, 'lxml')
    
    async with WebCrawler() as crawler:
        h1_tags = crawler._extract_headings(soup, 'h1')
        h2_tags = crawler._extract_headings(soup, 'h2')
        
        assert len(h1_tags) == 1
        assert h1_tags[0] == "Heading 1"
        assert len(h2_tags) == 2


@pytest.mark.asyncio
async def test_extract_images():
    """Test image extraction."""
    from bs4 import BeautifulSoup
    
    html = '''
    <html><body>
        <img src="image1.jpg" alt="Image 1">
        <img src="image2.jpg" alt="">
        <img src="image3.jpg">
    </body></html>
    '''
    soup = BeautifulSoup(html, 'lxml')
    
    async with WebCrawler() as crawler:
        images_data = crawler._extract_images(soup, 'https://example.com')
        
        assert images_data['total_images'] == 3
        assert images_data['images_without_alt'] == 2


@pytest.mark.asyncio
async def test_extract_links():
    """Test link extraction."""
    from bs4 import BeautifulSoup
    
    html = '''
    <html><body>
        <a href="/page1">Internal Link</a>
        <a href="https://example.com/page2">Internal Link 2</a>
        <a href="https://external.com">External Link</a>
    </body></html>
    '''
    soup = BeautifulSoup(html, 'lxml')
    
    async with WebCrawler() as crawler:
        links_data = crawler._extract_links(soup, 'https://example.com')
        
        assert links_data['total_links'] > 0
        assert len(links_data['internal_links']) >= 1
        assert len(links_data['external_links']) >= 1
