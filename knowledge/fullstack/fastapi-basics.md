---
difficulty: easy
last_sent:
review_count: 0
tags:
  - fastapi
  - python
  - api
topic: fullstack
---

# FastAPI Basics

FastAPI is a modern, high-performance Python web framework for building APIs. It leverages type hints for automatic request validation, serialization, and interactive documentation (Swagger UI and ReDoc) with zero configuration.

## Installation and Setup

```bash
pip install fastapi uvicorn
```

```python
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Hello, world!"}

# Run: uvicorn main:app --reload
```

## Path Parameters

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    return {"file_path": file_path}
```

FastAPI validates types automatically—`user_id: int` ensures the path segment is an integer, returning 422 on mismatch.

## Query Parameters

```python
from typing import Optional

@app.get("/search")
def search(q: str, page: int = 1, limit: int = 10, sort: Optional[str] = None):
    return {"query": q, "page": page, "limit": limit, "sort": sort}
```

Query params with defaults are optional. Those without defaults are required.

## Request Body with Pydantic

```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)

@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    return {"id": 1, **user.model_dump()}
```

Pydantic validates and parses the JSON body. Invalid requests automatically return detailed error messages.

## Response Models

Control the shape of returned data without exposing internal fields.

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    return {"id": 1, "name": user.name, "email": user.email}
```

FastAPI strips any fields not in `UserResponse` from the output.

## HTTP Methods

```python
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate):
    return {"id": user_id, **user.model_dump()}

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    pass

@app.patch("/users/{user_id}", response_model=UserResponse)
def patch_user(user_id: int, user: UserCreate):
    return {"id": user_id, **user.model_dump()}
```

## Status Codes and Headers

```python
from fastapi import Header, HTTPException

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}

@app.get("/check-header")
def check_header(x_request_id: str = Header(...)):
    return {"request_id": x_request_id}
```

## File Uploads

```python
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
    }
```

## Automatic Docs

FastAPI generates interactive docs at:
- `/docs` — Swagger UI
- `/redoc` — ReDoc

These are built from your type hints, Pydantic models, and route definitions—no manual documentation needed.

## Common Bugs

- **Missing request body on POST**: Sending form data instead of JSON when the endpoint expects a Pydantic model returns 422. Use `Form(...)` for form data.
- **Mutable default arguments**: `def endpoint(items: list = [])` is a bug. Use `None` default with `= items or []` inside.
- **`async def` vs `def`**: `def` routes run in a thread pool (good for sync DB calls). `async def` runs on the event loop—never call blocking I/O in `async def`.
- **CORS errors**: Forgetting `CORSMiddleware` when the frontend is on a different origin.
