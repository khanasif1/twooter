#!/usr/bin/env python3
"""
Example usage script for the Twooter Team Bot

This script demonstrates various ways to use the team bot for CTF competitions.
It includes examples of basic posting, automated engagement, and team coordination.

Run this script after configuring your bot to see it in action.
"""

import time
import sys
from team_bot import TwooterTeamBot


def basic_posting_example():
    """Example of basic posting functionality."""
    print("🔨 Basic Posting Example")
    print("=" * 50)
    
    bot = TwooterTeamBot()
    
    if not bot.start():
        print("❌ Failed to start bot. Please check your configuration.")
        return False
    
    try:
        # Simple post
        print("📝 Creating a simple post...")
        result = bot.post("🤖 Team bot is now online and ready for the CTF!")
        
        if result:
            post_id = result.get('data', {}).get('id')
            print(f"✅ Post created with ID: {post_id}")
            
            # Like our own post (for demonstration)
            if post_id:
                print("👍 Liking our own post...")
                bot.like_post(post_id)
        
        # Create a thread
        print("🧵 Creating a thread...")
        thread_posts = [
            "🚨 Team Update Thread 🚨",
            "We're making great progress on the web challenges",
            "Currently working on the crypto section",
            "Let us know if you want to collaborate! 🤝"
        ]
        
        thread_result = bot.create_thread(thread_posts, delay_seconds=2)
        if thread_result:
            print(f"✅ Thread created with {len(thread_result)} posts")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in basic posting example: {e}")
        return False
    finally:
        bot.stop()


def automated_engagement_example():
    """Example of automated engagement functionality."""
    print("\n🤖 Automated Engagement Example")
    print("=" * 50)
    
    bot = TwooterTeamBot()
    
    if not bot.start():
        print("❌ Failed to start bot. Please check your configuration.")
        return False
    
    try:
        print("🔍 Starting automated engagement for 2 minutes...")
        print("The bot will monitor for CTF-related keywords and engage automatically")
        
        # Define keywords to monitor
        keywords = ["ctf", "challenge", "flag", "solution", "hint"]
        
        # Start auto-engagement for a short period (2 minutes for demo)
        print(f"🎯 Monitoring keywords: {keywords}")
        print("⏱️  Running for 2 minutes (press Ctrl+C to stop early)")
        
        # Run auto-engagement with high frequency for demo
        import threading
        import time
        
        def stop_after_delay():
            time.sleep(120)  # 2 minutes
            bot.auto_mode = False
        
        # Start stop timer
        stop_timer = threading.Thread(target=stop_after_delay)
        stop_timer.daemon = True
        stop_timer.start()
        
        # Run auto-engagement
        bot.auto_engage(
            keywords=keywords,
            actions=['like'],  # Only like posts for demo
            check_interval=30,  # Check every 30 seconds
            max_actions_per_hour=20
        )
        
        print("✅ Automated engagement demo completed")
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️  Automated engagement stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error in automated engagement example: {e}")
        return False
    finally:
        bot.stop()


def team_coordination_example():
    """Example of team coordination functionality."""
    print("\n👥 Team Coordination Example")
    print("=" * 50)
    
    bot = TwooterTeamBot()
    
    if not bot.start():
        print("❌ Failed to start bot. Please check your configuration.")
        return False
    
    try:
        # Team check-in
        print("📢 Posting team check-in...")
        bot.post("🌅 Good morning! Our team is starting today's CTF session 💪")
        
        # Status update
        print("📊 Posting status update...")
        bot.post("📊 Team Status: Web challenges complete ✅ | Working on crypto 🔐 | Need help with reversing 🤔")
        
        # Collaboration call
        print("🤝 Posting collaboration call...")
        collaboration_post = bot.post("🤝 Looking for teams to collaborate on the advanced crypto challenge. DM us if interested!")
        
        # Schedule follow-up (for demonstration, we'll just show the concept)
        print("⏰ Scheduling follow-up posts...")
        
        # In a real scenario, you might schedule these with a proper scheduler
        follow_ups = [
            "⏰ Midday update: Making good progress on reversing challenge",
            "🎯 Afternoon update: Solved 3 more challenges, moving up the leaderboard!",
            "🌙 End of day: Great work team! Tomorrow we tackle the final challenges"
        ]
        
        for i, follow_up in enumerate(follow_ups):
            print(f"   Scheduled: {follow_up}")
            # In practice, you'd use a scheduler like APScheduler or cron
            # For demo, we'll just show one more post
            if i == 0:
                time.sleep(5)  # Wait 5 seconds for demo
                bot.post(follow_up)
                break
        
        print("✅ Team coordination example completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in team coordination example: {e}")
        return False
    finally:
        bot.stop()


def interactive_demo():
    """Run interactive mode for manual testing."""
    print("\n🎮 Interactive Demo")
    print("=" * 50)
    
    bot = TwooterTeamBot()
    
    print("Starting interactive mode...")
    print("You can manually test the bot commands.")
    print("Type 'help' for available commands or 'quit' to exit.")
    
    bot.run_interactive_mode()


def main():
    """Main function to run all examples."""
    print("🤖 Twooter Team Bot - Example Usage")
    print("=" * 60)
    
    # Check if we should run specific examples
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "basic":
            basic_posting_example()
        elif mode == "auto":
            automated_engagement_example()
        elif mode == "team":
            team_coordination_example()
        elif mode == "interactive":
            interactive_demo()
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Available modes: basic, auto, team, interactive")
            sys.exit(1)
    else:
        # Run all examples in sequence
        print("🚀 Running all examples in sequence...")
        print("This will demonstrate the bot's capabilities step by step.")
        
        input("\nPress Enter to start basic posting example...")
        success1 = basic_posting_example()
        
        if success1:
            input("\nPress Enter to start automated engagement example...")
            success2 = automated_engagement_example()
            
            if success2:
                input("\nPress Enter to start team coordination example...")
                success3 = team_coordination_example()
                
                if success3:
                    print("\n🎉 All examples completed successfully!")
                    print("Your bot is ready for CTF competitions!")
                    
                    choice = input("\nWould you like to try interactive mode? (y/n): ")
                    if choice.lower().startswith('y'):
                        interactive_demo()
        
        print("\n👋 Example session completed. Happy CTF-ing!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Example session interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)