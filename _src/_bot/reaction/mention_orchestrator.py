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


def reply_to_post(extractor: VictorPostsExtractor, post_id: int, reply_content: str) -> bool:
    """
    Reply to a specific post using the generated AI content with rate limiting.
    
    Args:
        extractor (VictorPostsExtractor): The already authenticated extractor instance
        post_id (int): The ID of the original post to reply to
        reply_content (str): The AI-generated reply content
        
    Returns:
        bool: True if reply was posted successfully, False otherwise
    """
    max_retries = 3
    base_delay = 30  # Start with 30 seconds for rate limiting
    
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
                reply_id = result.get('data', {}).get('id', 'Unknown')
                print(f"   ✅ Successfully replied to post {post_id} with reply ID: {reply_id}")
                return True
            else:
                print(f"   ❌ Failed to reply to post {post_id}: No data in response")
                return False
                
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
                    return False
            else:
                print(f"   ❌ Error replying to post {post_id}: {e}")
                return False
    
    return False


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
        print("❌ No posts mentioning @victor_hawthorne found")
        return
    
    # Initialize Azure OpenAI client
    ai_client = VictorCampaignAzureOpenAI()
    
    # Limit mentions if specified
    mentions_to_process = posts_mentioning_victor[:max_mentions] if max_mentions else posts_mentioning_victor
    
    print(f"\n🤖 Generating replies for {len(mentions_to_process)} posts mentioning @victor_hawthorne...")
    if max_mentions:
        print(f"   📋 Limited to first {max_mentions} mentions for rate limiting")
    
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
            success = reply_to_post(extractor, int(post_id), reply)
            
            if success:
                print(f"   🎉 Successfully posted reply to @{author}'s post!")
            else:
                print(f"   ⚠️  Generated reply but failed to post it")
            
            # Add delay between mentions to prevent rate limiting
            if idx < len(mentions_to_process):  # Don't delay after the last one
                delay = 15  # 15 seconds between each mention processing
                print(f"   ⏱️  Waiting {delay}s before processing next mention...")
                time.sleep(delay)
            
        except Exception as e:
            print(f"   ❌ Error processing mention {idx}: {e}")
            continue
    
    print(f"\n🎉 Reply generation and posting complete for all mentions!")


if __name__ == "__main__":
    # Process only first 3 mentions to test rate limiting
    generate_replies_to_mentions()