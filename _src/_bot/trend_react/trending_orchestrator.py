#!/usr/bin/env python3
"""
Trending Content Orchestrator for Victor Hawthorne Campaign

This module orchestrates engagement with trending content on the Twooter platform.
It discovers trending hashtags, finds associated posts, and engages with them
through likes, reposts, and AI-generated replies to boost Victor's campaign visibility.
"""

from trending_extractor import TrendingHashtagExtractor
from azure_openai_client import VictorCampaignTrendingAI
from auth_manager import AuthenticationManager
from posting_manager import PostingManager
import time
import random


def engage_with_post(posting_manager: PostingManager, post_id: int) -> dict:
    """
    Engage with a specific post through likes and reposts.
    
    Args:
        posting_manager (PostingManager): The authenticated posting manager instance
        post_id (int): The ID of the post to engage with
        
    Returns:
        dict: Results of engagement operations
    """
    results = {
        'like': False,
        'repost': False,
        'errors': []
    }
    
    try:
        # Like the post
        try:
            like_result = posting_manager.like_post(post_id)
            if like_result:
                results['like'] = True
                print(f"   👍 Successfully liked post {post_id}")
            else:
                print(f"   ❌ Failed to like post {post_id}")
        except Exception as e:
            error_msg = f"Error liking post {post_id}: {e}"
            results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        
        # Small delay between operations
        time.sleep(2)
        
        # Repost the post
        try:
            repost_result = posting_manager.repost(post_id)
            if repost_result:
                results['repost'] = True
                print(f"   🔄 Successfully reposted post {post_id}")
            else:
                print(f"   ❌ Failed to repost post {post_id}")
        except Exception as e:
            error_msg = f"Error reposting post {post_id}: {e}"
            results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        
        # Summary of operations
        successful_ops = sum([results['like'], results['repost']])
        print(f"   📊 Engagement complete: {successful_ops}/2 operations successful")
        
    except Exception as e:
        error_msg = f"Error in engage_with_post: {e}"
        results['errors'].append(error_msg)
        print(f"   ❌ {error_msg}")
    
    return results


