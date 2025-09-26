#!/usr/bin/env python3
"""
Mention Orchestrator for Victor Hawthorne Campaign

This module generates supportive replies to posts mentioning @victor_hawthorne
using Azure OpenAI and includes all tags from the original post.
"""

from victor_posts_extractor import VictorPostsExtractor
from azure_openai_client import VictorCampaignAzureOpenAI
from auth_manager import AuthenticationManager
from posting_manager import PostingManager
import time
import random


def reply_to_post(extractor: VictorPostsExtractor, post_id: int, reply_content: str) -> tuple[bool, int]:
    """
    Reply to a specific post using the generated AI content with rate limiting.
    
    Args:
        extractor (VictorPostsExtractor): The already authenticated extractor instance
        post_id (int): The ID of the original post to reply to
        reply_content (str): The AI-generated reply content
        
    Returns:
        tuple[bool, int]: (success, reply_id) - True if reply posted successfully and reply ID
    """
    max_retries = 3
    base_delay = 10  # Start with 30 seconds for rate limiting
    
    for attempt in range(max_retries):
        try:
            # Use the existing extractor's authentication manager
            posting_manager = PostingManager(extractor.auth_manager)
            
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


def like_and_repost_posts(extractor: VictorPostsExtractor, original_post_id: int, reply_id: int = None) -> dict:
    """
    Like and repost both the original post and the reply post.
    
    Args:
        extractor (VictorPostsExtractor): The already authenticated extractor instance
        original_post_id (int): The ID of the original post to like and repost
        reply_id (int, optional): The ID of the reply post to like and repost
        
    Returns:
        dict: Results of like and repost operations
    """
    results = {
        'original_like': False,
        'original_repost': False,
        'reply_like': False,
        'reply_repost': False,
        'errors': []
    }
    
    try:
        posting_manager = PostingManager(extractor.auth_manager)
        
        # Like and repost the original post
        print(f"   👍 Liking original post {original_post_id}...")
        try:
            like_result = posting_manager.like_post(original_post_id)
            if like_result:
                results['original_like'] = True
                print(f"   ✅ Successfully liked original post {original_post_id}")
            else:
                print(f"   ❌ Failed to like original post {original_post_id}")
        except Exception as e:
            error_msg = f"Error liking original post {original_post_id}: {e}"
            results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        
        # Small delay between operations
        time.sleep(2)
        
        print(f"   🔄 Reposting original post {original_post_id}...")
        try:
            repost_result = posting_manager.repost(original_post_id)
            if repost_result:
                results['original_repost'] = True
                print(f"   ✅ Successfully reposted original post {original_post_id}")
            else:
                print(f"   ❌ Failed to repost original post {original_post_id}")
        except Exception as e:
            error_msg = f"Error reposting original post {original_post_id}: {e}"
            results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        
        # Like and repost the reply if it exists
        if reply_id:
            time.sleep(2)
            
            print(f"   👍 Liking reply post {reply_id}...")
            try:
                like_result = posting_manager.like_post(reply_id)
                if like_result:
                    results['reply_like'] = True
                    print(f"   ✅ Successfully liked reply post {reply_id}")
                else:
                    print(f"   ❌ Failed to like reply post {reply_id}")
            except Exception as e:
                error_msg = f"Error liking reply post {reply_id}: {e}"
                results['errors'].append(error_msg)
                print(f"   ❌ {error_msg}")
            
            time.sleep(2)
            
            print(f"   🔄 Reposting reply post {reply_id}...")
            try:
                repost_result = posting_manager.repost(reply_id)
                if repost_result:
                    results['reply_repost'] = True
                    print(f"   ✅ Successfully reposted reply post {reply_id}")
                else:
                    print(f"   ❌ Failed to repost reply post {reply_id}")
            except Exception as e:
                error_msg = f"Error reposting reply post {reply_id}: {e}"
                results['errors'].append(error_msg)
                print(f"   ❌ {error_msg}")
        
        # Summary of operations
        successful_ops = sum([results['original_like'], results['original_repost'], 
                             results['reply_like'], results['reply_repost']])
        total_ops = 2 + (2 if reply_id else 0)
        
        print(f"   📊 Engagement complete: {successful_ops}/{total_ops} operations successful")
        
    except Exception as e:
        error_msg = f"Error in like_and_repost_posts: {e}"
        results['errors'].append(error_msg)
        print(f"   ❌ {error_msg}")
    
    return results


