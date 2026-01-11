import os
import sys
import traceback
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

# Open a file to write output
with open('error_log.txt', 'w', encoding='utf-8') as f:
    f.write(f"API Key loaded: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}\n")
    f.write(f"API Key prefix: {os.getenv('OPENAI_API_KEY', '')[:20]}...\n\n")
    
    try:
        import chromadb
        from chromadb.utils import embedding_functions
        
        f.write("Creating OpenAI embedding function...\n")
        api_key = os.getenv("OPENAI_API_KEY")
        ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-3-small"
        )
        f.write("Embedding function created!\n")
        
        f.write("Testing embedding...\n")
        result = ef(["hello world"])
        f.write(f"Embedding result shape: {len(result[0])} dimensions\n")
        
        f.write("\n=== SUCCESS ===\n")
        
    except Exception as e:
        f.write(f"\nERROR: {type(e).__name__}: {e}\n\n")
        f.write(traceback.format_exc())

print("Output written to error_log.txt")
