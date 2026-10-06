#  DealSniper AI — Autonomous Freelance Job & Proposal Intelligence Machine

An end-to-end multi-modal AI system that analyzes freelance job postings, audits client risk, retrieves market rate benchmarks using a Knowledge Graph, drafts high-converting proposals, and generates spoken interview preparation briefs.

##  Architecture Overview

- **Vision Parsing (Pillar 4):** Qwen 3.8 27B Vision extracts job metadata, required skills, and client spend from screenshots.
- **Market Intelligence (Pillar 3):** Neo4j GraphRAG stores and queries hourly rate benchmarks and winning proposal hook patterns.
- **Multi-Agent Orchestration (Pillar 1):** LangGraph coordinates a Market Strategist, Proposal Copywriter, and an LLM Judge that audits proposals for generic AI clichés.
- **Audio Synthesis (Pillar 4):** Neural Text-to-Speech (Edge-TTS) and Whisper STT for voice memos and interview coaching briefs.
- **Decoupled Full-Stack (Pillar 2):** FastAPI microservice backend connected to an interactive Streamlit dashboard.

##  Quickstart

1. **Clone & Setup Environment:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/dealsniper-ai.git
   cd dealsniper-ai
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt