#!/usr/bin/env python3
"""
Victor for President Website Scraper - Simplified Version

This script scrapes the Victor for President campaign website using
requests + BeautifulSoup for better Windows compatibility.

Features:
- Scrapes all pages (index.html, policies.html, and paginated pages)
- Extracts news articles and press releases with full content
- Follows links to get detailed content
- Saves data as structured JSON
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class VictorWebScraperSimple:
    """
    Simplified scraper for Victor for President campaign website.
    Uses only requests + BeautifulSoup for maximum compatibility.
    """
    
    def __init__(self):
        self.base_url = "https://victor-for-president.legitreal.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.scraped_urls: Set[str] = set()
        self.data = {
            "scraping_metadata": {
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "total_pages_scraped": 0,
                "total_articles_extracted": 0,
                "scraper_version": "simple_requests"
            },
            "main_pages": [],
            "news_articles": [],
            "press_releases": [],
            "policies": [],
            "errors": []
        }
        
    def scrape_all(self) -> Dict:
        """
        Main scraping method that orchestrates the entire process.
        
        Returns:
            Dict: Complete scraped data
        """
        print("🚀 Starting Victor for President website scraping (Simple Version)...")
        
        # URLs to scrape
        main_urls = [
            f"{self.base_url}/index.html",
            f"{self.base_url}/policies.html"
        ]
        
        # Get paginated URLs
        print("🔍 Discovering paginated pages...")
        paginated_urls = self._discover_paginated_urls()
        all_urls = main_urls + paginated_urls
        
        print(f"📄 Found {len(all_urls)} main pages to scrape")
        
        # Step 1: Scrape main pages and collect article links
        article_links = set()
        
        for url in all_urls:
            try:
                print(f"\n📖 Scraping main page: {url}")
                page_data = self._scrape_main_page(url)
                
                if page_data:
                    self.data["main_pages"].append(page_data)
                    # Collect article links from this page
                    if "article_links" in page_data:
                        article_links.update(page_data["article_links"])
                        print(f"   Found {len(page_data['article_links'])} article links")
                    
                    time.sleep(1)  # Be respectful to the server
                        
            except Exception as e:
                error = f"Error scraping main page {url}: {str(e)}"
                print(f"❌ {error}")
                self.data["errors"].append(error)
        
        print(f"\n🔗 Found {len(article_links)} unique article links to scrape")
        
        # Step 2: Scrape individual articles
        for i, article_url in enumerate(article_links, 1):
            try:
                print(f"📰 Scraping article {i}/{len(article_links)}: {article_url}")
                article_data = self._scrape_article(article_url)
                
                if article_data:
                    # Categorize based on content
                    if self._is_press_release(article_data):
                        self.data["press_releases"].append(article_data)
                        print("   📢 Categorized as: Press Release")
                    else:
                        self.data["news_articles"].append(article_data)
                        print("   📰 Categorized as: News Article")
                
                time.sleep(0.5)  # Rate limiting
                        
            except Exception as e:
                error = f"Error scraping article {article_url}: {str(e)}"
                print(f"❌ {error}")
                self.data["errors"].append(error)
        
        # Step 3: Extract policies from policies page
        print(f"\n📋 Extracting policies...")
        self._extract_policies()
        
        # Update metadata
        self.data["scraping_metadata"]["total_pages_scraped"] = len(self.data["main_pages"])
        self.data["scraping_metadata"]["total_articles_extracted"] = len(self.data["news_articles"]) + len(self.data["press_releases"])
        self.data["scraping_metadata"]["completion_time"] = datetime.now().isoformat()
        
        print(f"\n✅ Scraping completed!")
        print(f"📊 Statistics:")
        print(f"   - Main pages: {len(self.data['main_pages'])}")
        print(f"   - News articles: {len(self.data['news_articles'])}")
        print(f"   - Press releases: {len(self.data['press_releases'])}")
        print(f"   - Policies: {len(self.data['policies'])}")
        print(f"   - Errors: {len(self.data['errors'])}")
        
        return self.data
    
    def _discover_paginated_urls(self) -> List[str]:
        """
        Discover all paginated URLs by checking page2, page3, etc.
        
        Returns:
            List[str]: List of valid paginated URLs
        """
        paginated_urls = []
        
        # Check for pagination (starting from page 2)
        for page_num in range(2, 10):  # Check up to page 10
            page_url = f"{self.base_url}/page{page_num}/"
            
            try:
                response = self.session.head(page_url, timeout=15)
                if response.status_code == 200:
                    paginated_urls.append(page_url)
                    print(f"✅ Found page: page{page_num}")
                else:
                    print(f"🔚 No more pages found (page{page_num} returned {response.status_code})")
                    break
                    
                time.sleep(0.3)  # Small delay between checks
                
            except Exception as e:
                print(f"❌ Error checking page{page_num}: {e}")
                break
                
        return paginated_urls
    
    def _scrape_main_page(self, url: str) -> Optional[Dict]:
        """
        Scrape a main page and extract article links and basic content.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict: Page data with article links
        """
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic page info
            page_data = {
                "url": url,
                "title": self._extract_title(soup),
                "description": self._extract_description(soup),
                "scraped_at": datetime.now().isoformat(),
                "article_links": [],
                "status_code": response.status_code
            }
            
            # Extract article links
            article_links = self._extract_article_links(soup, url)
            page_data["article_links"] = article_links
            
            # Extract any preview content
            previews = self._extract_article_previews(soup)
            page_data["article_previews"] = previews
            
            return page_data
            
        except Exception as e:
            raise Exception(f"Failed to scrape main page {url}: {str(e)}")
    
    def _scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape an individual article for full content.
        
        Args:
            url: Article URL to scrape
            
        Returns:
            Dict: Article data
        """
        if url in self.scraped_urls:
            return None
        
        self.scraped_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            article_data = {
                "url": url,
                "title": self._extract_title(soup),
                "content": self._extract_article_content(soup),
                "summary": self._extract_summary(soup),
                "date": self._extract_date(soup),
                "author": self._extract_author(soup),
                "tags": self._extract_tags(soup),
                "images": self._extract_images(soup, url),
                "scraped_at": datetime.now().isoformat(),
                "status_code": response.status_code,
                "word_count": len(self._extract_article_content(soup).split())
            }
            
            return article_data
            
        except Exception as e:
            raise Exception(f"Failed to scrape article {url}: {str(e)}")
    
    def _extract_policies(self):
        """
        Extract policy information from the policies page.
        """
        policies_url = f"{self.base_url}/policies.html"
        
        try:
            response = self.session.get(policies_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract policy sections
            policies = self._extract_policy_sections(soup)
            self.data["policies"] = policies
            
            print(f"   📋 Extracted {len(policies)} policy sections")
            
        except Exception as e:
            error = f"Error extracting policies: {str(e)}"
            print(f"❌ {error}")
            self.data["errors"].append(error)
    
    def _extract_article_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all article links from a page."""
        links = set()
        
        # Find all links on the page
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Check if it looks like an article URL
            if self._is_article_url(full_url):
                links.add(full_url)
        
        return list(links)
    
    def _extract_article_previews(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract article preview summaries from main pages."""
        previews = []
        
        # Look for common article preview patterns
        for item in soup.find_all(['article', 'div'], class_=True):
            # Skip if class doesn't suggest it's content
            classes = ' '.join(item.get('class', [])).lower()
            if not any(word in classes for word in ['article', 'news', 'post', 'item', 'content', 'summary']):
                continue
                
            title_elem = item.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            text_content = item.get_text(strip=True)
            link_elem = item.find('a', href=True)
            
            if title_elem and len(text_content) > 50:  # Reasonable content length
                preview = {
                    "title": title_elem.get_text(strip=True),
                    "summary": text_content[:300] + "..." if len(text_content) > 300 else text_content,
                    "link": urljoin(self.base_url, link_elem['href']) if link_elem else ""
                }
                previews.append(preview)
        
        return previews
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page/article title."""
        # Try multiple title extraction methods
        for selector in ['h1', 'title', '.title', '.headline', '.article-title', '.post-title']:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 3:  # Valid title length
                    return title
        
        return "No title found"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description."""
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content', '').strip()
        
        # Try og:description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc.get('content', '').strip()
        
        # Fallback to first substantial paragraph
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if len(text) > 50:  # Reasonable description length
                return text[:200] + "..." if len(text) > 200 else text
        
        return ""
    
    def _extract_article_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', '.navigation', '.menu']):
            element.decompose()
        
        # Try to find main content area
        content_selectors = [
            'article',
            '[role="main"]',
            '.content',
            '.article-content',
            '.post-content',
            '.main-content',
            'main',
            '.entry-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                text = content_elem.get_text(separator='\n', strip=True)
                if len(text) > 100:  # Reasonable content length
                    return text
        
        # Fallback: get all paragraphs and meaningful text
        content_parts = []
        for elem in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = elem.get_text(strip=True)
            if len(text) > 20:  # Skip very short text
                content_parts.append(text)
        
        return '\n\n'.join(content_parts) if content_parts else "No content found"
    
    def _extract_summary(self, soup: BeautifulSoup) -> str:
        """Extract article summary or excerpt."""
        # Try various summary selectors
        for selector in ['.summary', '.excerpt', '.lead', '.intro', '.description']:
            summary_elem = soup.select_one(selector)
            if summary_elem:
                return summary_elem.get_text(strip=True)
        
        # Fallback: first paragraph with reasonable length
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if 50 <= len(text) <= 500:  # Good summary length
                return text
        
        return ""
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract publication date."""
        # Try various date selectors
        for selector in ['time', '[datetime]', '.date', '.published', '.post-date', '.article-date']:
            date_elem = soup.select_one(selector)
            if date_elem:
                # Try datetime attribute first
                datetime_attr = date_elem.get('datetime')
                if datetime_attr:
                    return datetime_attr
                # Fallback to text content
                date_text = date_elem.get_text(strip=True)
                if date_text:
                    return date_text
        
        return ""
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract article author."""
        for selector in ['.author', '.by-author', '.writer', '.post-author', '[rel="author"]']:
            author_elem = soup.select_one(selector)
            if author_elem:
                return author_elem.get_text(strip=True)
        
        return ""
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract article tags."""
        tags = []
        
        for selector in ['.tags', '.categories', '.keywords', '.tag-list']:
            tag_container = soup.select_one(selector)
            if tag_container:
                for tag in tag_container.find_all(['a', 'span', 'li']):
                    tag_text = tag.get_text(strip=True)
                    if tag_text and len(tag_text) < 50:  # Reasonable tag length
                        tags.append(tag_text)
        
        return list(set(tags))  # Remove duplicates
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract images from article."""
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                full_url = urljoin(base_url, src)
                # Skip very small images (likely icons/decorative)
                if not any(skip in src.lower() for skip in ['icon', 'logo', 'pixel', '1x1']):
                    images.append({
                        "url": full_url,
                        "alt": img.get('alt', ''),
                        "title": img.get('title', ''),
                        "width": img.get('width', ''),
                        "height": img.get('height', '')
                    })
        
        return images
    
    def _extract_policy_sections(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract policy sections from policies page."""
        policies = []
        
        # Remove navigation and other non-content elements
        for element in soup(['nav', 'header', 'footer', 'aside', '.navigation', '.menu']):
            element.decompose()
        
        # Look for policy sections
        for section in soup.find_all(['section', 'div', 'article'], class_=True):
            # Check if this looks like a policy section
            classes = ' '.join(section.get('class', [])).lower()
            if not any(word in classes for word in ['policy', 'section', 'content', 'main']):
                continue
                
            title_elem = section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            content = section.get_text(separator='\n', strip=True)
            
            if title_elem and len(content) > 100:  # Reasonable policy length
                policy = {
                    "title": title_elem.get_text(strip=True),
                    "content": content,
                    "word_count": len(content.split())
                }
                policies.append(policy)
        
        # If no clear policy sections found, extract all headings and content
        if not policies:
            current_policy = None
            for elem in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div']):
                if elem.name.startswith('h'):  # Heading
                    # Save previous policy
                    if current_policy and len(current_policy['content']) > 100:
                        policies.append(current_policy)
                    
                    # Start new policy
                    current_policy = {
                        "title": elem.get_text(strip=True),
                        "content": "",
                        "word_count": 0
                    }
                elif current_policy:  # Content element
                    text = elem.get_text(strip=True)
                    if text:
                        current_policy['content'] += '\n' + text
            
            # Don't forget the last policy
            if current_policy and len(current_policy['content']) > 100:
                current_policy['word_count'] = len(current_policy['content'].split())
                policies.append(current_policy)
        
        return policies
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL looks like an article URL."""
        if not url.startswith(self.base_url):
            return False
        
        # Skip non-article patterns
        skip_patterns = [
            'javascript:', 'mailto:', '#', '.css', '.js', '.jpg', '.png', '.gif', '.pdf',
            '.ico', '.svg', 'contact', 'about', 'privacy', 'terms'
        ]
        
        url_lower = url.lower()
        for pattern in skip_patterns:
            if pattern in url_lower:
                return False
        
        # Basic URL structure check
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Skip homepage and main directories
        if path in ['/', '/index.html', '/policies.html']:
            return False
        
        # Must have some path content
        return len(path) > 1
    
    def _is_press_release(self, article_data: Dict) -> bool:
        """Determine if an article is a press release."""
        text_to_check = (
            article_data.get('title', '') + ' ' +
            article_data.get('content', '') + ' ' +
            article_data.get('summary', '')
        ).lower()
        
        press_release_indicators = [
            'press release', 'announces', 'statement', 'official', 'campaign',
            'for immediate release', 'media contact'
        ]
        
        return any(indicator in text_to_check for indicator in press_release_indicators)
    
    def get_latest_content(self) -> Dict:
        """
        Get the latest news and press releases without full scraping.
        
        Returns:
            Dict: Latest content with news articles and press releases
        """
        print("🔄 Getting latest Victor campaign content...")
        
        latest_data = {
            "news_articles": [],
            "press_releases": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Get main page to find latest articles
            main_url = f"{self.base_url}/index.html"
            response = self.session.get(main_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article links
            article_links = self._extract_article_links(soup, main_url)
            print(f"📰 Found {len(article_links)} articles to process")
            
            # Process each article
            for i, article_url in enumerate(article_links[:10], 1):  # Limit to 10 latest
                try:
                    print(f"   Processing article {i}: {article_url}")
                    article_data = self._scrape_article(article_url)
                    
                    if article_data:
                        # Categorize and add to appropriate list
                        if self._is_press_release(article_data):
                            latest_data["press_releases"].append(article_data)
                        else:
                            latest_data["news_articles"].append(article_data)
                    
                    time.sleep(0.3)  # Rate limiting
                    
                except Exception as e:
                    print(f"   ❌ Error processing {article_url}: {e}")
                    continue
            
            print(f"✅ Latest content retrieved: {len(latest_data['news_articles'])} news, {len(latest_data['press_releases'])} press releases")
            return latest_data
            
        except Exception as e:
            print(f"❌ Error getting latest content: {e}")
            return latest_data

    def save_data(self, filename: str = None) -> str:
        """
        Save scraped data to JSON file.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"victor_campaign_data_{timestamp}.json"
        
        filepath = Path(filename)
        
        # Ensure the data is JSON serializable
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Data saved to: {filepath.absolute()}")
            return str(filepath.absolute())
            
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return ""


def main():
    """Main execution function."""
    print("🗳️  Victor for President Campaign Website Scraper")
    print("🔧 Simple Version (requests + BeautifulSoup)")
    print("=" * 60)
    
    scraper = VictorWebScraperSimple()
    
    try:
        # Scrape all data
        data = scraper.scrape_all()
        
        # Save to file
        output_file = scraper.save_data()
        
        if output_file:
            print(f"\n🎉 Scraping completed successfully!")
            print(f"📁 Output file: {output_file}")
            print(f"📊 Final statistics:")
            print(f"   - Total pages scraped: {data['scraping_metadata']['total_pages_scraped']}")
            print(f"   - Total articles extracted: {data['scraping_metadata']['total_articles_extracted']}")
            print(f"   - News articles: {len(data['news_articles'])}")
            print(f"   - Press releases: {len(data['press_releases'])}")
            print(f"   - Policies: {len(data['policies'])}")
            
            if data['errors']:
                print(f"⚠️  Errors encountered: {len(data['errors'])}")
                for error in data['errors']:
                    print(f"   - {error}")
        else:
            print("\n❌ Failed to save data!")
            return 1
        
    except Exception as e:
        print(f"❌ Fatal error during scraping: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)