from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from agent import ResearchAgent
import os

app = FastAPI(title="AI Research Agent API")

class ResearchRequest(BaseModel):
    query: str
    api_key: Optional[str] = None
    depth: Optional[str] = "Standard (5 steps)"
    output_format: Optional[str] = "Detailed Report"

class ResearchResponse(BaseModel):
    query: str
    result: str
    steps_taken: int

class AskRequest(BaseModel):
    query: str
    api_key: Optional[str] = None

class AskResponse(BaseModel):
    query: str
    answer: str

@app.post("/research", response_model=ResearchResponse)
async def conduct_research(req: ResearchRequest):
    depth_map = {"Quick (3 steps)": 3, "Standard (5 steps)": 5, "Deep (7 steps)": 7}
    max_steps = depth_map.get(req.depth or "Standard (5 steps)", 5)
    
    agent = ResearchAgent(api_key=req.api_key, max_steps=max_steps, output_format=req.output_format)
    
    # Run the generator to completion
    steps_count = 0
    try:
        for step in agent.run(req.query):
            steps_count += 1
            if step.get("type") == "error":
                raise HTTPException(status_code=500, detail=step.get("text"))
        
        if not agent.final_result:
            raise HTTPException(status_code=500, detail="Agent failed to produce a result")
            
        return ResearchResponse(
            query=req.query,
            result=agent.final_result,
            steps_taken=steps_count
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    try:
        agent = ResearchAgent(api_key=req.api_key)
        # Direct answer using sub_model for speed
        prompt = f"Provide a direct, concise answer to this question: {req.query}"
        response = agent.sub_model.generate_content(prompt)
        return AskResponse(query=req.query, answer=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
