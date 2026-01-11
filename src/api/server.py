from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from src.reasoning.chain import LegalChain
# from vidhi_ai.src.ingestion.pipeline import run_ingestion # Placeholder

app = FastAPI(title="Vidhi-AI API", description="Nepali Legal Intelligence System")

# Global chain instance
# Note: Requires OPENAI_API_KEY env var
chain = LegalChain()

class ChatRequest(BaseModel):
    query: str
    history: list = []

class ChatResponse(BaseModel):
    answer: str
    citations: list = []

@app.get("/")
def health():
    return {"status": "ok", "system": "Vidhi-AI"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        if not request.query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # In a real async deployment, interacting with sync OpenAI client might block
        # better to use AsyncOpenAI or run in threadpool.
        answer = chain.answer(request.query)
        
        return ChatResponse(
            answer=answer,
            citations=[] # TODO: Parse citations from answer structure
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
def trigger_ingestion():
    return {"message": "Ingestion started (Mock). Use CLI for full batch process."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
