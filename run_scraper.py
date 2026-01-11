#!/usr/bin/env python3
"""
Run scraper to download Acts from lawcommission.gov.np
"""
import asyncio
import sys
sys.path.insert(0, '.')

from src.ingestion.scraper import scrape_existing_laws

async def main():
    print("=" * 60)
    print("VIDHI-AI SCRAPER - Nepal Law Commission")
    print("=" * 60)
    print("\nThis will download ~300 Acts (HTML/PDF)")
    print("Expected time: 2-3 hours")
    print("Output: data/raw/")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        await scrape_existing_laws(
            output_dir="data/raw",
            limit=300  # Change to None for all Acts
        )
        print("\n✓ Scraping complete!")
    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
