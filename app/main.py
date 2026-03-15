from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import fitz  # PyMuPDF
from .models import DeidRequest, DeidResponse, BatchDeidRequest, BatchDeidResponse, FeedbackRequest
from .pipeline.hybrid import DeidPipeline
import json
import os
import logging
import time

# Redirect HF Cache to a writable directory
os.environ["HF_HOME"] = os.path.join(os.getcwd(), ".hf_cache")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("clinical-deidentify")

app = FastAPI(
    title="Clinical-Deidentify API",
    description="Fast, hybrid PHI removal for clinical text",
    version="0.1.1" # Incremented for robustness release
)

# Initialize pipeline lazily or at startup
try:
    logger.info("Initializing DeidPipeline...")
    pipeline = DeidPipeline()
    logger.info("Pipeline initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize pipeline: {str(e)}")
    pipeline = None # Handle at endpoint level

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return FileResponse("app/static/index.html")

@app.get("/health")
async def health_check():
    """Diagnostic endpoint for Docker/K8s."""
    status = "healthy"
    model_loaded = pipeline is not None
    if not model_loaded:
        status = "unhealthy"
    return {
        "status": status,
        "model_loaded": model_loaded,
        "timestamp": time.time()
    }

@app.post("/deidentify", response_model=DeidResponse)
async def deidentify_text(request: DeidRequest):
    try:
        result = pipeline.deidentify(request.text, mode=request.mode)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deidentify/file", response_model=DeidResponse)
async def deidentify_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename.lower()
        
        if filename.endswith(".pdf"):
            # Extract text from PDF
            doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
        elif filename.endswith(".txt"):
            text = content.decode("utf-8")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload .pdf or .txt")

        if not text.strip():
            raise HTTPException(status_code=400, detail="File is empty or no text could be extracted.")

        result = pipeline.deidentify(text)
        return result
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch", response_model=BatchDeidResponse)
async def deidentify_batch(request: BatchDeidRequest):
    results = []
    for text in request.texts:
        try:
            results.append(pipeline.deidentify(text, mode=request.mode))
        except Exception as e:
            # In a real app, we might handle partial failures differently
            results.append({"original": text, "deidentified": "ERROR", "entities": []})
    return {"results": results}

@app.post("/feedback")
async def store_feedback(request: FeedbackRequest):
    # For now, just append to a local JSON file for active learning
    feedback_file = "feedback.jsonl"
    with open(feedback_file, "a") as f:
        f.write(json.dumps(request.dict()) + "\n")
    return {"status": "success", "message": "Feedback recorded"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
