import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()

print("--- 1. CONNECTING TO NEO4J CLOUD DATABASE ---")
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD").strip(),
    database=os.getenv("NEO4J_DATABASE")
)

print("\n--- 2. SEEDING FREELANCE MARKET INTELLIGENCE ---")

# Step A: Clear old nodes
graph.query("MATCH (n) DETACH DELETE n")

# Step B: Seed new intelligence graph
seed_query = """
// 1. Core Tech Skills
MERGE (s1:Skill {name: 'LangGraph', category: 'Multi-Agent AI'})
MERGE (s2:Skill {name: 'FastAPI', category: 'Backend'})
MERGE (s3:Skill {name: 'Neo4j', category: 'Knowledge Graphs'})
MERGE (s4:Skill {name: 'Docker', category: 'DevOps'})
MERGE (s5:Skill {name: 'Streamlit', category: 'Frontend UI'})

// 2. Pricing Benchmarks
MERGE (b1:Benchmark {tier: 'High-Value Enterprise', rate_range: '$75-$100/hr'})
MERGE (b2:Benchmark {tier: 'Standard Development', rate_range: '$40-$65/hr'})

// 3. Client Risk Rules
MERGE (r1:RiskRule {name: 'UnverifiedPayment', severity: 'CRITICAL', deduction: 40, message: 'Client payment method is unverified.'})
MERGE (r2:RiskRule {name: 'ZeroHireRate', severity: 'HIGH', deduction: 30, message: 'Client has 0% hire rate over past jobs.'})
MERGE (r3:RiskRule {name: 'LowRating', severity: 'MEDIUM', deduction: 20, message: 'Client review score is below 4.5 stars.'})

// 4. Winning Proposal Hook Patterns
MERGE (h1:HookPattern {name: 'Proof_First', rule: 'Open line 1 with a direct reference to a similar live system built.'})
MERGE (h2:HookPattern {name: 'Architecture_First', rule: 'Open line 1 with a technical breakdown of how to solve their latency/memory issue.'})

// 5. Connect Relationships (The Wires)
MERGE (s1)-[:BENCHMARK_RATE]->(b1)
MERGE (s3)-[:BENCHMARK_RATE]->(b1)
MERGE (s2)-[:BENCHMARK_RATE]->(b2)
MERGE (s4)-[:BENCHMARK_RATE]->(b2)
MERGE (s5)-[:BENCHMARK_RATE]->(b2)

MERGE (s1)-[:PAIRS_WITH]->(s2)
MERGE (s1)-[:PAIRS_WITH]->(s3)
MERGE (s2)-[:PAIRS_WITH]->(s4)

MERGE (s1)-[:RECOMMENDED_HOOK]->(h2)
MERGE (s2)-[:RECOMMENDED_HOOK]->(h1)
"""

graph.query(seed_query)
graph.refresh_schema()
print(" Freelance Intelligence Knowledge Graph is seeded and active in the cloud!")

# ==========================================
# 3. VERIFICATION QUERY
# ==========================================
verify_query = """
MATCH (s:Skill)-[:BENCHMARK_RATE]->(b:Benchmark)
RETURN s.name AS Skill, b.rate_range AS MarketRate, b.tier AS Tier
"""
results = graph.query(verify_query)

print("\n--- 3. VERIFIED MARKET RATES ---")
for row in results:
    print(f"🔹 {row['Skill']} ({row['Tier']}): {row['MarketRate']}")
