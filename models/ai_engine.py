"""
AI Engine — Groq (llama-3.3-70b-versatile) — with truncation repair + retry
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

# Output token caps
MAX_OUTPUT_TOKENS  = 8000
MAX_FILES_PER_LANG = 30   # hard cap per language in the summary sent to LLM


# ─────────────────────────────────────────────────────────────────────
# Summary builder
# ─────────────────────────────────────────────────────────────────────

def build_facts_summary(all_facts, aggressive=False):
    """
    Converts raw extractor output into a compact JSON summary for the LLM.

    aggressive=True  →  strip methods/functions, keep only file names, roles,
                        classes, and direct dependencies. Used when the first
                        attempt truncates.
    """
    summary = {}

    for language, facts_list in all_facts.items():
        summary[language] = []

        cap = MAX_FILES_PER_LANG if not aggressive else 20
        for facts in facts_list[:cap]:
            if not isinstance(facts, dict):
                continue

            filename = facts.get("filename", "unknown")

            if aggressive:
                classes = []
                for cls in facts.get("classes", []):
                    if not isinstance(cls, dict):
                        continue
                    classes.append({
                        "name": cls.get("name"),
                        "type": cls.get("type", "class"),
                        "annotations": cls.get("annotations", [])[:3],
                        "dependencies": cls.get("dependencies", [])[:4],
                    })
                file_summary = {"filename": filename}
                if classes:
                    file_summary["classes"] = classes
                spring = facts.get("spring_patterns", {})
                if isinstance(spring, dict) and any(spring.values()):
                    file_summary["spring_patterns"] = {k: v for k, v in spring.items() if v}
                requires = facts.get("requires", [])[:4]
                if requires:
                    file_summary["requires"] = requires
                summary[language].append(file_summary)
                continue

            # Normal (non-aggressive) path
            file_summary = {
                "filename": filename,
                "functions": facts.get("functions", [])[:8],
                "requires":  facts.get("requires", [])[:6],
            }

            imports = facts.get("imports", [])
            if imports:
                file_summary["imports"] = imports[:6]

            classes = []
            for cls in facts.get("classes", []):
                if not isinstance(cls, dict):
                    continue
                classes.append({
                    "name":         cls.get("name"),
                    "type":         cls.get("type", "class"),
                    "methods":      cls.get("methods", [])[:6],
                    "annotations":  cls.get("annotations", [])[:4],
                    "dependencies": cls.get("dependencies", [])[:5],
                })
            if classes:
                file_summary["classes"] = classes

            spring = facts.get("spring_patterns", {})
            if isinstance(spring, dict) and any(spring.values()):
                file_summary["spring_patterns"] = {k: v for k, v in spring.items() if v}

            components = facts.get("components", [])
            if components:
                file_summary["components"] = [
                    c["name"] for c in components if isinstance(c, dict)
                ][:6]

            calls = facts.get("calls", [])
            if calls:
                file_summary["calls"] = calls[:8]

            if any([
                file_summary.get("functions"),
                file_summary.get("classes"),
                file_summary.get("components"),
                file_summary.get("spring_patterns"),
                file_summary.get("requires"),
                file_summary.get("imports"),
            ]):
                summary[language].append(file_summary)

        if language in summary and not summary[language]:
            del summary[language]

    return summary


def count_summary_files(summary):
    return sum(len(v) for v in summary.values())


# ─────────────────────────────────────────────────────────────────────
# System prompt
# ─────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a Principal Software Architect at a FAANG-level company.
You have designed distributed systems, microservices, and enterprise backends for 20+ years.
Your architecture diagrams are used in board presentations and system design reviews.

You will receive a JSON summary of a codebase and must produce a world-class architecture diagram.

DIAGRAM RULES — NON NEGOTIABLE

NODE RULES:
1. Every file and class in the summary MUST become a node — never skip anything.
2. Add inferred infrastructure nodes implied by the code:
   - mongoose / sequelize / mysql / postgres / db.js  → add "Database" node
   - nodemailer / emailService                        → add "SMTP Server" node
   - jwt / passport / auth                            → add "Auth Layer" node
   - routes / router                                  → add "HTTP Request" client node
   - server.js / app.js / main.py                     → add "Client / Browser" node
3. Node labels = actual filename or class name — never genericize.
4. Every description must be specific to THIS project.
5. Role must be exactly one of:
   entry | router | controller | service | repository | database |
   middleware | entity | utility | external | client

EDGE RULES:
1. Every require() / import / @Autowired / dependency = a real edge.
2. Edge labels must be specific operations:
   GOOD: "POST /api/users", "queries attendance records", "validates JWT token"
   BAD:  "depends on", "uses", "calls"
3. Show the complete request lifecycle:
   Client -> entry -> middleware -> router -> controller -> service -> repository -> database

OUTPUT FORMAT — RETURN ONLY VALID JSON, NO MARKDOWN, NO BACKTICKS

{
  "project_name": "Full descriptive project name",
  "diagram": {
    "nodes": [
      {
        "id": "n1",
        "label": "exact filename or class name",
        "role": "entry | router | controller | service | repository | database | middleware | entity | utility | external | client",
        "language": "javascript | python | java | infrastructure",
        "description": "one precise sentence specific to this file"
      }
    ],
    "edges": [
      {
        "from": "n1",
        "to": "n2",
        "label": "specific operation"
      }
    ]
  },
  "description": {
    "overview": "4 sentences: what, who, stack, key capabilities",
    "components": [
      {
        "name": "exact filename or class name",
        "role": "precise role title",
        "what_it_does": "one sentence specific to this file"
      }
    ],
    "architecture_pattern": "3+ sentences: pattern name, data flow with real filenames, layer responsibilities"
  }
}"""


