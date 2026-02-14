import requests
import os
from dotenv import load_dotenv

load_dotenv()
# Your code snippet to analyze
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
# Send to local Ollama
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.2",
        "prompt": f"Analyze this Python code and describe: what classes exist, "
                  f"what methods each class has, and how the classes relate to each other.\n\nCode:\n{code_snippet}",
        "stream": False
    }
)

print(response.json()["response"])