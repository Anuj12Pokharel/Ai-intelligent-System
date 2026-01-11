import os
import requests
import chromadb
from typing import List
from src.schema import Act, Section
from dotenv import load_dotenv

load_dotenv()

def get_openai_embedding(texts: List[str], api_key: str) -> List[List[float]]:
    """Get embeddings from OpenAI API"""
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "text-embedding-3-small",
        "input": texts
    }
    response = requests.post(url, headers=headers, json=data, timeout=60)
    if response.status_code != 200:
        raise Exception(f"OpenAI API error: {response.status_code}")
    result = response.json()
    return [item["embedding"] for item in result["data"]]

class LegalIndexer:
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        # Create collection without embedding function - we'll compute embeddings manually
        self.collection = self.client.get_or_create_collection(
            name="nepali_laws",
            metadata={"hnsw:space": "cosine"}
        )

    def index_act(self, act: Act):
        """
        Flattens an Act into Clause-level chunks for precise citations.
        Falls back to Section-level if no clauses detected.
        """
        ids = []
        documents = []
        metadatas = []

        for part in act.parts:
            for chapter in part.chapters:
                for section in chapter.sections:
                    # Try clause-level indexing first
                    if section.clauses:
                        for clause in section.clauses:
                            chunk_text = (
                                f"Act: {act.title}\n"
                                f"Chapter: {chapter.title}\n"
                                f"Section (दफा) {section.section_number}\n"
                                f"Clause (खण्ड) {clause.clause_id}: {clause.content}"
                            )
                            doc_id = f"{act.title}_{section.section_number}_{clause.clause_id}".replace(" ", "_").replace(":", "")
                            
                            ids.append(doc_id)
                            documents.append(chunk_text)
                            metadatas.append({
                                "act_title": act.title,
                                "chapter": chapter.title,
                                "section_number": section.section_number,
                                "clause_number": clause.clause_id,
                                "source_url": act.source_url
                            })
                    else:
                        # Fall back to section-level if no clauses
                        chunk_text = (
                            f"Act: {act.title}\n"
                            f"Chapter: {chapter.title}\n"
                            f"Section (दफा) {section.section_number}: {section.content}"
                        )
                        doc_id = f"{act.title}_{section.section_number}".replace(" ", "_")
                        
                        ids.append(doc_id)
                        documents.append(chunk_text)
                        metadatas.append({
                            "act_title": act.title,
                            "chapter": chapter.title,
                            "section_number": section.section_number,
                            "source_url": act.source_url
                        })
        
        # Handle Acts with direct chapters (no Parts)
        for chapter in act.chapters:
            for section in chapter.sections:
                # Try clause-level indexing first
                if section.clauses:
                    for clause in section.clauses:
                        chunk_text = (
                            f"Act: {act.title}\n"
                            f"Chapter: {chapter.title}\n"
                            f"Section (दफा) {section.section_number}\n"
                            f"Clause (खण्ड) {clause.clause_id}: {clause.content}"
                        )
                        doc_id = f"{act.title}_{section.section_number}_{clause.clause_id}".replace(" ", "_").replace(":", "")
                        
                        ids.append(doc_id)
                        documents.append(chunk_text)
                        metadatas.append({
                            "act_title": act.title,
                            "chapter": chapter.title,
                            "section_number": section.section_number,
                            "clause_number": clause.clause_id,
                            "source_url": act.source_url
                        })
                else:
                    # Fall back to section-level if no clauses
                    chunk_text = (
                        f"Act: {act.title}\n"
                        f"Chapter: {chapter.title}\n"
                        f"Section (दफा) {section.section_number}: {section.content}"
                    )
                    doc_id = f"{act.title}_{section.section_number}".replace(" ", "_")
                    
                    ids.append(doc_id)
                    documents.append(chunk_text)
                    metadatas.append({
                        "act_title": act.title,
                        "chapter": chapter.title,
                        "section_number": section.section_number,
                        "source_url": act.source_url
                    })

        if ids:
            # Get embeddings from OpenAI
            embeddings = get_openai_embedding(documents, self.api_key)
            
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            clause_count = sum(1 for m in metadatas if "clause_number" in m)
            section_count = len(ids) - clause_count
            print(f"Indexed {len(ids)} chunks for {act.title} ({clause_count} clauses, {section_count} sections)")

if __name__ == "__main__":
    pass
