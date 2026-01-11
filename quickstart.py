#!/usr/bin/env python3
"""
Quick Start Script for Vidhi-AI
Runs the complete pipeline: scrape data (optional) → parse → index → validate
"""
import sys
import argparse
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion.pipeline import IngestionPipeline
from validate import VidhiValidator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Vidhi-AI Quick Start')
    parser.add_argument('--ingest', action='store_true', help='Run ingestion pipeline')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of files to process')
    parser.add_argument('--validate', action='store_true', help='Run full validation')
    parser.add_argument('--scrape', action='store_true', help='Run scraper first (WARNING: takes time)')
    
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("VIDHI-AI QUICK START")
    logger.info("="*60)
    
    if args.scrape:
        logger.info("\n📥 STEP 1: Running Scraper...")
        logger.warning("⚠ Scraping will take several minutes. Press Ctrl+C to skip.")
        import asyncio
        from vidhi_ai.src.ingestion.scraper import scrape_catalog
        asyncio.run(scrape_catalog())
    
    if args.ingest:
        logger.info("\n📊 STEP 2: Running Ingestion Pipeline...")
        pipeline = IngestionPipeline()
        pipeline.run_batch(limit=args.limit)
    
    if args.validate:
        logger.info("\n✅ STEP 3: Validating System...")
        validator = VidhiValidator()
        validator.run_full_validation()
    
    if not (args.ingest or args.validate or args.scrape):
        logger.info("\n💡 Usage Examples:")
        logger.info("  python quickstart.py --ingest --limit 5    # Process first 5 files")
        logger.info("  python quickstart.py --validate            # Check system status")
        logger.info("  python quickstart.py --ingest --validate   # Full pipeline")
        logger.info("\n  For CLI: python cli.py --help")

if __name__ == "__main__":
    main()
