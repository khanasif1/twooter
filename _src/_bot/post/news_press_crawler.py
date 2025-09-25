#!/usr/bin/env python3
"""
Victor Campaign News and Press Releases Crawler

This crawler specifically targets News and Press Releases links from
https://victor-for-president.legitreal.com/index.html and extracts
detailed content from each article.

Returns data in the specified JSON format:
{
    "main": [
        {
            "title": "",
            "content": "",
            "summary": ""
        }
    ]
}
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class NewsPressCrawler:
    """
    Focused crawler for Victor campaign News and Press Releases.
    """
    
    def __init__(self):
        self.base_url = "https://victor-for-president.legitreal.com"
        self.index_url = f"{self.base_url}/index.html"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.processed_urls: Set[str] = set()
    
    def crawl_news_and_press(self) -> Dict:
        """
        Main crawler method that extracts News and Press Releases.
        
        Returns:
            Dict: Data in the specified format with main array
        """
        print("🚀 Starting News and Press Releases crawler...")
        print(f"🔍 Scanning: {self.index_url}")
        
        result = {
            "main": [],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "source_url": self.index_url,
                "total_articles": 0,
                "crawler_version": "news_press_focused"
            }
        }
        
        try:
            # Step 1: Get the main index page
            print("📖 Loading main page...")
            response = self.session.get(self.index_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Step 2: Find News and Press Release links
            article_links = self._find_news_press_links(soup)
            print(f"🔗 Found {len(article_links)} News/Press Release links")
            
            # Step 3: Process each article
            for i, article_url in enumerate(article_links, 1):
                try:
                    print(f"📰 Processing article {i}/{len(article_links)}: {article_url}")
                    article_data = self._extract_article_details(article_url)
                    
                    if article_data:
                        result["main"].append(article_data)
                        print(f"   ✅ Extracted: {article_data['title'][:50]}...")
                    else:
                        print(f"   ❌ Failed to extract content")
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"   ❌ Error processing {article_url}: {e}")
                    continue
            
            # Update metadata
            result["metadata"]["total_articles"] = len(result["main"])
            result["metadata"]["completion_time"] = datetime.now().isoformat()
            
            print(f"\n✅ Crawling completed!")
            print(f"📊 Total articles extracted: {len(result['main'])}")
            
            return result
            
        except Exception as e:
            print(f"❌ Fatal error during crawling: {e}")
            result["metadata"]["error"] = str(e)
            return result
    
    def _find_news_press_links(self, soup: BeautifulSoup) -> List[str]:
        """
        Find all News and Press Release links from the main page.
        
        Args:
            soup: BeautifulSoup object of the main page
            
        Returns:
            List[str]: List of article URLs
        """
        article_links = set()
        
        # Strategy 1: Look for links in articles, posts, or news sections
        news_indicators = [
            'article', 'post', 'news', 'press', 'content', 'item',
            'story', 'release', 'update', 'announcement'
        ]
        
        # Find elements that likely contain news/press links
        for element in soup.find_all(['article', 'div', 'section'], class_=True):
            classes = ' '.join(element.get('class', [])).lower()
            
            # Check if element classes suggest news/press content
            if any(indicator in classes for indicator in news_indicators):
                # Find all links within this element
                for link in element.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(self.base_url, href)
                    
                    if self._is_news_press_url(full_url, link):
                        article_links.add(full_url)
        
        # Strategy 2: Look for links with news/press indicators in text or URL
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(self.base_url, href)
            link_text = link.get_text(strip=True).lower()
            
            # Check URL and link text for news/press indicators
            if self._is_news_press_url(full_url, link):
                article_links.add(full_url)
        
        # Strategy 3: Look for specific URL patterns
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(self.base_url, href)
            
            # Common patterns for news/press articles
            if any(pattern in full_url.lower() for pattern in [
                '/post/', '/news/', '/press/', '/article/', '/story/',
                '/release/', '/update/', '/announcement/'
            ]):
                if self._is_valid_article_url(full_url):
                    article_links.add(full_url)
        
        # Remove duplicates and sort
        unique_links = list(article_links)
        unique_links.sort()
        
        print(f"   📝 Strategy breakdown:")
        print(f"      - Total unique links found: {len(unique_links)}")
        
        return unique_links
    
    def _is_news_press_url(self, url: str, link_element) -> bool:
        """
        Check if a URL appears to be a news or press release article.
        
        Args:
            url: The URL to check
            link_element: The BeautifulSoup link element
            
        Returns:
            bool: True if likely a news/press article
        """
        # Must be from the same domain
        if not url.startswith(self.base_url):
            return False
        
        # Skip unwanted file types and pages
        skip_patterns = [
            'javascript:', 'mailto:', '#', '.css', '.js', '.jpg', '.png', 
            '.gif', '.pdf', '.ico', '.svg', 'contact', 'about', 'privacy', 
            'terms', 'policies.html', 'authors-list.html'
        ]
        
        url_lower = url.lower()
        for pattern in skip_patterns:
            if pattern in url_lower:
                return False
        
        # Skip homepage variants
        if url_lower.endswith(('/index.html', '/', '/index')):
            return False
        
        # Check link text for news/press indicators
        link_text = link_element.get_text(strip=True).lower()
        news_press_keywords = [
            'news', 'press', 'release', 'article', 'story', 'update',
            'announcement', 'statement', 'kingston', 'victor', 'campaign',
            'beyond', 'future', 'vision', 'building', 'people'
        ]
        
        text_has_keywords = any(keyword in link_text for keyword in news_press_keywords)
        
        # Check URL structure for article patterns
        url_has_pattern = any(pattern in url_lower for pattern in [
            '/post/', '/news/', '/press/', '/article/', '/story/',
            '/release/', '/2025-', 'kingston', 'beyond', 'future'
        ])
        
        return text_has_keywords or url_has_pattern
    
    def _is_valid_article_url(self, url: str) -> bool:
        """
        Additional validation for article URLs.
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if valid article URL
        """
        # Must be from correct domain
        if not url.startswith(self.base_url):
            return False
        
        # Must have some path content
        if url.count('/') < 4:  # Less than base_url + meaningful path
            return False
        
        # Skip already processed
        if url in self.processed_urls:
            return False
        
        return True
    
    def _extract_article_details(self, url: str) -> Optional[Dict]:
        """
        Extract title, content, and summary from an article page.
        
        Args:
            url: Article URL to scrape
            
        Returns:
            Dict: Article data with title, content, summary
        """
        if url in self.processed_urls:
            return None
        
        self.processed_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_content(soup)
            
            # Extract or generate summary
            summary = self._extract_summary(soup, content)
            
            # Validate that we have meaningful content
            if not title or len(content) < 100:
                print(f"   ⚠️  Insufficient content extracted from {url}")
                return None
            
            return {
                "title": title,
                "content": content,
                "summary": summary
            }
            
        except Exception as e:
            print(f"   ❌ Error extracting from {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extract article title using multiple strategies.
        
        Args:
            soup: BeautifulSoup object of the article page
            
        Returns:
            str: Article title
        """
        # Strategy 1: Look for main heading
        for selector in ['h1', 'h2', '.title', '.headline', '.article-title', '.post-title']:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 3:
                    return title
        
        # Strategy 2: Page title
        title_elem = soup.find('title')
        if title_elem:
            title = title_elem.get_text(strip=True)
            # Clean up title (remove site name)
            if '|' in title:
                title = title.split('|')[0].strip()
            if title and len(title) > 3:
                return title
        
        return "Untitled Article"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main article content.
        
        Args:
            soup: BeautifulSoup object of the article page
            
        Returns:
            str: Article content
        """
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                           'aside', '.navigation', '.menu', '.sidebar', 
                           '.comments', '.share', '.related']):
            element.decompose()
        
        # Strategy 1: Look for main content containers
        content_selectors = [
            'article',
            '[role="main"]',
            '.content',
            '.article-content',
            '.post-content',
            '.main-content',
            'main',
            '.entry-content',
            '.article-body',
            '.post-body'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(separator='\n', strip=True)
                if len(text) > 200:  # Reasonable content length
                    return self._clean_content(text)
        
        # Strategy 2: Collect all paragraphs and meaningful content
        content_parts = []
        
        # Find content after the main heading
        main_heading = soup.find(['h1', 'h2'])
        content_area = soup
        
        if main_heading:
            # Get content after the main heading
            for sibling in main_heading.find_next_siblings():
                if sibling.name in ['p', 'div', 'section', 'article']:
                    text = sibling.get_text(strip=True)
                    if len(text) > 20:  # Skip very short text
                        content_parts.append(text)
        
        # If no content found after heading, collect all paragraphs
        if not content_parts:
            for elem in soup.find_all(['p', 'div']):
                text = elem.get_text(strip=True)
                if len(text) > 30:  # Skip short text snippets
                    content_parts.append(text)
        
        content = '\n\n'.join(content_parts) if content_parts else "No content found"
        return self._clean_content(content)
    
    def _extract_summary(self, soup: BeautifulSoup, content: str) -> str:
        """
        Extract or generate article summary.
        
        Args:
            soup: BeautifulSoup object of the article page
            content: Full article content
            
        Returns:
            str: Article summary
        """
        # Strategy 1: Look for explicit summary/excerpt
        for selector in ['.summary', '.excerpt', '.lead', '.intro', 
                        '.description', '.abstract', '.preview']:
            summary_elem = soup.select_one(selector)
            if summary_elem:
                summary = summary_elem.get_text(strip=True)
                if 50 <= len(summary) <= 500:  # Good summary length
                    return summary
        
        # Strategy 2: Use first substantial paragraph
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if 100 <= len(text) <= 400:  # Good summary length
                return text
        
        # Strategy 3: Generate from content (first few sentences)
        if content and len(content) > 100:
            sentences = content.split('. ')
            if len(sentences) >= 2:
                # Take first 1-3 sentences
                summary_sentences = sentences[:3]
                summary = '. '.join(summary_sentences)
                if not summary.endswith('.'):
                    summary += '.'
                
                # Ensure reasonable length
                if len(summary) > 400:
                    summary = summary[:400] + "..."
                
                return summary
        
        return content[:200] + "..." if len(content) > 200 else content
    
    def _clean_content(self, text: str) -> str:
        """
        Clean and format extracted content.
        
        Args:
            text: Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove common navigation text
        navigation_patterns = [
            r'Home.*?Contact',
            r'Skip to.*?content',
            r'Navigation.*?menu',
            r'Search.*?site',
            r'Copyright.*?\d{4}',
            r'All rights reserved',
            r'Privacy.*?Policy',
            r'Terms.*?Service'
        ]
        
        for pattern in navigation_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return text.strip()
    
    def save_data(self, data: Dict, filename: str = None) -> str:
        """
        Save crawled data to JSON file.
        
        Args:
            data: Data to save
            filename: Optional custom filename
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_press_data_{timestamp}.json"
        
        filepath = Path(filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Data saved to: {filepath.absolute()}")
            return str(filepath.absolute())
            
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return ""


def main():
    """Main execution function."""
    print("📰 Victor Campaign News & Press Releases Crawler")
    print("=" * 55)
    
    crawler = NewsPressCrawler()
    
    try:
        # Crawl news and press releases
        data = crawler.crawl_news_and_press()
        
        # Display results
        print(f"\n📊 Crawling Results:")
        print(f"   - Total articles: {len(data['main'])}")
        
        if data['main']:
            print(f"\n📝 Articles found:")
            for i, article in enumerate(data['main'], 1):
                title = article['title'][:60] + "..." if len(article['title']) > 60 else article['title']
                print(f"   {i}. {title}")
        
    except Exception as e:
        print(f"❌ Fatal error during crawling: {e}")
        return 1
    
    return data


if __name__ == "__main__":
    print(f"Main Result : \n \n{main().get('main', [])}")
 