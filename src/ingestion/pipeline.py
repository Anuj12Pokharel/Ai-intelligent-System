"""
Orchestration pipeline for ingesting legal documents.
Coordinates scraping, parsing, and indexing with comprehensive logging.
"""
import os
import json
import logging
from pathlib import Path
from typing import List
from src.ingestion.parser import NepaliLegalParser
from src.ingestion.html_parser import NepaliHTMLParser
from src.retrieval.indexer import LegalIndexer
from src.schema import Act

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vidhi_ai_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self, 
                 raw_data_dir: str = "data/raw",
                 processed_data_dir: str = "data/processed",
                 chroma_dir: str = "data/chroma_db"):
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_data_dir = Path(processed_data_dir)
        self.indexer = LegalIndexer(persist_directory=chroma_dir)
        
        # Ensure directories exist
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Metrics
        self.stats = {
            'total_files': 0,
            'pdf_success': 0,
            'html_success': 0,
            'failures': 0,
            'indexed': 0
        }
        
        logger.info(f"Pipeline initialized: {raw_data_dir} -> {processed_data_dir}")

    def process_file(self, file_path: Path, source_url: str = "") -> Act:
        """Parse a single file (PDF or HTML) into structured Act"""
        logger.info(f"Processing: {file_path.name}")
        
        try:
            if file_path.suffix.lower() == '.pdf':
                parser = NepaliLegalParser(str(file_path), source_url)
                act = parser.parse()
                self.stats['pdf_success'] += 1
            elif file_path.suffix.lower() in ['.html', '.htm']:
                parser = NepaliHTMLParser(str(file_path), source_url)
                act = parser.parse()
                self.stats['html_success'] += 1
            else:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
            # Save structured JSON
            safe_name = file_path.stem.replace(' ', '_')[:100]
            output_path = self.processed_data_dir / f"{safe_name}.json"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(act.model_dump(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"✓ Saved: {output_path.name} ({len(act.chapters)} chapters)")
            return act
            
        except Exception as e:
            logger.error(f"✗ Failed to process {file_path.name}: {e}")
            self.stats['failures'] += 1
            raise

    def index_act(self, act: Act):
        """Index an Act into ChromaDB with error handling"""
        try:
            logger.info(f"Indexing: {act.title}")
            self.indexer.index_act(act)
            self.stats['indexed'] += 1
        except Exception as e:
            logger.error(f"✗ Failed to index {act.title}: {e}")
            raise

    def run_batch(self, limit: int = None):
        """Process all files in raw_data_dir"""
        # Find all PDF and HTML files
        all_files = []
        all_files.extend(self.raw_data_dir.glob("*.pdf"))
        all_files.extend(self.raw_data_dir.glob("*.html"))
        all_files.extend(self.raw_data_dir.glob("*.htm"))
        
        if limit:
            all_files = all_files[:limit]
        
        self.stats['total_files'] = len(all_files)
        logger.info(f"Found {len(all_files)} files to process")
        
        for file_path in all_files:
            try:
                act = self.process_file(file_path)
                self.index_act(act)
            except Exception as e:
                logger.error(f"Skipping {file_path.name} due to error: {e}")
                continue
        
        self.print_stats()

    def print_stats(self):
        """Print pipeline statistics"""
        logger.info("="*60)
        logger.info("PIPELINE STATISTICS")
        logger.info("="*60)
        logger.info(f"Total Files: {self.stats['total_files']}")
        logger.info(f"PDF Success: {self.stats['pdf_success']}")
        logger.info(f"HTML Success: {self.stats['html_success']}")
        logger.info(f"Failures: {self.stats['failures']}")
        logger.info(f"Indexed: {self.stats['indexed']}")
        
        success_rate = ((self.stats['pdf_success'] + self.stats['html_success']) / 
                       self.stats['total_files'] * 100) if self.stats['total_files'] > 0 else 0
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("="*60)

    def load_and_index_json(self, json_path: str):
        """Load pre-parsed JSON and index it"""
        logger.info(f"Loading JSON: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        act = Act(**data)
        self.index_act(act)

if __name__ == "__main__":
    # Example usage
    pipeline = IngestionPipeline()
    # pipeline.run_batch(limit=10)  # Process first 10 files
