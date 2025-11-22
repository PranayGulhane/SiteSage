"""Web crawler for extracting SEO data from URLs."""
import asyncio
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup
import requests


class WebCrawler:
    """Asynchronous web crawler for SEO data extraction."""
    
    def __init__(self, timeout: int = 30):
        """Initialize crawler with timeout settings."""
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Create aiohttp session."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    async def crawl(self, url: str) -> Dict:
        """
        Crawl a URL and extract SEO data.
        
        Args:
            url: The URL to crawl
            
        Returns:
            Dictionary containing extracted SEO data
        """
        try:
            start_time = time.time()
            
            # Fetch the page
            async with self.session.get(url) as response:
                html_content = await response.text()
                page_size = len(html_content.encode('utf-8'))
                load_time = time.time() - start_time
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Extract data
            seo_data = {
                'title': self._extract_title(soup),
                'meta_description': self._extract_meta_description(soup),
                'h1_tags': self._extract_headings(soup, 'h1'),
                'h2_tags': self._extract_headings(soup, 'h2'),
                'images': self._extract_images(soup, url),
                'links': self._extract_links(soup, url),
                'load_time': load_time,
                'page_size': page_size
            }
            
            # Check for broken links (async)
            seo_data['broken_links'] = await self._check_broken_links(
                seo_data['links']['all_links'][:50]  # Limit to first 50 links
            )
            
            return seo_data
            
        except Exception as e:
            raise Exception(f"Failed to crawl URL: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title."""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else None
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract meta description."""
        meta = soup.find('meta', attrs={'name': 'description'})
        if not meta:
            meta = soup.find('meta', attrs={'property': 'og:description'})
        return meta.get('content', '').strip() if meta else None
    
    def _extract_headings(self, soup: BeautifulSoup, tag: str) -> List[str]:
        """Extract all headings of a specific tag."""
        headings = soup.find_all(tag)
        return [h.get_text(strip=True) for h in headings if h.get_text(strip=True)]
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Extract image data including alt tags."""
        images = []
        images_without_alt = 0
        
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            if src:
                # Convert relative URLs to absolute
                absolute_src = urljoin(base_url, src)
                has_alt = bool(alt and alt.strip())
                
                images.append({
                    'src': absolute_src,
                    'alt': alt,
                    'has_alt': has_alt
                })
                
                if not has_alt:
                    images_without_alt += 1
        
        return {
            'images': images,
            'total_images': len(images),
            'images_without_alt': images_without_alt
        }
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Extract internal and external links."""
        internal_links = []
        external_links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').strip()
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)
            link_domain = urlparse(absolute_url).netloc
            
            link_data = {
                'url': absolute_url,
                'text': link.get_text(strip=True)
            }
            
            if link_domain == base_domain:
                internal_links.append(link_data)
            else:
                external_links.append(link_data)
        
        return {
            'internal_links': internal_links,
            'external_links': external_links,
            'all_links': internal_links + external_links,
            'total_links': len(internal_links) + len(external_links)
        }
    
    async def _check_broken_links(self, links: List[Dict]) -> List[Dict]:
        """Check for broken links asynchronously."""
        broken_links = []
        
        async def check_link(link_data: Dict):
            try:
                async with self.session.head(
                    link_data['url'], 
                    timeout=aiohttp.ClientTimeout(total=10),
                    allow_redirects=True
                ) as response:
                    if response.status >= 400:
                        return {
                            'url': link_data['url'],
                            'status_code': response.status,
                            'text': link_data.get('text', '')
                        }
            except Exception:
                return {
                    'url': link_data['url'],
                    'status_code': 0,
                    'text': link_data.get('text', ''),
                    'error': 'Connection failed'
                }
            return None
        
        # Check links in parallel
        tasks = [check_link(link) for link in links]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None and exceptions
        broken_links = [r for r in results if r and not isinstance(r, Exception)]
        
        return broken_links
