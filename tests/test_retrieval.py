"""
Tests for RAG retrieval system
"""
import pytest
from vidhi_ai.src.retrieval.indexer import LegalIndexer
from vidhi_ai.src.retrieval.engine import RetrievalEngine
from vidhi_ai.src.schema import Act, Chapter, Section

class TestRetrieval:
    @pytest.fixture
    def sample_act(self):
        """Create a sample Act for testing"""
        return Act(
            title="Test Act, 2074",
            source_url="http://test.com",
            chapters=[
                Chapter(
                    chapter_number="1",
                    title="General Provisions",
                    sections=[
                        Section(
                            section_number="1",
                            title="Short Title",
                            content="This Act shall be known as the Test Act."
                        ),
                        Section(
                            section_number="2",
                            title="Definitions",
                            content="In this Act, unless the context requires otherwise, 'Court' means the Supreme Court."
                        )
                    ]
                )
            ]
        )
    
    def test_indexing(self, sample_act, tmp_path):
        """Test that Acts are correctly indexed"""
        indexer = LegalIndexer(persist_directory=str(tmp_path / "chroma_test"))
        indexer.index_act(sample_act)
        
        # Check collection has items
        assert indexer.collection.count() > 0
    
    def test_retrieval(self, sample_act, tmp_path):
        """Test semantic search retrieval"""
        # Index sample act
        indexer = LegalIndexer(persist_directory=str(tmp_path / "chroma_test"))
        indexer.index_act(sample_act)
        
        # Create retrieval engine
        engine = RetrievalEngine(persist_dir=str(tmp_path / "chroma_test"))
        
        # Search for relevant content
        results = engine.search("What is the short title?", k=1)
        
        assert len(results) > 0
        assert "Test Act" in results[0]["content"]
    
    def test_metadata_preservation(self, sample_act, tmp_path):
        """Test that hierarchical metadata is preserved"""
        indexer = LegalIndexer(persist_directory=str(tmp_path / "chroma_test"))
        indexer.index_act(sample_act)
        
        engine = RetrievalEngine(persist_dir=str(tmp_path / "chroma_test"))
        results = engine.search("Supreme Court", k=1)
        
        assert len(results) > 0
        metadata = results[0]["metadata"]
        assert metadata["act_title"] == "Test Act, 2074"
        assert metadata["section_number"] == "2"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
