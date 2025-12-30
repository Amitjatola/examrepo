---
description: Aerogate project rules - critical implementation details and constraints
---

# Aerogate Project Rules

## ⚠️ CRITICAL: Database Configuration

**This project REQUIRES PostgreSQL with pgvector and pg_trgm extensions.**

> [!CAUTION]
> NEVER switch the database to SQLite or any other database. The semantic search functionality depends on PostgreSQL-specific features.

### Required Configuration

```env
# .env file - DO NOT CHANGE
DATABASE_URL=postgresql+asyncpg://amitjatola@localhost:5432/aerogate
```

### Required PostgreSQL Extensions
```sql
CREATE EXTENSION IF NOT EXISTS vector;    -- For semantic embeddings
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- For fuzzy text search
```

### Model Configuration
The `Question` model MUST use `Vector(384)` for embeddings:
```python
from pgvector.sqlalchemy import Vector
embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(384)))
```

---

## Architecture Overview

### Backend (FastAPI + PostgreSQL)
- **Framework**: FastAPI with async SQLAlchemy
- **Database**: PostgreSQL with pgvector, pg_trgm
- **Embedding Model**: BGE-Large (384 dimensions)
- **Port**: 8000

### Frontend (Vite + React)
- **Framework**: Vite + React
- **Port**: 5173
- **API Base**: http://localhost:8000/api/v1

---

## Key API Endpoints

| Endpoint | Purpose | Depends On |
|----------|---------|------------|
| `/search?q=` | Semantic question search | pgvector, pg_trgm |
| `/questions?year=` | Filter questions by year | PostgreSQL |
| `/auth/register` | User signup | Users table |
| `/auth/login` | User login | Users table |

---

## File Structure - Critical Files

```
backend/
├── .env                          # ⚠️ DATABASE_URL - DO NOT CHANGE TO SQLITE
├── app/
│   ├── core/
│   │   ├── config.py            # Reads DATABASE_URL
│   │   ├── database.py          # SQLAlchemy engine
│   │   └── embedding.py         # BGE-Large embeddings
│   ├── domains/
│   │   ├── questions/
│   │   │   ├── models.py        # ⚠️ Must use Vector(384) for embedding
│   │   │   └── repository.py    # Uses pgvector cosine_distance
│   │   └── auth/
│   │       └── models.py        # User model
│   └── api/v1/
│       ├── search.py            # Main search endpoint
│       └── questions.py         # Question CRUD
```

---

## Running the Project

### Backend
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

---

## Importing Questions

```bash
# Single file
curl -X POST "http://localhost:8000/api/v1/questions/import/bulk" -F "file=@app/example.json"

# All example files
curl -X POST "http://localhost:8000/api/v1/questions/import/bulk" -F "file=@app/example.json"
curl -X POST "http://localhost:8000/api/v1/questions/import/bulk" -F "file=@app/example2.json"
curl -X POST "http://localhost:8000/api/v1/questions/import/bulk" -F "file=@app/example3.json"
```

---

## Common Issues & Solutions

### "Failed to fetch" on search
**Cause**: Database switched to SQLite  
**Solution**: Restore PostgreSQL in `.env`:
```
DATABASE_URL=postgresql+asyncpg://amitjatola@localhost:5432/aerogate
```

### "cosine_distance not found"
**Cause**: pgvector extension not enabled or model using JSON instead of Vector  
**Solution**: 
1. Enable extension: `CREATE EXTENSION IF NOT EXISTS vector;`
2. Use `Vector(384)` in models.py

### Tables missing after schema change
**Solution**: Restart backend server to recreate tables, then reimport questions.

---

## LaTeX Rendering

The project uses **remark-math + rehype-katex** for LaTeX rendering.

> [!IMPORTANT]
> The database stores LaTeX without `$` delimiters. The `LatexRenderer.jsx` component has a preprocessor that auto-wraps LaTeX patterns.

### Key Component
`frontend/src/components/LatexRenderer.jsx` - Preprocesses and renders LaTeX

### Usage
Always use `LatexRenderer` for content containing math:
```jsx
import LatexRenderer from './LatexRenderer';

<LatexRenderer text={question.question_text_latex || question.question_text} />
```

### Supported Patterns
- `\begin{bmatrix}...\end{bmatrix}` - Matrices
- `\frac{a}{b}` - Fractions
- `\det(A)` - Determinants
- Greek letters: `\lambda`, `\alpha`, etc.
