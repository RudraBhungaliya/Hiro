import requests
import json

code_snippet = """
class UserService:
    def __init__(self, db):
        self.db = db

    def get_user(self, user_id):
        return self.db.query(user_id)

    def create_user(self, name, email):
        user = {"name": name, "email": email}
        return self.db.save(user)


class DatabaseService:
    def query(self, user_id):
        return {"id": user_id, "name": "Test User"}

    def save(self, data):
        return True
"""

prompt = f"""
Analyze this Python code and return ONLY a JSON object.
No explanation. No markdown. No code blocks. Just raw JSON.

Use exactly this structure:
{{
  "nodes": [
    {{"id": "1", "label": "ClassName", "type": "class"}}
  ],
  "edges": [
    {{"from": "1", "to": "2", "label": "depends on"}}
  ]
}}

Rules:
- Every class becomes a node
- Every method becomes a node with type "method"
- If class A uses class B add an edge from A to B
- If a class has a method add an edge from class to method
- IDs must be unique strings

Code:
{code_snippet}
"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }
)

raw = response.json()["response"]
print(raw)
print()
try:
    data = json.loads(raw)
    print("=== PARSED SUCCESSFULLY ===")
    print(f"Nodes: {len(data['nodes'])}")
    print(f"Edges: {len(data['edges'])}")
    for node in data["nodes"]:
        print(f"  node → {node['label']} ({node['type']})")
    for edge in data["edges"]:
        print(f"  edge → {edge['from']} to {edge['to']} ({edge['label']})")

except json.JSONDecodeError:
    print("=== JSON PARSE FAILED ===")
    print("AI wrapped it in markdown. Paste output here and we fix it.")