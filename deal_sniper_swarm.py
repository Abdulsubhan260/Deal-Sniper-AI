import os
import asyncio
from typing import TypedDict
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_neo4j import Neo4jGraph
from langgraph.graph import StateGraph, END
import edge_tts

load_dotenv()


copywriter_llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7)

# Heavy reasoning judge model
judge_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.0)

# Connect to your active Neo4j Cloud instance
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD").strip(),
    database=os.getenv("NEO4J_DATABASE")
)


class DealSniperState(TypedDict):
    job_data: str
    pitch_strategy: str
    market_intel: str
    proposal_draft: str
    evaluator_feedback: str
    approved: bool
    coaching_notes: str


# AGENT 1: Market Strategist (GraphRAG)
def market_strategist_node(state: DealSniperState):
    print("\n--- 1. AGENT: MARKET STRATEGIST QUERYING NEO4J ---")
    
    # Query Neo4j for skills, benchmarks, and hook patterns
    query = """
    MATCH (s:Skill)-[:BENCHMARK_RATE]->(b:Benchmark)
    OPTIONAL MATCH (s)-[:RECOMMENDED_HOOK]->(h:HookPattern)
    RETURN s.name AS Skill, b.rate_range AS Rate, b.tier AS Tier, h.rule AS HookRule
    """
    db_results = graph.query(query)
    
    intel_summary = "\n".join([
        f"- {r['Skill']}: Benchmark {r['Rate']} ({r['Tier']}). Hook Tip: {r.get('HookRule', 'Standard Hook')}"
        for r in db_results
    ])
    print(f"📊 Market Intelligence Retrieved:\n{intel_summary}")
    
    return {"market_intel": intel_summary}

# AGENT 2: Proposal Copywriter
def copywriter_node(state: DealSniperState):
    print("\n--- 2. AGENT: PROPOSAL COPYWRITER DRAFTING ---")
    
    job_data = state["job_data"]
    pitch_strategy = state["pitch_strategy"]
    market_intel = state["market_intel"]
    feedback = state.get("evaluator_feedback", "None")
    
    prompt = f"""
    You are an elite, top-rated freelance AI Engineer named Ali.
    Draft a winning, high-converting Upwork cover letter based on this data:
    
    [JOB POST DATA]:
    {job_data}
    
    [FREELANCER CUSTOM STRATEGY]:
    {pitch_strategy}
    
    [MARKET PRICING & HOOK RULES]:
    {market_intel}
    
    [SENIOR JUDGE CRITIQUE TO FIX]:
    {feedback}
    
    STRICT PROPOSAL RULES:
    1. NEVER start with generic greetings like 'Dear Hiring Manager', 'I hope this finds you well', or 'I am excited to apply'.
    2. Line 1 MUST be a direct, technical hook solving their core problem.
    3. Keep it under 200 words across 3 clean, punchy paragraphs.
    4. Explicitly integrate the custom strategy notes.
    5. End with a confident, low-friction call to action.
    """
    
    # TODO: Invoke copywriter_llm with the prompt
    response=copywriter_llm.invoke(prompt)
    return {
        "proposal_draft": response.content
    }
    # Return a dictionary updating "proposal_draft"
    

# AGENT 3: Senior Evaluator / Judge (LLM-as-a-Judge)
def evaluator_judge_node(state: DealSniperState):
    print("\n--- 3. AGENT: SENIOR JUDGE AUDITING PROPOSAL ---")
    
    draft = state["proposal_draft"]
    strategy = state["pitch_strategy"]
    
    audit_prompt = f"""
    You are a ruthless freelance agency director auditing this proposal:
    
    \"\"\"{draft}\"\"\"
    
    Required Freelancer Strategy: \"\"\"{strategy}\"\"\"
    
    AUDIT CHECKLIST:
    1. Does Line 1 open directly with a technical solution without generic pleasantries?
    2. Does the proposal include the required strategy (e.g., demo links, specific tech stack)?
    3. Is it free of robotic AI clichés (e.g., 'In today's fast-paced world', 'delighted to apply')?
    4. Is it under 200 words?
    
    If ALL rules pass: Output EXACTLY 'APPROVED'.
    If ANY rule fails: Output 'REJECTED: [1 sentence explaining exactly what the copywriter must fix]'.
    """
    
    # TODO: Invoke judge_llm with audit_prompt
    response=judge_llm.invoke(audit_prompt)
    if "APPROVED" in response.content:
        return {"approved": True,
                "evaluator_feedback":"APPROVED"}
    else:
        return{"approved": False,
               "evaluator_feedback":response.content}
    # TODO: Check if "APPROVED" is in response.content
    # If yes: return {"approved": True, "evaluator_feedback": "APPROVED"}
    # If no: return {"approved": False, "evaluator_feedback": response.content}
    

