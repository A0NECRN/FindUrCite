
import os
import sys
import json
import asyncio
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Add src to sys.path
sys.path.append(os.path.dirname(__file__))

from main import ResearchPipeline

app = FastAPI()

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount outputs directory
OUTPUTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "research_outputs"))
if not os.path.exists(OUTPUTS_DIR):
    os.makedirs(OUTPUTS_DIR)
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")

@app.get("/")
async def get():
    with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        request = json.loads(data)
        user_input = request.get("input", "")
        model = request.get("model", "qwen2.5:7b")
        
        # Create a specific output dir for this run
        timestamp = asyncio.get_event_loop().time() # or just use standard time
        # ResearchPipeline handles timestamping if we pass a base dir?
        # No, ResearchPipeline takes output_dir. 
        # Let's let ResearchPipeline create the timestamped dir inside OUTPUTS_DIR
        # But wait, ResearchPipeline logic:
        # if not output_dir: ... timestamp ...
        # If we pass output_dir, it uses it.
        
        # We want: OUTPUTS_DIR / <timestamp>
        run_id = time.strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(OUTPUTS_DIR, f"run_{run_id}")
        pdf_dir = os.path.join(run_dir, "pdfs")
        
        pipeline = ResearchPipeline(model=model, output_dir=run_dir, pdf_dir=pdf_dir)
        
        for event in pipeline.run(user_input):
            # If event is pdf_ready, we need to fix the path to be a URL
            if event['type'] == 'pdf_ready':
                # Absolute path: E:\...\research_outputs\run_...\pdfs\file.pdf
                # URL: /outputs/run_.../pdfs/file.pdf
                # We need to construct the relative path from OUTPUTS_DIR
                abs_path = event['pdf_path']
                rel_path = os.path.relpath(abs_path, OUTPUTS_DIR)
                # Ensure forward slashes for URL
                rel_path = rel_path.replace(os.sep, '/')
                event['pdf_url'] = f"/outputs/{rel_path}"
            
            await websocket.send_json(event)
            await asyncio.sleep(0.01) # Yield control briefly
            
        await websocket.send_json({"type": "complete"})
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_json({"type": "error", "content": str(e)})

if __name__ == "__main__":
    import uvicorn
    print("Starting server at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
