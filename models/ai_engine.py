"""
AI Engine — Groq (llama-3.3-70b-versatile)
Production-grade architecture analysis.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv
from models.diagram_cache import get_cached, save_to_cache

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"


def build_facts_summary(all_facts):
    summary = {}

    for language, facts_list in all_facts.items():
        summary[language] = []

        for facts in facts_list:
            if not isinstance(facts, dict):
                continue

            file_summary = {
                "filename":  facts.get("filename", "unknown"),
                "functions": facts.get("functions", [])[:10],
                "requires":  facts.get("requires", [])[:8],
            }

            classes = []
            for cls in facts.get("classes", []):
                if not isinstance(cls, dict):
                    continue
                classes.append({
                    "name":        cls.get("name"),
                    "type":        cls.get("type", "class"),
                    "methods":     cls.get("methods", [])[:8],
                    "annotations": cls.get("annotations", [])[:6],
                    "dependencies": cls.get("dependencies", [])[:6],
                })
            if classes:
                file_summary["classes"] = classes

            spring = facts.get("spring_patterns", {})
            if isinstance(spring, dict) and any(spring.values()):
                file_summary["spring_patterns"] = {
                    k: v for k, v in spring.items() if v
                }

            components = facts.get("components", [])
            if components:
                file_summary["components"] = [
                    c["name"] for c in components
                    if isinstance(c, dict)
                ][:8]

            calls = facts.get("calls", [])
            if calls:
                file_summary["calls"] = calls[:10]

            if any([
                file_summary.get("functions"),
                file_summary.get("classes"),
                file_summary.get("components"),
                file_summary.get("spring_patterns"),
            ]):
                summary[language].append(file_summary)

        if language in summary and not summary[language]:
            del summary[language]

    return summary


SYSTEM_PROMPT = """You are a Principal Software Architect at a FAANG-level company.
You have designed distributed systems, microservices, and enterprise backends for 20+ years.
Your architecture diagrams are used in board presentations and system design reviews.

You will receive a JSON summary of a codebase and must produce a world-class architecture diagram
that would impress a CTO, satisfy a senior engineer, and be understood by a product manager.

═══════════════════════════════════════════════════════════
DIAGRAM RULES — NON NEGOTIABLE
═══════════════════════════════════════════════════════════

NODE RULES:
1. Every single file and class in the summary MUST become a node — never skip anything
2. Add inferred infrastructure nodes that are implied by the code:
   - If you see db.js / mongoose / sequelize / mysql / postgres → add a "Database" node
   - If you see nodemailer / emailService → add an "SMTP / Email Server" node  
   - If you see jwt / passport / auth → add a "Auth Layer" node
   - If you see routes / router → the entry HTTP request must be shown as a node
   - If you see server.js / app.js → add a "Client / Browser" node at the top
3. Node labels = actual filename or class name — never rename or genericize
4. Every node description must be specific to THIS project — never say "handles application logic"
5. Roles must reflect the actual architectural role:
   - entry = app.js / server.js / main.py / Application.java
   - router = routes files
   - controller = controller files / @Controller / @RestController
   - service = service files / @Service / business logic
   - repository = repository files / @Repository / DAO / queries.js
   - database = actual DB node (inferred)
   - middleware = auth / validation / logging middleware
   - entity = @Entity / data models / schemas
   - utility = helper / util / formatter files
   - external = SMTP server / third party APIs / email server
   - client = browser / frontend / API client

EDGE RULES:
1. Every require() / import / @Autowired / dependency = a REAL edge
2. Edge labels must describe the EXACT data operation — never use vague labels like:
   - BAD: "depends on", "uses", "calls", "connects"  
   - GOOD: "POST /api/students", "queries attendance records", "sends email alert",
           "validates JWT token", "registers /student routes", "returns student JSON",
           "checks attendance threshold", "executes SQL query", "hashes password"
3. Show the COMPLETE request lifecycle as a flow:
   Client → server.js → middleware → router → controller → service → repository → database
   And the response flow back
