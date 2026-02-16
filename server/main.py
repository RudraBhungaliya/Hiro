from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from parser import analyze_directory
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    path: str

@app.get("/")
def read_root():
    return {"message": "Diagram Generation Engine API"}

from ai_service import analyze_codebase

import sys

def get_file_list(path):
    print(f"Scanning directory: {path}", file=sys.stderr)
    files = []
    
    # Gracefully handle file path (if user provides a file path instead of directory)
    if os.path.isfile(path):
         _, ext = os.path.splitext(path)
         return [{"path": path, "type": ext.lstrip('.').lower()}]

    limit = 1000 # Limit to avoid potential timeouts on massive directories
    count = 0
    try:
        for root, _, filenames in os.walk(path):
            if count >= limit:
                print(f"Warning: File limit ({limit}) reached", file=sys.stderr)
                break
            for filename in filenames:
                if count >= limit: break
                
                # Skip common ignored directories
                if any(x in root for x in [".git", "node_modules", "__pycache__", ".venv", ".idea", ".vscode"]):
                    continue
                    
                file_path = os.path.join(root, filename)
                _, ext = os.path.splitext(filename)
                files.append({
                    "path": file_path,
                    "type": ext.lstrip('.').lower()
                })
                count += 1
    except Exception as e:
        print(f"Error scanning directory: {e}", file=sys.stderr)
        
    print(f"Found {len(files)} files", file=sys.stderr)
    return files

@app.post("/api/analyze")
def analyze_code(request: AnalysisRequest):
    print(f"Received request for path: {request.path}", file=sys.stderr)
    if not os.path.exists(request.path):
        print("Path does not exist", file=sys.stderr)
        raise HTTPException(status_code=400, detail="Path does not exist")
    
    try:
        files = get_file_list(request.path)
        result = analyze_codebase(files)
        print("Analysis complete, returning result", file=sys.stderr)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error processing request: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
