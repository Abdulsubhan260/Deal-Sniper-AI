import os
import asyncio
import base64
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import uvicorn
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_neo4j import Neo4jGraph
from langgraph.graph import StateGraph, END
import edge_tts

# Import your existing swarm logic and vision functions
from deal_sniper_swarm import app as swarm_app
from ingest_job import extract_job_metadata

load_dotenv()

api = FastAPI(
    title="DealSniper AI Backend Microservice",
    description="Decoupled Multi-Agent API for Freelance Job & Proposal Intelligence"
)

# Connect to Neo4j Cloud
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD").strip(),
    database="a7250f0e"
)

@api.post("/snipe-deal")
async def snipe_deal_endpoint(
    screenshot: UploadFile = File(...),
    custom_notes: str = Form("")
):
    print(f"\n--- 1. API RECEIVED JOB SCREENSHOT: {screenshot.filename} ---")
    
    try:
        # A. Save uploaded image temporarily
        temp_img_path = f"temp_{screenshot.filename}"
        with open(temp_img_path, "wb") as f:
            f.write(await screenshot.read())
            
        # B. Run Vision Extraction (Pillar 4)
        print("--- 2. EXTRACTING JOB METADATA VIA VISION ---")
        job_metadata = extract_job_metadata(temp_img_path)
        
        # C. Run LangGraph Multi-Agent Swarm (Pillars 1 & 3)
        print("--- 3. LAUNCHING MULTI-AGENT SWARM ---")
        strategy_text = custom_notes if custom_notes.strip() else "Pitch enterprise delivery and reliability."
        
        initial_state = {
            "job_data": job_metadata,
            "pitch_strategy": strategy_text,
            "market_intel": "",
            "proposal_draft": "",
            "evaluator_feedback": "",
            "approved": False,
            "coaching_notes": ""
        }
        
        swarm_result = swarm_app.invoke(initial_state)
        
        # D. Synthesize Audio Coaching (Pillar 4 Audio)
        audio_filename = "interview_prep.mp3"
        comm = edge_tts.Communicate(swarm_result["coaching_notes"], "en-US-ChristopherNeural")
        await comm.save(audio_filename)
        
        # Clean up temp image
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
            
        # Return structured, decoupled JSON response
        return {
            "status": "success",
            "job_metadata": job_metadata,
            "market_intel": swarm_result["market_intel"],
            "proposal": swarm_result["proposal_draft"],
            "coaching_notes": swarm_result["coaching_notes"],
            "audio_available": True
        }

    except Exception as e:
        print(f"Error in API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=7860)