def generate_replies_to_mentions(max_mentions: int = None):
    """
    Generate supportive replies to all posts mentioning @victor_hawthorne and post them.
    
    This function performs the complete workflow:
    1. Extracts posts mentioning Victor Hawthorne
    2. For each post, generates a supportive reply using Azure OpenAI
    3. Includes all tags from the original post in the reply
    4. Immediately posts the reply to the original post
    
    Args:
        max_mentions (int, optional): Maximum number of mentions to process. If None, processes all.
    """
    # Initialize extractor and login
    extractor = VictorPostsExtractor()
    if not extractor.login():
        print("❌ Cannot proceed without authentication")
        return
    
    # Get posts mentioning Victor Hawthorne
    posts_mentioning_victor = extractor.get_posts_mentioning_victor_hawthorne()
    
    if not posts_mentioning_victor:
        print("ℹ️  No new posts mentioning @victor_hawthorne found in this iteration")
        return
    
    print(f"🎯 Found {len(posts_mentioning_victor)} posts mentioning @victor_hawthorne")
    
    # Initialize Azure OpenAI client
    ai_client = VictorCampaignAzureOpenAI()
    
    # Limit mentions if specified
    mentions_to_process = posts_mentioning_victor[:max_mentions] if max_mentions else posts_mentioning_victor
    
    print(f"\n🤖 Processing {len(mentions_to_process)} posts mentioning @victor_hawthorne...")
    if max_mentions and len(posts_mentioning_victor) > max_mentions:
        print(f"   📋 Limited to first {max_mentions} mentions (found {len(posts_mentioning_victor)} total)")
    
    successful_replies = 0
    total_processed = 0
    
    # System prompt for generating supportive replies
    reply_system_prompt = (
        "You are an AI helper for Victor Hawthorne's presidential campaign. "
        "Generate a supportive reply to a social media post that mentions Victor Hawthorne. "
        "The reply should be positive, engaging, and support Victor's campaign themes. "
        "Keep it under 255 characters. Be authentic and conversational. "
        "Always include @victor_hawthorne and #VoteHawthorne #Hawthorne2025 in your reply."
    )
    
    # Loop through mentions to process
    for idx, post in enumerate(mentions_to_process, 1):
        total_processed += 1
        try:
            print(f"\n📝 Processing mention {idx}/{len(mentions_to_process)}...")
            
            # Extract post details
            post_id = post.get('id', 'Unknown')
            original_content = post.get('content', '')
            author = post.get('author', {}).get('username', 'Unknown')
            
            # Extract all tags from the original post
            original_tags = []
            tags = post.get('tags', [])
            for tag in tags:
                tag_name = tag.get('name', '')
                if tag_name:
                    original_tags.append(f"#{tag_name}")
            
            # Prepare content for AI
            content_for_ai = f"""
Original Post by @{author} (ID: {post_id}):
{original_content}

Original Tags: {' '.join(original_tags) if original_tags else 'None'}

Generate a supportive reply that includes Victor Hawthorne's campaign themes and all the original tags.
            """
            
            print(f"   👤 Original author: @{author}")
            print(f"   📱 Original content: {original_content[:100]}...")
            print(f"   🏷️  Original tags: {', '.join(original_tags) if original_tags else 'None'}")
            
            # Generate reply using Azure OpenAI
            reply = ai_client.generate_social_post(reply_system_prompt, content_for_ai)
            
            # Add original tags to the reply if not already included
            if original_tags:
                reply_with_tags = reply
                for tag in original_tags:
                    if tag not in reply_with_tags:
                        # Add tag if there's space (keeping under 255 chars)
                        potential_reply = f"{reply_with_tags} {tag}"
                        if len(potential_reply) <= 255:
                            reply_with_tags = potential_reply
                
                reply = reply_with_tags
            
            # Ensure the reply is under 255 characters
            if len(reply) > 255:
                reply = reply[:252] + "..."
            
            print(f"   ✅ Generated reply ({len(reply)} chars): {reply}")
            print(f"   🎯 Reply to post ID: {post_id}")
            
            # Immediately reply to the original post with the generated content
            print(f"   📤 Posting reply to original post...")
            time.sleep(random.randint(1, 5))
            success, reply_id = reply_to_post(extractor, int(post_id), reply)
            
            if success:
                successful_replies += 1
                print(f"   🎉 Successfully posted reply to @{author}'s post!")
                
                # Like and repost both the original post and the reply
                print(f"   💫 Engaging with posts (like & repost)...")
                time.sleep(random.randint(1, 5))
                engagement_results = like_and_repost_posts(extractor, int(post_id), reply_id)
                
                # Show engagement summary
                if engagement_results['original_like'] or engagement_results['original_repost']:
                    print(f"   ✅ Original post engagement successful")
                if engagement_results['reply_like'] or engagement_results['reply_repost']:
                    print(f"   ✅ Reply post engagement successful")
                if engagement_results['errors']:
                    print(f"   ⚠️  Some engagement operations failed")
                
            else:
                print(f"   ⚠️  Generated reply but failed to post it")
            
            # Add delay between mentions to prevent rate limiting
            if idx < len(mentions_to_process):  # Don't delay after the last one
                delay = 5  # 5 seconds between each mention processing
                print(f"   ⏱️  Waiting {delay}s before processing next mention...")
                time.sleep(delay)
            
        except Exception as e:
            print(f"   ❌ Error processing mention {idx}: {e}")
            continue
    
    # Show summary statistics
    print(f"\n📊 Iteration Summary:")
    print(f"   📈 Posts processed: {total_processed}")
    print(f"   ✅ Successful replies: {successful_replies}")
    print(f"   ❌ Failed replies: {total_processed - successful_replies}")
    if total_processed > 0:
        success_rate = (successful_replies / total_processed) * 100
        print(f"   📈 Success rate: {success_rate:.1f}%")
    
    print(f"\n🎉 Reply generation and engagement workflow complete!")
    print(f"   Time completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")


