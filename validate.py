"""
End-to-end validation and testing script for Vidhi-AI
"""
import logging
from pathlib import Path
from src.ingestion.pipeline import IngestionPipeline
from src.retrieval.engine import RetrievalEngine
from src.reasoning.chain import LegalChain
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VidhiValidator:
    """Validates the entire Vidhi-AI system"""
    
    def __init__(self):
        self.pipeline = IngestionPipeline()
        self.retriever = RetrievalEngine()
        self.chain = None  # Initialize when needed
    
    def validate_ingestion(self):
        """Validate data ingestion"""
        logger.info("=" * 60)
        logger.info("STEP 1: Validating Data Ingestion")
        logger.info("=" * 60)
        
        raw_files = list(Path("data/raw").glob("*.*"))
        processed_files = list(Path("data/processed").glob("*.json"))
        
        logger.info(f"Raw files: {len(raw_files)}")
        logger.info(f"Processed files: {len(processed_files)}")
        
        return len(raw_files) > 0
    
    def validate_indexing(self):
        """Validate vector database"""
        logger.info("=" * 60)
        logger.info("STEP 2: Validating Vector Database")
        logger.info("=" * 60)
        
        try:
            count = self.retriever.collection.count()
            logger.info(f"✓ Indexed sections: {count}")
            
            if count == 0:
                logger.warning("⚠ No sections indexed yet!")
                return False
            
            # Sample query
            results = self.retriever.search("दफा", k=3)
            logger.info(f"✓ Sample search returned {len(results)} results")
            
            if results:
                logger.info(f"  Sample result: {results[0]['metadata']['act_title']}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Indexing validation failed: {e}")
            return False
    
    def validate_retrieval(self):
        """Test semantic search"""
        logger.info("=" * 60)
        logger.info("STEP 3: Validating Retrieval")
        logger.info("=" * 60)
        
        test_queries = [
            "नागरिकता",  # Citizenship
            "सजाय",      # Punishment
            "अधिकार"     # Rights
        ]
        
        for query in test_queries:
            try:
                results = self.retriever.search(query, k=2)
                logger.info(f"✓ Query '{query}': {len(results)} results")
                
                if results:
                    logger.info(f"  Top result: {results[0]['metadata']['section_number']}")
            except Exception as e:
                logger.error(f"✗ Query '{query}' failed: {e}")
        
        return True
    
    def validate_llm_integration(self):
        """Test LLM question answering"""
        logger.info("=" * 60)
        logger.info("STEP 4: Validating LLM Integration")
        logger.info("=" * 60)
        
        if not os.getenv('OPENAI_API_KEY'):
            logger.warning("⚠ OPENAI_API_KEY not set. Skipping LLM test.")
            return False
        
        try:
            self.chain = LegalChain()
            
            # Test queries
            test_question = "नागरिकता कसरी प्राप्त गर्न सकिन्छ?"  # How to get citizenship?
            
            logger.info(f"Test question: {test_question}")
            answer = self.chain.answer(test_question)
            logger.info(f"✓ Answer received ({len(answer)} chars)")
            logger.info(f"  Preview: {answer[:200]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ LLM validation failed: {e}")
            return False
    
    def run_full_validation(self):
        """Run all validation steps"""
        logger.info("\n" + "="*60)
        logger.info("VIDHI-AI SYSTEM VALIDATION")
        logger.info("="*60 + "\n")
        
        results = {
            'ingestion': self.validate_ingestion(),
            'indexing': self.validate_indexing(),
            'retrieval': self.validate_retrieval(),
            'llm': self.validate_llm_integration()
        }
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*60)
        
        for step, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            logger.info(f"{step.upper()}: {status}")
        
        total = sum(results.values())
        percentage = (total / len(results)) * 100
        
        logger.info(f"\nOverall: {total}/{len(results)} checks passed ({percentage:.0f}%)")
        logger.info("="*60 + "\n")
        
        return results

if __name__ == "__main__":
    validator = VidhiValidator()
    validator.run_full_validation()