4. Cross-cutting concerns must be shown:
   - Auth middleware connects to ALL protected routes
   - Email service connects FROM the service that triggers it
   - Database connects FROM all repositories/query files
5. If a service calls another service — show that edge
6. If an entity is used by a repository — show that edge

═══════════════════════════════════════════════════════════
DESCRIPTION RULES
═══════════════════════════════════════════════════════════

OVERVIEW: Must answer all 4 questions:
  - What does this system do? (domain + purpose)
  - Who uses it? (end users)
  - What technology stack is it built on?
  - What are the 2-3 most important things it does?

COMPONENTS: For every single file/class:
  - Name the exact file
  - Give its precise architectural role
  - Write one sentence that could only apply to THIS file in THIS project
  - No two component descriptions should sound alike

ARCHITECTURE PATTERN:
  - Name the exact pattern (e.g. "3-Tier Layered MVC", "Repository Pattern with Service Layer")
  - Walk through the EXACT data flow step by step using real filenames
  - Explain what each layer is responsible for
  - Mention any cross-cutting concerns (auth, email, logging)
  - Explain how the layers are decoupled from each other

═══════════════════════════════════════════════════════════
OUTPUT FORMAT — RETURN ONLY THIS JSON
═══════════════════════════════════════════════════════════

{
  "project_name": "Full descriptive project name e.g. University Attendance & Management System",
  "diagram": {
    "nodes": [
      {
        "id": "n1",
        "label": "exact filename or class name",
        "role": "entry | router | controller | service | repository | database | middleware | entity | utility | external | client",
        "language": "javascript | python | java | infrastructure",
        "description": "one precise sentence specific to this file in this project"
      }
    ],
    "edges": [
      {
        "from": "n1",
        "to": "n2",
        "label": "specific data operation e.g. queries student attendance records"
      }
    ]
  },
  "description": {
    "overview": "4 sentences answering: what, who, stack, key capabilities",
    "components": [
      {
        "name": "exact filename or class name",
        "role": "precise role title",
        "what_it_does": "one sentence that could only describe this specific file"
      }
    ],
    "architecture_pattern": "3+ sentences: pattern name, step-by-step data flow with real filenames, layer responsibilities, cross-cutting concerns"
  }
}"""


def analyze_with_gemini(all_facts):
    """
    Sends facts to Groq llama-3.3-70b, returns structured architecture result.
    Results are cached by codebase hash — same repo always returns the same diagram.
    Function name kept as analyze_with_gemini so no other file needs to change.
    """
    summary = build_facts_summary(all_facts)

    if not summary:
        raise ValueError("No analyzable content found in the codebase.")

    # ── Cache check ────────────────────────────────────────────
    cached = get_cached(summary)
    if cached is not None:
        return cached
    # ──────────────────────────────────────────────────────────

    if not summary:
        raise ValueError("No analyzable content found in the codebase.")

    user_prompt = f"""Analyze this codebase summary and return the architecture JSON.
Remember: every file must be a node, every dependency must be an edge, 
all descriptions must be specific to THIS project.

Codebase summary:
{json.dumps(summary, indent=2)}

Return ONLY the JSON object. No explanation. No markdown. No backticks."""

    print(f"Sending to Groq ({MODEL})...")

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt}
            ],
            temperature=0,
            max_tokens=6000,
        )
    except Exception as e:
        raise ValueError(f"Groq API error: {str(e)}")

    raw = response.choices[0].message.content.strip()

    if not raw:
        raise ValueError("Groq returned an empty response.")

    # Strip markdown blocks
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    if raw.endswith("```"):
        raw = raw[:-3].strip()

    # Extract JSON object
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Groq returned invalid JSON: {e}\n"
            f"Raw response preview:\n{raw[:500]}"
        )

    # ── Save to cache so next run is instant ──────────────────
    save_to_cache(summary, result)
    # ──────────────────────────────────────────────────────────

    return result