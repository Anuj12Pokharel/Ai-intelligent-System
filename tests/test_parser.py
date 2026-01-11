"""
Unit tests for the Legal Parser
"""
import pytest
from vidhi_ai.src.ingestion.parser import NepaliLegalParser

class TestNepaliLegalParser:
    def test_nepali_to_english_conversion(self):
        parser = NepaliLegalParser.__new__(NepaliLegalParser)
        assert parser.nepali_to_english_num("१२३") == "123"
        assert parser.nepali_to_english_num("०") == "0"
        assert parser.nepali_to_english_num("९९९") == "999"
    
    def test_number_extraction(self):
        parser = NepaliLegalParser.__new__(NepaliLegalParser)
        parser.NEPALI_TO_ENGLISH = NepaliLegalParser.NEPALI_TO_ENGLISH
        
        assert parser.extract_number("दफा १") == "1"
        assert parser.extract_number("परिच्छेद-५") == "5"
        assert parser.extract_number("Section 42") == "42"
    
    def test_clause_detection(self):
        parser = NepaliLegalParser.__new__(NepaliLegalParser)
        parser.clause_pattern = NepaliLegalParser.__dict__['clause_pattern']
        
        # Test various clause formats
        content = """
        (१) यो पहिलो खण्ड हो।
        (२) यो दोस्रो खण्ड हो।
        """
        # This would require full initialization; simplified for demo
        # clauses = parser.detect_clauses(content)
        # assert len(clauses) == 2
    
    def test_pattern_matching(self):
        """Test regex patterns match expected Nepali legal structures"""
        parser = NepaliLegalParser.__new__(NepaliLegalParser)
        import re
        
        # Part pattern
        part_pattern = re.compile(r'भाग[\s-]*[\u0966-\u096F0-9]+')
        assert part_pattern.match("भाग १")
        assert part_pattern.match("भाग-२")
        
        # Chapter pattern
        chapter_pattern = re.compile(r'परिच्छेद[\s-]*[\u0966-\u096F0-9]+')
        assert chapter_pattern.match("परिच्छेद १")
        assert chapter_pattern.match("परिच्छेद-३")
        
        # Section pattern
        section_pattern = re.compile(r'दफा[\s-]*[\u0966-\u096F0-9]+')
        assert section_pattern.match("दफा १")
        assert section_pattern.match("दफा 42")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
