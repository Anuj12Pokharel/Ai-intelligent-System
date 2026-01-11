#!/usr/bin/env python3
"""
Run full scraper to download all 300 Acts from Nepal Law Commission
"""
import asyncio
import sys
import os
sys.path.insert(0, '.')

from src.ingestion.scraper import scrape_catalog

async def main():
    print("=" * 70)
    print("VIDHI-AI: Full Scraper - Downloading 300+ Acts")
    print("=" * 70)
    print("\nTarget: https://lawcommission.gov.np/category/1757/")
    print("Output: data/raw/")
    print("Pagination: Up to 70 pages")
    print("\nThis will take 2-3 hours...")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    # Ensure output directory exists
    os.makedirs("data/raw", exist_ok=True)
    
    try:
        await scrape_catalog()
        print("\n" + "=" * 70)
        print("✓ SCRAPING COMPLETE!")
        print("=" * 70)
        
        # Count downloaded files
        files = os.listdir("data/raw")
        print(f"\nTotal files downloaded: {len(files)}")
        
    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
