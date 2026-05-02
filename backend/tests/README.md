# Backend tests

## Setup

```bash
cd backend
pip install -r requirements-dev.txt
```

Tests expect **PostgreSQL** (same features as production: `asyncpg`, JSONB, `pgvector`). Point pytest at a dedicated DB:

```bash
export AEROGATE_TEST_DATABASE_URL="postgresql+asyncpg://USER@localhost:5432/aerogate_test"
createdb aerogate_test   # once
pytest
```

Default URL in `conftest.py` is `postgresql+asyncpg://amitjatola@localhost:5432/aerogate_test` — override with `AEROGATE_TEST_DATABASE_URL` if your user/host differs.

## What runs

| Module | Coverage |
|--------|----------|
| `test_dashboard_stats.py` | `QuestionService.get_user_dashboard_stats` + `/api/v1/dashboard/stats` (extended fields) |
| `test_bookmarks_api.py` | `/api/v1/users/me/bookmarks` PUT/GET list/GET one/DELETE |
| Existing suites | auth, subscriptions, integration, search traps |

Run a subset:

```bash
pytest tests/test_dashboard_stats.py tests/test_bookmarks_api.py -q
```
