#!/usr/bin/env python3
"""
Post Orchestrator for Victor Campaign Automated Content Generation

This orchestrator coordinates the complete workflow for automated social media
content generation and posting for Victor Hawthorne's presidential campaign.

Workflow:
1. Crawl News and Press Releases from Victor's campaign website
2. Get trending posts from the social media platform
3. Combine the data and generate viral social media content using Azure OpenAI
4. Post the generated content to the social media platform

Features:
- Automated content pipeline
- Error handling and retry logic
- Logging and status reporting
- Configurable content generation parameters
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import our custom modules
from news_press_crawler import NewsPressCrawler
from azure_openai_client import VictorCampaignAzureOpenAI
from social_helper import TwooterTeamBot
import random

class PostOrchestrator:
    """
    Main orchestrator class that coordinates the automated content generation
    and posting workflow for Victor Hawthorne's campaign.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Post Orchestrator.
        
        Args:
            config_path (Optional[str]): Path to configuration file for social bot
        """
        self.config_path = config_path
        self.crawler = None
        self.ai_client = None
        self.social_bot = None
        
        # Initialize components
        self._initialize_components()
        
        print("🎭 Post Orchestrator initialized")
    
    def _initialize_components(self):
        """Initialize all required components."""
        try:
            # Initialize News/Press crawler
            self.crawler = NewsPressCrawler()
            print("✅ News/Press crawler initialized")
            
            # Initialize Azure OpenAI client
            self.ai_client = VictorCampaignAzureOpenAI()
            print("✅ Azure OpenAI client initialized")
            
            # Initialize social media bot
            self.social_bot = TwooterTeamBot(self.config_path)
            print("✅ Social media bot initialized")
            
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            raise
    
    def get_news_and_press_data(self) -> Dict[str, Any]:
        """
        First function: Call news_press_crawler and get the data.
        
        Returns:
            Dict[str, Any]: News and press release data from Victor's campaign
        """
        print("\n📰 Step 1: Fetching News and Press Releases...")
        print("=" * 50)
        
        try:
            # Use the crawler to get latest news and press releases
            data = self.crawler.crawl_news_and_press()
            
            if data and data.get('main'):
                articles_count = len(data['main'])
                print(f"✅ Successfully retrieved {articles_count} articles")
                
                # Display brief summary of articles
                for i, article in enumerate(data['main'][:3], 1):  # Show first 3
                    title = article['title'][:60] + "..." if len(article['title']) > 60 else article['title']
                    print(f"   {i}. {title}")
                
                if len(data['main']) > 3:
                    print(f"   ... and {len(data['main']) - 3} more articles")
                
                return data
            else:
                print("⚠️  No articles found from news/press crawler")
                return {"main": [], "metadata": {"error": "No articles found"}}
                
        except Exception as e:
            print(f"❌ Error fetching news/press data: {e}")
            return {"main": [], "metadata": {"error": str(e)}}
    
    def get_trending_social_data(self, limit: int = 5) -> Dict[str, Any]:
        """
        Second function: Call social_helper.py --trending and get latest trending data.
        
        Args:
            limit (int): Number of trending posts to retrieve (default: 5)
            
        Returns:
            Dict[str, Any]: Trending posts data from the platform
        """
        print(f"\n📈 Step 2: Fetching Trending Social Media Posts...")
        print("=" * 50)
        
        try:
            # Start the social bot if not already started
            if not self.social_bot.running:
                if not self.social_bot.start():
                    raise Exception("Failed to start social media bot")
            
            # Get trending posts using the social bot's method
            trending_data = self.social_bot.get_trending_posts(limit=limit)
            
            if trending_data and trending_data.get('data'):
                posts_count = len(trending_data['data'])
                print(f"✅ Successfully retrieved {posts_count} trending posts")
                
                # Display brief summary of trending posts
                for i, post in enumerate(trending_data['data'][:3], 1):  # Show first 3
                    author = post.get('author', {}).get('username', 'Unknown')
                    content_preview = post.get('content', '')[:50] + "..." if len(post.get('content', '')) > 50 else post.get('content', '')
                    print(f"   {i}. @{author}: {content_preview}")
                
                if len(trending_data['data']) > 3:
                    print(f"   ... and {len(trending_data['data']) - 3} more posts")
                
                return trending_data
            else:
                print("⚠️  No trending posts found")
                return {"data": [], "metadata": {"error": "No trending posts found"}}
                
        except Exception as e:
            print(f"❌ Error fetching trending social data: {e}")
            return {"data": [], "metadata": {"error": str(e)}}
    
    def generate_social_content(self, news_data: Dict[str, Any], 
                              trending_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Third function: Loop through each news item, concatenate with all trending data,
        and generate social media content for each news article.
        
        Args:
            news_data (Dict[str, Any]): News and press release data
            trending_data (Dict[str, Any]): Trending social media posts data
            
        Returns:
            List[Dict[str, Any]]: List of generated social media posts with metadata
        """
        print(f"\n🤖 Step 3: Generating Social Media Content...")
        print("=" * 50)
        
        generated_posts = []
        
        try:
            news_articles = news_data.get('main', [])
            
            if not news_articles:
                print("⚠️  No news articles found. Creating fallback post...")
                fallback_msg = "🇺🇸 Victor Hawthorne for President! Join the movement for fairness, opportunity, and a sustainable future. #VictorForPresident #FairnessForAll #ClimateAction"
                generated_posts.append({
                    "content": fallback_msg,
                    "news_title": "Fallback Message",
                    "success": True
                })
                return generated_posts
            
            print(f"📰 Processing {len(news_articles)} news articles...")
            
            # Loop through each news article
            for i, article in enumerate(news_articles, 1):
                try:
                    print(f"\n📝 Generating content for article {i}/{len(news_articles)}: {article.get('title', 'Unknown')[:50]}...")
                    
                    # Prepare content for this specific article + all trending data
                    combined_content = self._prepare_content_for_ai_single_article(article, trending_data)
                    
                    print(f"   📝 Prepared {len(combined_content)} characters for AI processing")
                    
                    # Generate social media post using Azure OpenAI
                    generated_post = self.ai_client.generate_social_post(combined_content)
                    
                    if generated_post:
                        print(f"   ✅ Generated post ({len(generated_post)} characters)")
                        print(f"   📱 Content: \"{generated_post[:100]}{'...' if len(generated_post) > 100 else ''}\"")
                        
                        generated_posts.append({
                            "content": generated_post,
                            "news_title": article.get('title', 'Unknown'),
                            "news_id": i,
                            "success": True
                        })
                    else:
                        print(f"   ❌ Failed to generate content for article {i}")
                        generated_posts.append({
                            "content": f"🇺🇸 Victor Hawthorne: {article.get('title', 'Latest Update')[:100]}... #VictorForPresident",
                            "news_title": article.get('title', 'Unknown'),
                            "news_id": i,
                            "success": False,
                            "error": "No content generated"
                        })
                
                except Exception as e:
                    print(f"   ❌ Error generating content for article {i}: {e}")
                    generated_posts.append({
                        "content": f"🇺🇸 Victor Hawthorne: {article.get('title', 'Latest Update')[:100]}... #VictorForPresident",
                        "news_title": article.get('title', 'Unknown'),
                        "news_id": i,
                        "success": False,
                        "error": str(e)
                    })
            
            successful_posts = sum(1 for post in generated_posts if post.get('success'))
            print(f"\n✅ Content generation complete: {successful_posts}/{len(generated_posts)} successful")
            
            return generated_posts
                
        except Exception as e:
            print(f"❌ Fatal error generating social content: {e}")
            # Return a single fallback message
            fallback_msg = "🇺🇸 Victor Hawthorne for President! Join the movement for fairness, opportunity, and a sustainable future. #VictorForPresident #FairnessForAll #ClimateAction"
            return [{
                "content": fallback_msg,
                "news_title": "Fallback Message",
                "success": False,
                "error": str(e)
            }]
    
    def _prepare_content_for_ai_single_article(self, article: Dict[str, Any], 
                                             trending_data: Dict[str, Any]) -> str:
        """
        Prepare content for AI generation using a single news article and all trending data.
        
        Args:
            article (Dict[str, Any]): Single news article data
            trending_data (Dict[str, Any]): All trending social media posts data
            
        Returns:
            str: Combined and formatted content for AI processing
        """
        content_parts = []
        
        # Add specific Victor Hawthorne article information
        content_parts.append("Victor Hawthorne Press Release:")
        title = article.get('title', 'No title')
        summary = article.get('summary', article.get('content', ''))[:300]  # Limit summary length
        content_parts.append(f"\nTitle: {title}")
        content_parts.append(f"Summary: {summary}")
        
        # Add trending social media posts
        content_parts.append("\n\nTrending Social Media Posts:")
        
        if trending_data.get('data'):
            for i, post in enumerate(trending_data['data'][:5], 1):  # Use top 5 trending posts
                author = post.get('author', {}).get('username', 'Unknown')
                content = post.get('content', '')[:150]  # Limit content length
                content_parts.append(f"\n{i}. @{author}: {content}")
        else:
            content_parts.append("\nNo trending posts available.")
        
        # Add campaign themes
        content_parts.append("\n\nVictor Hawthorne Campaign Themes:")
        content_parts.append("- Free tertiary education and expanded vocational grants")
        content_parts.append("- Progressive taxation for fairness")
        content_parts.append("- Aggressive action on climate change")
        content_parts.append("- Ending offshore drilling")
        content_parts.append("- Strengthening worker protections")
        content_parts.append("- Supporting renters' rights")
        
        combined_content = ''.join(content_parts)
        
        # Ensure content isn't too long for the AI model
        if len(combined_content) > 2000:
            combined_content = combined_content[:2000] + "..."
        
        return combined_content

    def _prepare_content_for_ai(self, news_data: Dict[str, Any], 
                               trending_data: Dict[str, Any]) -> str:
        """
        Prepare and concatenate news and trending data for AI content generation.
        
        Args:
            news_data (Dict[str, Any]): News and press release data
            trending_data (Dict[str, Any]): Trending social media posts data
            
        Returns:
            str: Combined and formatted content for AI processing
        """
        content_parts = []
        
        # Add Victor Hawthorne press release information
        content_parts.append("Victor Hawthorne Press Release Information:")
        
        if news_data.get('main'):
            for i, article in enumerate(news_data['main'][:3], 1):  # Use top 3 articles
                title = article.get('title', 'No title')
                summary = article.get('summary', article.get('content', ''))[:200]  # Limit summary length
                content_parts.append(f"\n{i}. {title}")
                content_parts.append(f"   Summary: {summary}")
        else:
            content_parts.append("\nNo recent press releases available.")
        
        # Add trending social media posts
        content_parts.append("\n\nTrending Social Media Posts:")
        
        if trending_data.get('data'):
            for i, post in enumerate(trending_data['data'][:5], 1):  # Use top 5 trending posts
                author = post.get('author', {}).get('username', 'Unknown')
                content = post.get('content', '')[:150]  # Limit content length
                content_parts.append(f"\n{i}. @{author}: {content}")
        else:
            content_parts.append("\nNo trending posts available.")
        
        # Add campaign themes
        content_parts.append("\n\nVictor Hawthorne Campaign Themes:")
        content_parts.append("- Free tertiary education and expanded vocational grants")
        content_parts.append("- Progressive taxation for fairness")
        content_parts.append("- Aggressive action on climate change")
        content_parts.append("- Ending offshore drilling")
        content_parts.append("- Strengthening worker protections")
        content_parts.append("- Supporting renters' rights")
        
        combined_content = ''.join(content_parts)
        
        # Ensure content isn't too long for the AI model
        if len(combined_content) > 2000:
            combined_content = combined_content[:2000] + "..."
        
        return combined_content
    
    def post_social_content(self, generated_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fourth function: Loop through each generated post and post them individually.
        
        Args:
            generated_posts (List[Dict[str, Any]]): List of generated social media posts
            
        Returns:
            List[Dict[str, Any]]: List of posting results for each post
        """
        print(f"\n📤 Step 4: Posting Social Media Content...")
        print("=" * 50)
        
        posting_results = []
        
        try:
            # Ensure social bot is started
            if not self.social_bot.running:
                if not self.social_bot.start():
                    raise Exception("Failed to start social media bot for posting")
            
            print(f"📝 Posting {len(generated_posts)} social media posts...")
            print(f"⚠️  Note: Using rate limiting delays to avoid API limits")
            
            # Loop through each generated post
            for i, post_data in enumerate(generated_posts, 1):
                try:
                    content = post_data.get('content', '')
                    news_title = post_data.get('news_title', 'Unknown')
                    
                    print(f"\n📤 Posting {i}/{len(generated_posts)}: {news_title[:50]}...")
                    print(f"   📱 Content: \"{content[:100]}{'...' if len(content) > 100 else ''}\"")
                    
                    # Retry logic for rate limiting
                    max_retries = 3
                    retry_count = 0
                    posted = False
                    
                    while retry_count < max_retries and not posted:
                        try:
                            # Create the post using the social bot
                            post_result = self.social_bot.create_post(content)
                            
                            # Handle different response formats
                            if post_result:
                                # Check if response has success flag (expected format)
                                if post_result.get('success'):
                                    post_id = post_result.get('data', {}).get('id', 'Unknown')
                                    print(f"   ✅ Successfully posted! Post ID: {post_id}")
                                    
                                    posting_results.append({
                                        "success": True,
                                        "post_id": post_id,
                                        "content": content,
                                        "news_title": news_title,
                                        "news_id": post_data.get('news_id', i),
                                        "response": post_result
                                    })
                                    posted = True
                                # Check if response contains post data directly (actual format)
                                elif post_result.get('id'):
                                    post_id = post_result.get('id', 'Unknown')
                                    print(f"   ✅ Successfully posted! Post ID: {post_id}")
                                    
                                    posting_results.append({
                                        "success": True,
                                        "post_id": post_id,
                                        "content": content,
                                        "news_title": news_title,
                                        "news_id": post_data.get('news_id', i),
                                        "response": {"success": True, "data": post_result}
                                    })
                                    posted = True
                                # Check if response has 'data' field with post info
                                elif post_result.get('data', {}).get('id'):
                                    post_id = post_result.get('data', {}).get('id', 'Unknown')
                                    print(f"   ✅ Successfully posted! Post ID: {post_id}")
                                    
                                    posting_results.append({
                                        "success": True,
                                        "post_id": post_id,
                                        "content": content,
                                        "news_title": news_title,
                                        "news_id": post_data.get('news_id', i),
                                        "response": {"success": True, "data": post_result.get('data')}
                                    })
                                    posted = True
                                else:
                                    error_msg = post_result.get('error', 'Unknown response format')
                                    print(f"   ❌ Failed to post: {error_msg}")
                                    break  # Don't retry for non-rate-limit errors
                            else:
                                print(f"   ❌ Failed to post: No response from server")
                                break  # Don't retry for no response
                        
                        except Exception as post_error:
                            error_str = str(post_error)
                            
                            # Check if it's a rate limiting error
                            if "429" in error_str or "Too Many Requests" in error_str:
                                retry_count += 1
                                if retry_count < max_retries:
                                    wait_time = 30 * (2 ** (retry_count - 1))  # Exponential backoff: 30s, 60s, 120s
                                    print(f"   ⏳ Rate limit hit. Waiting {wait_time}s before retry {retry_count}/{max_retries}...")
                                    time.sleep(wait_time)
                                else:
                                    print(f"   ❌ Max retries reached. Skipping this post.")
                                    posting_results.append({
                                        "success": False,
                                        "error": f"Rate limit exceeded after {max_retries} retries",
                                        "content": content,
                                        "news_title": news_title,
                                        "news_id": post_data.get('news_id', i)
                                    })
                            else:
                                # Non-rate-limit error, don't retry
                                print(f"   ❌ Error posting content: {post_error}")
                                posting_results.append({
                                    "success": False,
                                    "error": str(post_error),
                                    "content": content,
                                    "news_title": news_title,
                                    "news_id": post_data.get('news_id', i)
                                })
                                break
                    
                    # If we haven't posted yet and exhausted retries
                    if not posted and retry_count >= max_retries:
                        posting_results.append({
                            "success": False,
                            "error": "Failed to post after maximum retries",
                            "content": content,
                            "news_title": news_title,
                            "news_id": post_data.get('news_id', i)
                        })
                    
                    # Add longer delay between posts to avoid rate limiting
                    if i < len(generated_posts):
                        wait_time = 15  # 15 seconds between posts
                        print(f"   ⏸️  Waiting {wait_time} seconds before next post...")
                        time.sleep(wait_time)
                
                except Exception as e:
                    print(f"   ❌ Error posting content {i}: {e}")
                    posting_results.append({
                        "success": False,
                        "error": str(e),
                        "content": post_data.get('content', ''),
                        "news_title": post_data.get('news_title', 'Unknown'),
                        "news_id": post_data.get('news_id', i)
                    })
            
            # Summary
            successful_posts = sum(1 for result in posting_results if result.get('success'))
            print(f"\n📊 Posting Summary: {successful_posts}/{len(posting_results)} posts successful")
            
            return posting_results
                
        except Exception as e:
            print(f"❌ Fatal error posting social content: {e}")
            return [{
                "success": False,
                "error": str(e),
                "content": "",
                "news_title": "Error",
                "news_id": 0
            }]
    
    def run_complete_workflow(self, trending_limit: int = 5, 
                            save_data: bool = True, max_posts: int = None) -> Dict[str, Any]:
        """
        Execute the complete automated content generation and posting workflow.
        
        Args:
            trending_limit (int): Number of trending posts to fetch (default: 5)
            save_data (bool): Whether to save intermediate data to files (default: True)
            max_posts (int): Maximum number of posts to publish (default: None = all)
            
        Returns:
            Dict[str, Any]: Complete workflow results and metadata
        """
        print("🚀 Starting Complete Automated Content Workflow")
        print("=" * 60)
        
        workflow_start = datetime.now()
        results = {
            "workflow_id": f"victor_campaign_{workflow_start.strftime('%Y%m%d_%H%M%S')}",
            "start_time": workflow_start.isoformat(),
            "steps": {},
            "success": False,
            "errors": []
        }
        
        try:
            # Step 1: Get news and press releases
            print("\n🎬 Executing automated content generation workflow...")
            news_data = self.get_news_and_press_data()
            results["steps"]["news_data"] = {
                "success": bool(news_data.get('main')),
                "articles_count": len(news_data.get('main', [])),
                "timestamp": datetime.now().isoformat()
            }
            
            
            # Step 2: Get trending social media posts
            trending_data = self.get_trending_social_data(limit=trending_limit)
            print(f'Trending Data : {trending_data}')
            results["steps"]["trending_data"] = {
                "success": bool(trending_data.get('data')),
                "posts_count": len(trending_data.get('data', [])),
                "timestamp": datetime.now().isoformat()
            }
            
            
            # Step 3: Generate social media content (now returns a list)
            generated_posts = self.generate_social_content(news_data, trending_data)
            results["steps"]["content_generation"] = {
                "success": bool(generated_posts and any(post.get('success') for post in generated_posts)),
                "posts_generated": len(generated_posts) if generated_posts else 0,
                "successful_generations": sum(1 for post in generated_posts if post.get('success')) if generated_posts else 0,
                "generated_posts": generated_posts,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 4: Post the generated content (now handles a list)
            # Apply max_posts limit if specified
            posts_to_publish = generated_posts
            if max_posts and len(generated_posts) > max_posts:
                posts_to_publish = generated_posts[:max_posts]
                print(f"📌 Limiting posts to {max_posts} out of {len(generated_posts)} generated posts")
            
            posting_results = self.post_social_content(posts_to_publish)
            results["steps"]["posting"] = {
                "success": bool(posting_results and any(post.get('success') for post in posting_results)),
                "posts_attempted": len(posting_results) if posting_results else 0,
                "successful_posts": sum(1 for post in posting_results if post.get('success')) if posting_results else 0,
                "posting_results": posting_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Determine overall success
            all_steps_successful = all(
                step_result.get('success', False) 
                for step_result in results["steps"].values()
            )
            
            results["success"] = all_steps_successful
            results["end_time"] = datetime.now().isoformat()
            results["duration_seconds"] = (datetime.now() - workflow_start).total_seconds()
            
            # Final status report
            print(f"\n🎯 Workflow Complete!")
            print("=" * 30)
            print(f"✅ Overall Success: {results['success']}")
            print(f"⏱️  Duration: {results['duration_seconds']:.1f} seconds")
            print(f"📊 Steps Results:")
            for step_name, step_result in results["steps"].items():
                status = "✅" if step_result.get('success') else "❌"
                print(f"   {status} {step_name.replace('_', ' ').title()}")
            
            if results["success"]:
                successful_posts = results["steps"]["posting"]["successful_posts"]
                total_posts = results["steps"]["posting"]["posts_attempted"]
                print(f"\n🎉 Workflow completed successfully!")
                print(f"📊 Summary: {successful_posts}/{total_posts} posts published")
                
                # Show sample of posted content
                if posting_results and successful_posts > 0:
                    print(f"📱 Sample posted content:")
                    for i, post in enumerate(posting_results[:3], 1):
                        if post.get('success'):
                            content = post.get('content', '')[:100] + "..." if len(post.get('content', '')) > 100 else post.get('content', '')
                            print(f"   {i}. \"{content}\" (Post ID: {post.get('post_id')})")
            else:
                print(f"\n⚠️  Some steps failed. Check individual step results.")
            
            return results
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Fatal workflow error: {error_msg}")
            results["errors"].append(error_msg)
            results["success"] = False
            results["end_time"] = datetime.now().isoformat()
            results["duration_seconds"] = (datetime.now() - workflow_start).total_seconds()
            return results
        
        finally:
            # Cleanup: Stop social bot if it was started
            if self.social_bot and self.social_bot.running:
                self.social_bot.stop()
                print("🛑 Social bot stopped")
    
    def test_all_components(self) -> Dict[str, bool]:
        """
        Test all components to ensure they're working properly.
        
        Returns:
            Dict[str, bool]: Test results for each component
        """
        print("🧪 Testing All Components")
        print("=" * 30)
        
        test_results = {}
        
        # Test 1: News/Press Crawler
        print("\n1. Testing News/Press Crawler...")
        try:
            # Quick test - just check if we can initialize and connect
            test_crawler = NewsPressCrawler()
            test_results["news_crawler"] = True
            print("   ✅ News/Press crawler: OK")
        except Exception as e:
            test_results["news_crawler"] = False
            print(f"   ❌ News/Press crawler: FAILED - {e}")
        
        # Test 2: Azure OpenAI Client
        print("\n2. Testing Azure OpenAI Client...")
        try:
            if self.ai_client.test_connection():
                test_results["azure_openai"] = True
                print("   ✅ Azure OpenAI client: OK")
            else:
                test_results["azure_openai"] = False
                print("   ❌ Azure OpenAI client: FAILED - Connection test failed")
        except Exception as e:
            test_results["azure_openai"] = False
            print(f"   ❌ Azure OpenAI client: FAILED - {e}")
        
        # Test 3: Social Media Bot
        print("\n3. Testing Social Media Bot...")
        try:
            if self.social_bot._validate_setup():
                test_results["social_bot"] = True
                print("   ✅ Social media bot: OK")
            else:
                test_results["social_bot"] = False
                print("   ❌ Social media bot: FAILED - Configuration invalid")
        except Exception as e:
            test_results["social_bot"] = False
            print(f"   ❌ Social media bot: FAILED - {e}")
        
        # Overall result
        all_tests_passed = all(test_results.values())
        print(f"\n🎯 Overall Test Result: {'✅ PASS' if all_tests_passed else '❌ FAIL'}")
        
        return test_results


def main():
    """
    Main execution function with command-line interface.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Victor Campaign Post Orchestrator - Automated Content Generation and Posting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --run-workflow                    # Run complete automation workflow
  %(prog)s --test-components                 # Test all components
  %(prog)s --news-only                       # Fetch news/press releases only
  %(prog)s --trending-only                   # Fetch trending posts only
  %(prog)s --generate-only                   # Generate content without posting
  %(prog)s --trending-limit 10               # Fetch 10 trending posts
  %(prog)s --config config.json              # Use custom config file
        """
    )
    
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--run-workflow', action='store_true', 
                       help='Run the complete automated workflow')
    parser.add_argument('--test-components', action='store_true',
                       help='Test all components and exit')
    parser.add_argument('--news-only', action='store_true',
                       help='Fetch news/press releases only')
    parser.add_argument('--trending-only', action='store_true',
                       help='Fetch trending posts only')
    parser.add_argument('--generate-only', action='store_true',
                       help='Generate content but do not post')
    parser.add_argument('--trending-limit', type=int, default=5,
                       help='Number of trending posts to fetch (default: 5)')
    parser.add_argument('--max-posts', type=int, 
                       help='Maximum number of posts to publish (default: all)')
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save intermediate data to files')
    
    args = parser.parse_args()
    
    try:
        # Initialize orchestrator
        orchestrator = PostOrchestrator(args.config)
        
        # Handle test components
        if args.test_components:
            test_results = orchestrator.test_all_components()
            return 0 if all(test_results.values()) else 1
        
        # Handle individual component testing
        if args.news_only:
            news_data = orchestrator.get_news_and_press_data()
            print(f"\n📊 Retrieved {len(news_data.get('main', []))} articles")
            return 0
        
        if args.trending_only:
            trending_data = orchestrator.get_trending_social_data(limit=args.trending_limit)
            print(f"\n📊 Retrieved {len(trending_data.get('data', []))} trending posts")
            return 0
        
        if args.generate_only:
            news_data = orchestrator.get_news_and_press_data()
            trending_data = orchestrator.get_trending_social_data(limit=args.trending_limit)
            generated_posts = orchestrator.generate_social_content(news_data, trending_data)
            
            print(f"\n🤖 Generated {len(generated_posts)} social media posts:")
            for i, post in enumerate(generated_posts, 1):
                status = "✅" if post.get('success') else "❌"
                content = post.get('content', '')[:100] + "..." if len(post.get('content', '')) > 100 else post.get('content', '')
                print(f"   {status} {i}. \"{content}\"")
            return 0
        
        # Default: Run complete workflow
        if args.run_workflow or len(sys.argv) == 1:
            runcount = 0
            # Run in endless loop with random delays
            while True:
                runcount += 1
                try:
                    results = orchestrator.run_complete_workflow(
                        trending_limit=args.trending_limit,
                        save_data=not args.no_save,
                        max_posts=args.max_posts
                    )
                    
                    # Random delay between 5 and 30 seconds
                    delay = random.randint(5, 30)
                    print(f"\n⏰ Waiting {delay} seconds before next workflow run...")
                    print ("*****************************")
                    print (f"Completed run **{runcount}**")
                    print ("*****************************")
                    time.sleep(delay)
                except KeyboardInterrupt:
                    print("\n👋 Workflow loop interrupted by user")
                    break
                except Exception as e:
                    print(f"❌ Error in workflow loop: {e}")
                    # Wait before retrying on error
                    delay = random.randint(10, 20)
                    print(f"⏰ Waiting {delay} seconds before retry...")
                    time.sleep(delay)
            # return 0 if results.get('success') else 1
        
        # If no specific command, show help
        parser.print_help()
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Workflow interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)