# ─────────────────────────────────────────────────────────────────────
# JSON repair helpers
# ─────────────────────────────────────────────────────────────────────

def _strip_markdown(raw: str) -> str:
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return raw.strip()


def _extract_json_object(raw: str) -> str:
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start != -1 and end > start:
        return raw[start:end]
    return raw


def _count_depth(text: str):
    """Return (brace_depth, bracket_depth) of unclosed structures."""
    depth_brace   = 0
    depth_bracket = 0
    in_string     = False
    escape_next   = False

    for ch in text:
        if escape_next:
            escape_next = False
            continue
        if ch == '\\' and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            depth_brace += 1
        elif ch == '}':
            depth_brace -= 1
        elif ch == '[':
            depth_bracket += 1
        elif ch == ']':
            depth_bracket -= 1

    return depth_brace, depth_bracket


def _attempt_truncation_repair(raw: str) -> dict:
    """
    When the model output is cut off mid-JSON (token limit hit), try to recover
    a partial but valid result by closing all open structures.

    Steps:
      1. Try json.loads directly — return immediately if it works.
      2. Trim back to the last complete object entry (last `},` or `}`).
      3. Count unclosed braces/brackets and append closing chars.
      4. If we get at least project_name + diagram.nodes, return the partial result.
    """
    # Step 1 — direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Step 2 — trim trailing incomplete object
    trimmed = raw.rstrip()
    # Find the last position that ends a complete JSON object item
    last_complete = max(trimmed.rfind("},"), trimmed.rfind("}\n"), trimmed.rfind("} "))
    if last_complete != -1:
        trimmed = trimmed[:last_complete + 1]

    # Step 3 — close open structures
    depth_brace, depth_bracket = _count_depth(trimmed)
    closing = ("]" * max(depth_bracket, 0)) + ("}" * max(depth_brace, 0))
    repaired = trimmed + closing

    try:
        result = json.loads(repaired)
        print("  ⚠  Response was truncated — repaired partial JSON successfully.")
        result.setdefault("project_name", "Analyzed Project")
        result.setdefault("diagram", {})
        result["diagram"].setdefault("nodes", [])
        result["diagram"].setdefault("edges", [])
        result.setdefault("description", {
            "overview": (
                "Analysis was truncated due to response length. "
                "Run with --clear-cache and try again, or reduce the repo size."
            ),
            "components": [],
            "architecture_pattern": "See diagram nodes for architecture details.",
        })
        return result
    except json.JSONDecodeError:
        pass

    raise ValueError("Could not repair truncated JSON from model response.")


# ─────────────────────────────────────────────────────────────────────
# Groq API call
# ─────────────────────────────────────────────────────────────────────

def _call_groq(summary: dict, max_tokens: int) -> dict:
    """Single Groq API call. Returns parsed result dict."""
    user_prompt = (
        "Analyze this codebase summary and return the architecture JSON.\n"
        "Every file must be a node. Every dependency must be an edge.\n"
        "All descriptions must be specific to THIS project.\n\n"
        f"Codebase summary:\n{json.dumps(summary, indent=2)}\n\n"
        "Return ONLY the JSON object. No explanation. No markdown. No backticks."
    )

    file_count = count_summary_files(summary)
    print(f"  → Groq call: {file_count} files, max_tokens={max_tokens}")

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0,
            max_tokens=max_tokens,
        )
    except Exception as e:
        raise ValueError(f"Groq API error: {str(e)}")

    raw = response.choices[0].message.content
    if not raw:
        raise ValueError("Groq returned an empty response.")
    raw = raw.strip()
    raw = _strip_markdown(raw)
    raw = _extract_json_object(raw)

    return _attempt_truncation_repair(raw)


# ─────────────────────────────────────────────────────────────────────
# Public entrypoint
# ─────────────────────────────────────────────────────────────────────

def analyze_with_gemini(all_facts):
    """
    Sends facts to Groq llama-3.3-70b, returns structured architecture result.
    Results are cached by codebase hash — same repo always returns the same diagram.

    Retry strategy:
      Pass 1 — normal summary,     max_tokens=8 000
      Pass 2 — normal summary,     max_tokens=16 000  (bigger output budget)
      Pass 3 — aggressive summary, max_tokens=8 000   (fewer files, bare-minimum data)
    """
    summary = build_facts_summary(all_facts, aggressive=False)

    if not summary:
        raise ValueError("No analyzable content found in the codebase.")

    # ── Cache check ───────────────────────────────────────────
    cached = get_cached(summary)
    if cached is not None:
        return cached

    file_count = count_summary_files(summary)
    print(f"Sending to Groq ({MODEL})... ({file_count} files in summary)")

    result     = None
    last_error = None

    # Pass 1
    try:
        result = _call_groq(summary, max_tokens=MAX_OUTPUT_TOKENS)
    except ValueError as e:
        last_error = e
        print(f"  ⚠  Pass 1 failed: {e}")

    # Pass 2 — bigger output window
    if result is None:
        print("  Retrying with larger output budget (16 000 tokens)...")
        try:
            result = _call_groq(summary, max_tokens=16000)
        except ValueError as e:
            last_error = e
            print(f"  ⚠  Pass 2 failed: {e}")

    # Pass 3 — compress the input
    if result is None:
        print("  Retrying with compressed summary (aggressive trim)...")
        small_summary = build_facts_summary(all_facts, aggressive=True)
        try:
            result = _call_groq(small_summary, max_tokens=MAX_OUTPUT_TOKENS)
        except ValueError as e:
            last_error = e
            print(f"  ⚠  Pass 3 failed: {e}")

    if result is None:
        raise ValueError(
            f"All Groq retry attempts failed.\nLast error: {last_error}"
        )

    # ── Cache successful result ───────────────────────────────
    save_to_cache(summary, result)

    return result
