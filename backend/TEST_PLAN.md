# Test Plan - Aerogate Critical Features

## Test Coverage Areas

### 1. Subscription System
- ✅ Trial creation on user signup
- ✅ Trial expiration after 7 days
- ✅ Premium access validation
- ✅ Subscription status API

### 2. Authentication
- ✅ User registration
- ✅ User login
- ✅ Token validation

### 3. Premium Access Control
- ✅ Non-logged-in users see locked state
- ✅ Trial users see premium content
- ✅ Expired trial users see upgrade prompt
- ✅ Free tier users see upgrade prompt

### 4. Core Features
- ✅ Question retrieval
- ✅ LaTeX rendering
- ✅ Question attempts recording

## Test Execution
Run tests with:
```bash
cd backend
pytest tests/ -v
```
