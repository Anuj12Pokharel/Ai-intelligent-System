# Vidhi-AI: Nepali Legal Intelligence System

A production-grade legal chat system that indexes 300+ Acts from the Nepal Law Commission, providing precise legal answers with citations down to the specific clause (Khanda) while handling bilingual (Nepali/English) queries.

## Features

- **Hierarchical Data Ingestion**: Scrapes and parses legal documents into structured schemas (Act → Part → Chapter → Section → Clause)
- **Precise Citation**: Identifies exact legal provisions with Act, Chapter, and Section references
- **Bilingual Support**: Handles queries in both Nepali and English
- **Semantic Search**: Uses vector embeddings for accurate legal retrieval
- **Production-Ready API**: FastAPI server with comprehensive error handling
- **Scalable Architecture**: Modular design supporting 1,000+ Acts without re-indexing

##  Architecture

```
vidhi_ai/
├── data/
│   ├── raw/            # Downloaded PDFs/HTMLs
│   ├── processed/      # Structured JSON files
│   └── chroma_db/      # Vector database
├── src/
│   ├── schema.py       # Pydantic models
│   ├── ingestion/      # Scraping & parsing
│   │   ├── scraper.py
│   │   ├── parser.py
│   │   └── pipeline.py
│   ├── retrieval/      # Vector DB & search
│   │   ├── indexer.py
│   │   └── engine.py
│   ├── reasoning/      # LLM chains
│   │   └── chain.py
│   └── api/            # FastAPI server
│       └── server.py
├── tests/              # Unit tests
└── cli.py              # Command-line interface
```

## Quick Start

### Installation

```bash
# Clone and navigate
cd vidhi_ai

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for scraping)
playwright install

# Set OpenAI API key
export OPENAI_API_KEY="your-key-here"
```

### Usage

#### 1. Scrape Legal Documents
```bash
# Run the scraper (modify MAX_PAGES in scraper.py as needed)
python -m vidhi_ai.src.ingestion.scraper
```

#### 2. Process and Index
```bash
# Parse PDFs and build vector index
python cli.py ingest --limit 10
```

#### 3. Query the System
```bash
# CLI query
python cli.py ask "चोरीको सजाय के हो?"

# Or start the API server
python cli.py serve
```

#### 4. API Usage
```bash
# Start server
python cli.py serve --port 8000

# Query endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the punishment for theft?"}'
```

##  Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for LLM reasoning

### Scraper Configuration
Edit `src/ingestion/scraper.py`:
- `START_URL`: Target category URL
- `MAX_PAGES`: Pagination limit
- `DOWNLOAD_DIR`: Output directory

### Vector Database
Uses ChromaDB with persistent storage in `data/chroma_db/`.
Default embedding: `sentence-transformers/all-MiniLM-L6-v2`

##  Data Schema

```python
Act
├── title: str
├── act_year: str
├── source_url: str
├── parts: List[Part]
│   └── chapters: List[Chapter]
│       └── sections: List[Section]
│           ├── section_number: str
│           ├── content: str
│           └── sub_sections: List[SubSection]
│               └── clauses: List[Clause]
└── metadata: dict
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Test parser specifically
pytest tests/test_parser.py -v

# Test retrieval
pytest tests/test_retrieval.py -v
```

##  CLI Commands

```bash
# Check system status
python cli.py status

# Parse single PDF
python cli.py parse path/to/file.pdf --output structured.json

# Run ingestion pipeline
python cli.py ingest --raw-dir data/raw --limit 50

# Ask a question
python cli.py ask "न्यूनतम मजदूरी के हो?"

# Start API server
python cli.py serve --host 0.0.0.0 --port 8000
```

##  Technical Details

### Parser Features
- **Unicode Handling**: Robust Nepali numeral conversion (०-९ → 0-9)
- **Structure Detection**: Regex patterns for भाग, परिच्छेद, दफा, खण्ड
- **Fallback Mechanisms**: HTML extraction if PDF parsing fails

### RAG Pipeline
- **Chunking Strategy**: Section-level with parent context
- **Metadata Enrichment**: Act title, chapter, section stored with each chunk
- **Hybrid Retrieval**: Semantic + keyword matching (future enhancement)

### LLM Integration
- **System Prompt**: Enforces citation-first responses
- **Temperature**: 0 for deterministic legal answers
- **Context Window**: Top-k retrieved sections injected into prompt

##  Evaluation Criteria

### Citation Precision
- Accuracy in identifying exact Dapha and Khanda
- Tested against golden dataset of legal questions

### Ambiguity Management
- Metadata filtering prevents cross-Act confusion
- Explicit Act identification in all responses

### Bilingual Proficiency
- Preserves legal nuance in Nepali-English translation
- Query language auto-detected

## 🛠️ Production Readiness

- **Error Handling**: Comprehensive try-catch in scraper and parser
- **Rate Limiting**: Configurable delays in scraper
- **Logging**: Structured logging throughout pipeline
- **Scalability**: Incremental indexing support
- **Observability**: Status endpoint for health checks

##  License

This project is intended for educational and research purposes related to Nepali law.

##  Contributing

Contributions welcome! Focus areas:
- Improved OCR for scanned PDFs
- Enhanced clause detection
- Multilingual embedding models
- UI/UX for end users

##  Support

For issues or questions, please open a GitHub issue with:
- Error logs
- Sample input (if applicable)
- Expected vs actual behavior
