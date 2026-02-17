from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models.parser import parse_file
from models.folder_parser import parse_folder
from models.renderer import render

app = FastAPI()


class ParseRequest(BaseModel):
    mode: str    # "file" or "folder"
    target: str  # path to .py file or project folder


@app.post("/analyze")
def analyze(req: ParseRequest):
    try:
        if req.mode == "file":
            diagram_data = parse_file(req.target)

        elif req.mode == "folder":
            diagram_data = parse_folder(req.target)

        else:
            raise HTTPException(status_code=400, detail=f"Invalid mode '{req.mode}'. Use 'file' or 'folder'.")

        mermaid_code, description = render(diagram_data)

        return {
            "diagram": mermaid_code,
            "documentation": description
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}