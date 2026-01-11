# Vidhi-AI Project Structure

## Directory Overview

```
vidhi_ai/
│
├── data/                      # Data storage
│   ├── raw/                   # Downloaded PDFs and HTMLs from lawcommission.gov.np
│   ├── processed/             # Parsed and structured JSON files
│   └── chroma_db/             # Vector database (ChromaDB) storage
│
├── src/                       # Source code
│   ├── __init__.py
│   ├── schema.py              # Pydantic data models (Act, Chapter, Section, etc.)
│   │
│   ├── ingestion/             # Data ingestion layer
│   │   ├── __init__.py
│   │   ├── scraper.py         # Playwright-based web scraper
│   │   ├── parser.py          # PDF/HTML parser with Nepali Unicode support
│   │   └── pipeline.py        # Orchestration for scraping → parsing → indexing
│   │
│   ├── retrieval/             # RAG retrieval layer
│   │   ├── __init__.py
│   │   ├── indexer.py         # ChromaDB indexing logic
│   │   └── engine.py          # Semantic search engine
│   │
│   ├── reasoning/             # LLM reasoning layer
│   │   ├── __init__.py
│   │   └── chain.py           # OpenAI integration with RAG pipeline
│   │
│   └── api/                   # API server
│       ├── __init__.py
│       └── server.py          # FastAPI REST endpoints
│
├── tests/                     # Unit and integration tests
│   ├── test_parser.py         # Parser tests
│   └── test_retrieval.py      # Retrieval system tests
│
├── cli.py                     # Command-line interface
├── examples.py                # Usage examples
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── .env.example               # Environment configuration template
└── PROJECT_STRUCTURE.md       # This file
```

## Key Components

### 1. Data Models (`schema.py`)
Hierarchical Pydantic models representing Nepali legal structure:
- **Act**: Top-level document
- **Part** (भाग): Optional high-level grouping
- **Chapter** (परिच्छेद): Organizational unit
- **Section** (दफा): Legal provision
- **SubSection**: Subdivision of sections
- **Clause** (खण्ड): Smallest unit with specific provisions

### 2. Ingestion Pipeline
- **Scraper**: Navigates lawcommission.gov.np, downloads PDFs
- **Parser**: Converts PDFs to structured JSON using regex patterns for Nepali text
- **Pipeline**: Coordinates batch processing and indexing

### 3. RAG System
- **Indexer**: Embeds sections with context (Act + Chapter metadata)
- **Engine**: Vector similarity search with metadata filtering
- **Chain**: Combines retrieval + LLM for citation-backed answers

### 4. API Layer
- FastAPI server with `/chat` endpoint
- Handles bilingual queries
- Returns structured responses with citations

## Data Flow

```
1. Scraping
   lawcommission.gov.np → data/raw/*.pdf

2. Parsing
   data/raw/*.pdf → data/processed/*.json
   
3. Indexing
   data/processed/*.json → data/chroma_db/ (vector embeddings)
   
4. Querying
   User Query → Retrieval (ChromaDB) → LLM (OpenAI) → Answer
```

## Configuration Files

- **requirements.txt**: Python package dependencies
- **.env**: Environment variables (API keys, paths)
- **cli.py**: Entry point for all operations

## Testing Strategy

- **Unit Tests**: Individual component validation (parser, retrieval)
- **Integration Tests**: End-to-end pipeline testing
- **Golden Dataset**: Curated legal questions for evaluation

## Scalability Considerations

- **Incremental Indexing**: Add new Acts without rebuilding entire database
- **Metadata Filtering**: Distinguish between Acts with same section numbers
- **Chunking Strategy**: Section-level with parent context preservation
