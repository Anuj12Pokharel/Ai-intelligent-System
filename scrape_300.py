#!/usr/bin/env python3
"""
Automated scraper for 300 Acts from Nepal Law Commission
"""
import asyncio
import sys
sys.path.insert(0, '.')

from src.ingestion.scraper import scrape_catalog

async def main():
    print("=" * 60)
    print("VIDHI-AI: Scraping 300 Acts")
    print("=" * 60)
    print("\nTarget: lawcommission.gov.np")
    print("Output: data/raw/")
    print("Estimated time: 2-3 hours")
    print("\nStarting scraper...")
    print("=" * 60)
    print()
    
    try:
        await scrape_catalog()
        print("\n" + "=" * 60)
        print("✓ SCRAPING COMPLETE!")
        print("=" * 60)
    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
