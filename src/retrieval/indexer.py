import os
import requests
import chromadb
from typing import List
from src.schema import Act, Section
from dotenv import load_dotenv

load_dotenv()

def get_openai_embedding(texts: List[str], api_key: str) -> List[List[float]]:
    """Get embeddings from OpenAI API with retry logic"""
    import time
    
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "text-embedding-3-small",
        "input": texts
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return [item["embedding"] for item in result["data"]]
            elif response.status_code == 429:
                wait_time = (attempt + 1) * 5  # 5s, 10s, 15s
                print(f"   ⚠️ Rate limited (429). Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"   ⚠️ Error: {e}. Retrying...")
            time.sleep(2)
            
    raise Exception("Max retries exceeded for OpenAI embedding")

class LegalIndexer:
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.persist_directory = persist_directory  # Store for reference
        self.collection_name = "nepali_laws"  # Store for reference
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        # Create collection without embedding function - we'll compute embeddings manually
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def index_act(self, act: Act):
        """
        Flattens an Act into Clause-level chunks for precise citations.
        Falls back to Section-level if no clauses detected.
        """
        import hashlib
        
        ids = []
        documents = []
        metadatas = []
        
        # Create short hash of act title for unique prefix
        act_hash = hashlib.md5(act.title.encode('utf-8')).hexdigest()[:8]

        for part_idx, part in enumerate(act.parts, 1):
            for chap_idx, chapter in enumerate(part.chapters, 1):
                for sec_idx, section in enumerate(chapter.sections, 1):
                    # Try clause-level indexing first
                    if section.clauses:
                        for clause_idx, clause in enumerate(section.clauses, 1):
                            chunk_text = (
                                f"Act: {act.title}\n"
                                f"Part: {part.part_number}\n"
                                f"Chapter: {chapter.title}\n"
                                f"Section (दफा) {section.section_number}\n"
                                f"Clause (खण्ड) {clause.clause_id}: {clause.content}"
                            )
                            # Unique ID: hash_part_chapter_sectionIDX_clause
                            doc_id = f"{act_hash}_p{part_idx}_c{chap_idx}_s{sec_idx}_cl{clause_idx}"
                            
                            ids.append(doc_id)
                            documents.append(chunk_text)
                            metadatas.append({
                                "act_title": act.title,
                                "part_number": part.part_number,
                                "chapter": chapter.title,
                                "section_number": section.section_number,
                                "clause_number": clause.clause_id,
                                "source_url": act.source_url
                            })
                    else:
                        # Fall back to section-level if no clauses
                        chunk_text = (
                            f"Act: {act.title}\n"
                            f"Part: {part.part_number}\n"
                            f"Chapter: {chapter.title}\n"
                            f"Section (दफा) {section.section_number}: {section.content}"
                        )
                        doc_id = f"{act_hash}_p{part_idx}_c{chap_idx}_s{sec_idx}"
                        
                        ids.append(doc_id)
                        documents.append(chunk_text)
                        metadatas.append({
                            "act_title": act.title,
                            "part_number": part.part_number,
                            "chapter": chapter.title,
                            "section_number": section.section_number,
                            "source_url": act.source_url
                        })
        
        # Handle Acts with direct chapters (no Parts)
        for chap_idx, chapter in enumerate(act.chapters, 1):
            for sec_idx, section in enumerate(chapter.sections, 1):
                # Try clause-level indexing first
                if section.clauses:
                    for clause_idx, clause in enumerate(section.clauses, 1):
                        chunk_text = (
                            f"Act: {act.title}\n"
                            f"Chapter: {chapter.title}\n"
                            f"Section (दफा) {section.section_number}\n"
                            f"Clause (खण्ड) {clause.clause_id}: {clause.content}"
                        )
                        doc_id = f"{act_hash}_c{chap_idx}_s{sec_idx}_cl{clause_idx}"
                        
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
                    doc_id = f"{act_hash}_c{chap_idx}_s{sec_idx}"
                    
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
            print(f"Indexed {len(ids)} chunks for {act.title[:40]}... ({clause_count} clauses, {section_count} sections)")

if __name__ == "__main__":
    pass
