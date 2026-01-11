"""
Example usage scripts demonstrating Vidhi-AI functionality
"""

# Example 1: Parse a single PDF file
def example_parse_pdf():
    from vidhi_ai.src.ingestion.parser import NepaliLegalParser
    
    parser = NepaliLegalParser(
        filepath="data/raw/sample_act.pdf",
        source_url="https://www.lawcommission.gov.np/content/123"
    )
    
    act = parser.parse()
    
    print(f"Act Title: {act.title}")
    print(f"Year: {act.act_year}")
    print(f"Chapters: {len(act.chapters)}")
    
    # Save to JSON
    with open("output.json", "w", encoding="utf-8") as f:
        f.write(act.model_dump_json(indent=2))

# Example 2: Build index from processed JSONs
def example_build_index():
    from vidhi_ai.src.ingestion.pipeline import IngestionPipeline
    from pathlib import Path
    import json
    
    pipeline = IngestionPipeline()
    
    # Process all JSONs in processed directory
    for json_file in Path("data/processed").glob("*.json"):
        pipeline.load_and_index_json(str(json_file))
    
    print("Indexing complete!")

# Example 3: Query the system
def example_query():
    from vidhi_ai.src.reasoning.chain import LegalChain
    import os
    
    # Ensure API key is set
    os.environ["OPENAI_API_KEY"] = "your-key-here"
    
    chain = LegalChain()
    
    questions = [
        "चोरीको सजाय के हो?",  # What is the punishment for theft?
        "What are the requirements for marriage registration?",
        "नागरिकताको लागि के आवश्यकताहरू छन्?"  # What are the requirements for citizenship?
    ]
    
    for question in questions:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        print(f"{'='*60}")
        answer = chain.answer(question)
        print(answer)

# Example 4: API Client
def example_api_client():
    import requests
    
    # Assuming server is running on localhost:8000
    response = requests.post(
        "http://localhost:8000/chat",
        json={
            "query": "What is the legal age for marriage in Nepal?",
            "history": []
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Answer: {data['answer']}")
    else:
        print(f"Error: {response.status_code}")

# Example 5: Batch Processing
def example_batch_processing():
    from vidhi_ai.src.ingestion.pipeline import IngestionPipeline
    
    pipeline = IngestionPipeline(
        raw_data_dir="data/raw",
        processed_data_dir="data/processed"
    )
    
    # Process first 50 PDFs
    pipeline.run_batch(limit=50)

if __name__ == "__main__":
    print("Vidhi-AI Usage Examples")
    print("Uncomment the example you want to run\n")
    
    # example_parse_pdf()
    # example_build_index()
    # example_query()
    # example_api_client()
    # example_batch_processing()