# ROUTER: Decision Gate
def should_continue(state: DealSniperState):
    # TODO: Check state["approved"]
    if state["approved"] ==True:
        return "coach"
    else:
        return "copywriter"
    # If True: return "coach"
    # If False: return "copywriter"
    

# AGENT 4: Interview Coach (Pillar 4 Audio)
def coach_node(state: DealSniperState):
    print("\n--- 4. AGENT: INTERVIEW COACH GENERATING BRIEF ---")
    
    draft = state["proposal_draft"]
    
    coach_prompt = f"""
    Review this winning proposal:
    \"{draft}\"
    
    Provide 2 concise, tactical talking points for the freelancer to use when the client messages them back for a discovery call.
    Keep it punchy and actionable.
    """
    
    # TODO: Invoke copywriter_llm with coach_prompt
    response=copywriter_llm.invoke(coach_prompt)
    return {
        "coaching_notes":response.content
    }
    # Return a dictionary updating "coaching_notes" with response.content
    

# ==========================================
# 4. WIRE THE LANGGRAPH STATE MACHINE
# ==========================================
workflow = StateGraph(DealSniperState)
workflow.add_node("strategist",market_strategist_node)
workflow.add_node("copywriter",copywriter_node)
workflow.add_node("judge",evaluator_judge_node)
workflow.add_node("coach",coach_node)
workflow.set_entry_point("strategist")
workflow.add_edge("strategist","copywriter")
workflow.add_edge("copywriter","judge")
workflow.add_conditional_edges("judge",should_continue)
workflow.add_edge("coach",END)
# TODO: Add nodes: "strategist", "copywriter", "judge", "coach"
# TODO: Set entry point to "strategist"
# TODO: Add standard edge: "strategist" -> "copywriter"
# TODO: Add standard edge: "copywriter" -> "judge"
# TODO: Add conditional edge from "judge" using should_continue
# TODO: Add standard edge: "coach" -> END

app = workflow.compile()

# ==========================================
# 5. EXECUTION PIPELINE
# ==========================================
async def main():
    # Simulated Ingestion Packet from Sprint 2
    sample_job_data = """
    Job Title: AI Phone Agent Demo for SMBs
    Client Country: France
    Payment Verified: True
    Total Spend: $40k+
    Primary Skills: AI Agents, LangGraph, FastAPI, Voice AI
    Core Problem: Build a working prototype of an AI phone agent that handles appointments and FAQs for small businesses.
    """
    
    sample_pitch_strategy = """
    Custom Notes: Offer a 2-week delivery timeline at $75/hour and include a link to our live Hugging Face microservice demo.
    """
    
    initial_state = {
        "job_data": sample_job_data,
        "pitch_strategy": sample_pitch_strategy,
        "market_intel": "",
        "proposal_draft": "",
        "evaluator_feedback": "",
        "approved": False,
        "coaching_notes": ""
    }
    
    print("🚀 LAUNCHING DEALSNIPER AI MULTI-AGENT SWARM...")
    final_output = app.invoke(initial_state)
    
    print("\n==================================================")
    print("      🏆 DEALSNIPER WINNING PROPOSAL READY        ")
    print("==================================================")
    print(f"\n{final_output['proposal_draft']}")
    
    print("\n==================================================")
    print("      🎯 INTERVIEW COACHING TALKING POINTS        ")
    print("==================================================")
    print(f"\n{final_output['coaching_notes']}")
    
    # Generate spoken coaching brief using Edge-TTS
    print("\n--- SYNTHESIZING SPOKEN COACHING AUDIO ---")
    comm = edge_tts.Communicate(final_output["coaching_notes"], "en-US-ChristopherNeural")
    await comm.save("interview_prep.mp3")
    print("✅ Spoken interview preparation saved to: interview_prep.mp3")

if __name__ == "__main__":
    asyncio.run(main())