def reply_to_post(posting_manager: PostingManager, post_id: int, reply_content: str) -> tuple[bool, int]:
    """
    Reply to a specific post using the generated AI content with rate limiting.
    
    Args:
        posting_manager (PostingManager): The authenticated posting manager instance
        post_id (int): The ID of the original post to reply to
        reply_content (str): The AI-generated reply content
        
    Returns:
        tuple[bool, int]: (success, reply_id) - True if reply posted successfully and reply ID
    """
    max_retries = 3
    base_delay = 5  # Start with 5 seconds for rate limiting
    
    for attempt in range(max_retries):
        try:
            # Create reply to the original post
            result = posting_manager.create_post(
                content=reply_content,
                parent_id=post_id
            )
            
            # Check if result contains data (indicates success)
            if result and result.get('data'):
                reply_id = result.get('data', {}).get('id', None)
                print(f"   ✅ Successfully replied to post {post_id} with reply ID: {reply_id}")
                return True, reply_id
            else:
                print(f"   ❌ Failed to reply to post {post_id}: No data in response")
                return False, None
                
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a rate limiting error (429)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                if attempt < max_retries - 1:
                    # Calculate exponential backoff delay with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(1, 5)
                    print(f"   ⏳ Rate limited (429). Waiting {delay:.1f}s before retry {attempt + 2}/{max_retries}...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"   ❌ Max retries reached for post {post_id} due to rate limiting")
                    return False, None
            else:
                print(f"   ❌ Error replying to post {post_id}: {e}")
                return False, None
    
    return False, None


def process_trending_content(max_hashtags: int = 15, max_posts_per_hashtag: int = 50):
    """
    Process trending content and engage with relevant posts.
    
    This function performs the complete workflow:
    1. Extracts trending hashtags relevant to Victor's campaign
    2. For each relevant hashtag, gets associated posts
    3. Engages with posts through likes and reposts
    4. Generates AI replies to posts and posts them
    
    Args:
        max_hashtags (int, optional): Maximum number of hashtags to process
        max_posts_per_hashtag (int, optional): Maximum number of posts per hashtag
    """
    # Initialize extractor and login
    extractor = TrendingHashtagExtractor()
    if not extractor.login():
        print("❌ Cannot proceed without authentication")
        return
    
    # Initialize Azure OpenAI client
    ai_client = VictorCampaignTrendingAI()
    
    try:
        # Get campaign-relevant trending content
        trending_content = extractor.get_campaign_trending_content(
            hashtag_limit=max_hashtags * 2,  # Get more to filter from
            posts_per_hashtag=max_posts_per_hashtag
        )
        
        if not trending_content['hashtag_posts']:
            print("ℹ️ No campaign-relevant trending content found")
            return
        
        print(f"\n🎯 Processing {len(trending_content['hashtag_posts'])} trending hashtags...")
        
        total_processed = 0
        successful_engagements = 0
        successful_replies = 0
        
        # Process each hashtag and its posts
        for hashtag, posts in trending_content['hashtag_posts'].items():
            print(f"\n📈 Processing hashtag: {hashtag}")
            print(f"   📱 Found {len(posts)} posts to engage with")
            
            # Limit posts per hashtag to avoid overwhelming
            posts_to_process = posts[:max_posts_per_hashtag]
            
            for idx, post in enumerate(posts_to_process, 1):
                total_processed += 1
                try:
                    print(f"\n📝 Processing post {idx}/{len(posts_to_process)} in {hashtag}...")
                    
                    # Extract post details
                    post_id = post.get('id', 'Unknown')
                    post_content = post.get('content', '')
                    author = post.get('author', {}).get('username', 'Unknown')
                    
                    print(f"   👤 Author: @{author}")
                    print(f"   📱 Content: {post_content[:100]}...")
                    
                    # Engage with the post (like and repost)
                    print(f"   💫 Engaging with post (like & repost)...")
                    time.sleep(random.randint(1, 10))
                    engagement_results = engage_with_post(extractor.posting_manager, int(post_id))
                    
                    if engagement_results['like'] or engagement_results['repost']:
                        successful_engagements += 1
                        print(f"   ✅ Post engagement successful")
                    
                    # Generate AI reply
                    reply_content_prompt = f"""
                    Trending Post by @{author}: {post_content}
                    Hashtag: {hashtag}
                    
                    Generate a supportive response that promotes Victor Hawthorne's campaign themes
                    and engages positively with this trending content.
                    """
                    
                    print(f"   🤖 Generating AI reply...")
                    reply = ai_client.generate_trending_response(post_content, hashtag)
                    
                    # Ensure the reply is under 255 characters
                    if len(reply) > 255:
                        reply = reply[:252] + "..."
                    
                    print(f"   ✅ Generated reply ({len(reply)} chars): {reply}")
                    
                    # Post the reply
                    print(f"   📤 Posting reply...")
                    time.sleep(random.randint(1, 10))
                    success, reply_id = reply_to_post(extractor.posting_manager, int(post_id), reply)
                    
                    if success:
                        successful_replies += 1
                        print(f"   🎉 Successfully posted reply!")
                    else:
                        print(f"   ⚠️  Generated reply but failed to post it")
                    
                    # Add delay between posts to prevent rate limiting
                    if idx < len(posts_to_process):  # Don't delay after the last one
                        delay = random.randint(5, 10)  # 5-10 seconds between posts
                        print(f"   ⏱️  Waiting {delay}s before processing next post...")
                        time.sleep(delay)
                    
                except Exception as e:
                    print(f"   ❌ Error processing post {idx}: {e}")
                    continue
            
            # Add delay between hashtags
            remaining_hashtags = list(trending_content['hashtag_posts'].keys())
            current_index = remaining_hashtags.index(hashtag)
            if current_index < len(remaining_hashtags) - 1:
                delay = 5  # 5 seconds between hashtags
                print(f"\n⏱️  Completed {hashtag}. Waiting {delay}s before processing next hashtag...")
                time.sleep(delay)
        
        # Show final summary
        print(f"\n📊 Trending Content Engagement Summary:")
        print(f"   📈 Hashtags processed: {len(trending_content['hashtag_posts'])}")
        print(f"   📱 Posts processed: {total_processed}")
        print(f"   💫 Successful engagements: {successful_engagements}")
        print(f"   💬 Successful replies: {successful_replies}")
        if total_processed > 0:
            engagement_rate = (successful_engagements / total_processed) * 100
            reply_rate = (successful_replies / total_processed) * 100
            print(f"   📈 Engagement rate: {engagement_rate:.1f}%")
            print(f"   📈 Reply rate: {reply_rate:.1f}%")
        
    except Exception as e:
        print(f"❌ Error in trending content processing: {e}")


def run_continuous_trending_monitoring():
    """
    Run the trending content monitoring in an endless loop with proper pause intervals.
    Logs each iteration and includes safety pauses to avoid hammering the API.
    """
    iteration = 1
    print("🚀 Starting continuous trending content monitoring loop...")
    print("   Press Ctrl+C to stop the monitoring")
    
    try:
        while True:
            print(f"\n{'='*60}")
            print(f"🔄 Starting trending monitoring iteration #{iteration}")
            print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            try:
                # Process trending content (limit to avoid overwhelming the API)
                process_trending_content(max_hashtags=15, max_posts_per_hashtag=50)
                
                print(f"\n✅ Completed iteration #{iteration}")
                
            except Exception as e:
                print(f"\n❌ Error in iteration #{iteration}: {e}")
                print("   Continuing to next iteration...")
            
            # Pause between iterations to avoid hammering the API
            pause_duration = 15  # 15 seconds between iterations
            print(f"\n⏸️  Iteration #{iteration} complete. Pausing for {pause_duration} seconds...")
            print(f"   Next iteration #{iteration + 1} will start at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + pause_duration))}")
            
            # Show countdown for the last 60 seconds
            for remaining in range(pause_duration, 0, -1):
                if remaining <= 60 or remaining % 120 == 0:  # Show every 2 minutes, plus last minute
                    print(f"   ⏱️  Next iteration in {remaining} seconds...")
                time.sleep(1)
            
            iteration += 1
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Monitoring stopped by user after {iteration - 1} iterations")
        print("   Goodbye! 👋")
    except Exception as e:
        print(f"\n\n💥 Fatal error after {iteration - 1} iterations: {e}")
        print("   Monitoring stopped unexpectedly")


if __name__ == "__main__":
    # Run continuous trending content monitoring
    run_continuous_trending_monitoring()