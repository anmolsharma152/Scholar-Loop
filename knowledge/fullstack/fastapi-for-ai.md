---
topic: fullstack
difficulty: medium
tags: [fullstack, fastapi, python, ai-engineering]
last_sent:
review_count: 0
---

# FastAPI for AI Engineers

## FastAPI Overview

- Python 3.7+ web framework built on Starlette (async) and Pydantic (validation)
- Native async/await support; ASGI server (Uvicorn)
- Auto-generated OpenAPI (Swagger) docs from type hints
- 2-5x faster than Flask for async workloads

### Why FastAPI for AI/ML
- Async endpoints handle LLM API calls without blocking
- Pydantic validates LLM inputs/outputs (structured schemas)
- Background tasks for model loading, preprocessing
- WebSocket support for streaming token generation
- Native OpenAPI for client SDK generation

---

## Core Patterns

### Async Endpoints
```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/predict")
async def predict(request: PredictRequest):
    result = await run_inference(request.text)
    return PredictResponse(prediction=result)
```

Use async def when endpoint awaits I/O (DB, API, model call).
Use def (sync) for CPU-bound work; FastAPI runs it in threadpool.

### Pydantic Models
```python
from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

class PredictResponse(BaseModel):
    prediction: str
    confidence: float
    tokens_used: int
```

- Validation is automatic; invalid requests return 422
- Response model enforces output schema
- Field constraints: ge, le, min_length, regex patterns

### Dependency Injection
```python
from fastapi import Depends

def get_model():
    return loaded_model

@app.post("/predict")
async def predict(req: PredictRequest, model = Depends(get_model)):
    return await run_inference(model, req.text)
```

- Dependencies are resolved per-request
- Great for: DB sessions, auth, model singletons
- Chained dependencies for complex setup

### Background Tasks
```python
from fastapi import BackgroundTasks

@app.post("/predict-async")
async def predict_async(req: PredictRequest, bg: BackgroundTasks):
    task_id = generate_id()
    bg.add_task(run_inference_async, task_id, req.text)
    return {"task_id": task_id, "status": "queued"}
```

- Non-blocking: response returns immediately
- Use for: logging, async inference, cache warming

### Streaming Responses (LLM Token Streaming)
```python
from fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat(req: ChatRequest):
    async def token_generator():
        async for token in llm.stream(req.messages):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(token_generator(), media_type="text/event-stream")
```

### WebSocket for Real-Time
```python
@app.websocket("/ws/predict")
async def ws_predict(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        result = await run_inference(data)
        await websocket.send_json({"result": result})
```

---

## File Uploads (Model Artifacts, Data)

```python
from fastapi import UploadFile, File

@app.post("/upload-dataset")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    return {"rows": len(df), "columns": list(df.columns)}
```

---

## Error Handling

```python
from fastapi import HTTPException

@app.post("/predict")
async def predict(req: PredictRequest):
    if req.temperature < 0:
        raise HTTPException(status_code=400, detail="Temperature must be >= 0")
    try:
        return await run_inference(req)
    except ModelTimeout:
        raise HTTPException(status_code=503, detail="Model overloaded")
```

---

## Deployment

### Uvicorn (Development)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Gunicorn + Uvicorn Workers (Production)
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Considerations
- Readiness probe: /health endpoint
- Liveness probe: separate health check
- HPA: scale on CPU, memory, or custom metrics (queue depth)
- GPU resource limits in pod spec

---

## Security for AI Endpoints

- API key authentication via Header
- Rate limiting per user/tier (slowapi or Redis-backed)
- Input validation via Pydantic (prevent injection)
- Output filtering (toxicity, PII)
- CORS configuration for frontend access
- HTTPS termination at load balancer

---

## Interview Q&A Summary

| Question | Key Answer |
|---|---|
| WSGI vs ASGI? | WSGI is sync (Flask/Django); ASGI supports async + WebSockets |
| Why not Flask for LLM serving? | Flask is sync; blocks thread on each LLM call |
| How to stream LLM output? | StreamingResponse with SSE or WebSocket |
| How to handle model cold start? | Background task or startup event to preload model |
| OpenAPI auto-generation? | From Pydantic models + type hints; always in sync with code |
