#!/usr/bin/env python3
"""
Simple runner for Victor web scraper.
This version uses only requests + BeautifulSoup for Windows compatibility.
"""

import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from victor_scraper_simple import main
    
    if __name__ == "__main__":
        print("🚀 Starting Victor web scraper (Simple Version)...")
        exit_code = main()
        
        if exit_code == 0:
            print("\n✅ Scraper completed successfully!")
        else:
            print("\n❌ Scraper failed!")
        
        exit(exit_code)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure to install requirements first:")
    print("   pip install -r scraper_simple_requirements.txt")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)