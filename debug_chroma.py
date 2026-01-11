import sys
import traceback

try:
    import chromadb
    print(f"ChromaDB version: {chromadb.__version__}")
    
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    print("DefaultEmbeddingFunction imported")
    
    ef = DefaultEmbeddingFunction()
    print("Embedding function created")
    
    client = chromadb.PersistentClient(path="data/chroma_test3")
    print("Client created")
    
    col = client.get_or_create_collection("test_col", embedding_function=ef)
    print("Collection created")
    
    col.add(ids=["doc1"], documents=["This is a test document"])
    print("Document added!")
    
    print(f"Final count: {col.count()}")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    traceback.print_exc()