def run_continuous_monitoring():
    """
    Run the mention monitoring in an endless loop with proper pause intervals.
    Logs each iteration and includes safety pauses to avoid hammering the API.
    """
    iteration = 1
    print("🚀 Starting continuous mention monitoring loop...")
    print("   Press Ctrl+C to stop the monitoring")
    
    try:
        while True:
            print(f"\n{'='*60}")
            print(f"🔄 Starting monitoring iteration #{iteration}")
            print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            try:
                # Process mentions (limit to avoid overwhelming the API)
                generate_replies_to_mentions(max_mentions=100)
                
                print(f"\n✅ Completed iteration #{iteration}")
                
            except Exception as e:
                print(f"\n❌ Error in iteration #{iteration}: {e}")
                print("   Continuing to next iteration...")
            
            # Pause between iterations to avoid hammering the API
            pause_duration = 20  # 20 seconds between iterations
            print(f"\n⏸️  Iteration #{iteration} complete. Pausing for {pause_duration} seconds...")
            print(f"   Next iteration #{iteration + 1} will start at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + pause_duration))}")
            
            # Show countdown for the last 30 seconds
            for remaining in range(pause_duration, 0, -1):
                if remaining <= 30 or remaining % 60 == 0:  # Show every minute, plus last 30 seconds
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
    # Run continuous monitoring
    run_continuous_monitoring()