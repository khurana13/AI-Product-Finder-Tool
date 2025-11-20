# Architecture Documentation

## System Overview

The AI Product Search & Chatbot is a Flask-based web application that uses TF-IDF (Term Frequency-Inverse Document Frequency) for intelligent product retrieval and natural language search.

## Core Components

### 1. Search Engine (`app/search_engine.py`)

**Purpose**: Core TF-IDF retrieval engine for product search

**Key Functions**:
- `load_data()`: Loads CSV files from `data/` directory
- `build_corpus_from_data()`: Converts product data into searchable text corpus
- `build_tfidf_index()`: Creates TF-IDF vectorizer and matrix
- `retrieve_with_index()`: Performs similarity search using cosine similarity
- `parse_price_constraints()`: Extracts price filters from natural language queries

**Technologies**:
- pandas for data manipulation
- scikit-learn's TfidfVectorizer for text vectorization
- cosine_similarity for ranking results

### 2. Flask API (`app/main.py`)

**Purpose**: REST API server and web interface

**Endpoints**:

**Public Endpoints**:
- `GET /`: Serves the web UI
- `GET /search`: Product search with pagination and field selection
- `POST /chat`: Chatbot interface for conversational search

**Admin Endpoints** (require authentication):
- `POST /admin/rebuild`: Rebuild TF-IDF index
- `POST /admin/rotate`: Generate new admin token
- `POST /admin/reset_password`: Reset admin credentials

**Authentication**:
- Dual-mode: Basic Auth (username/password) OR Token Auth (X-Admin-Token header)
- Passwords hashed using Werkzeug's bcrypt implementation
- Credentials persisted in `persist/admin_credentials.json`

### 3. Web Interface (`static/`)

**Purpose**: User-facing single-page application

**Files**:
- `index.html`: Main HTML structure with hero section and interactive cards
- `styles.css`: Dark gradient theme with glassmorphism effects
- `app.js`: Frontend logic for API calls, pagination, animations

**Features**:
- Responsive design with mobile support
- Real-time search and chat
- Paginated results display
- Admin panel for index management

## Data Flow

### Search Flow
```
User Query → Frontend (app.js) → /search endpoint → search_engine.py
  ↓
TF-IDF Index (cosine similarity) → Ranked Results
  ↓
Price Filtering → Pagination → JSON Response → Frontend Display
```

### Chat Flow
```
User Message → Frontend → /chat endpoint → search_engine.py
  ↓
TF-IDF Retrieval (top_k results) → Format Response
  ↓
JSON Response with suggestions → Frontend Display
```

### Admin Flow
```
Admin Action → Frontend with Auth Token → Admin Endpoint
  ↓
Authentication Check (Basic Auth or Token)
  ↓
Action (rebuild index, rotate token, reset password)
  ↓
Success Response → Update Frontend
```

## Persistence Layer

### Directory: `persist/`

**Files**:
- `tfidf_vectorizer.joblib`: Serialized TfidfVectorizer (sklearn model)
- `tfidf_matrix.joblib`: Serialized TF-IDF sparse matrix
- `corpus.joblib`: Cached text corpus
- `metadata.joblib`: Product metadata for result mapping
- `admin_token.txt`: Admin authentication token (UUID)
- `admin_credentials.json`: Hashed username/password

**Benefits**:
- Faster application startup (no need to rebuild index)
- Persistent admin configuration across restarts
- Reduced CSV parsing overhead

## TF-IDF Implementation

### Vectorization
```python
TfidfVectorizer(
    max_features=1000,    # Top 1000 most important terms
    min_df=1,             # Term must appear in at least 1 document
    max_df=0.85,          # Ignore terms in >85% of documents
    stop_words='english'  # Remove common English words
)
```

### Similarity Scoring
- Uses cosine similarity to compare query vector with document vectors
- Scores range from 0 (no similarity) to 1 (identical)
- Results sorted by score in descending order
- Configurable top_k parameter for result limiting

## Price Parsing

**Supported Patterns**:
- "under X" / "below X" → max_price = X
- "above X" / "over X" → min_price = X
- "between X and Y" → min_price = X, max_price = Y
- "around X" / "near X" → min_price = 0.8*X, max_price = 1.2*X

**Implementation**:
- Regex pattern matching on query text
- Extraction of numeric values
- Conversion to price range filters

## Security Features

### Authentication Methods

1. **Basic Authentication**:
   - Username and password sent in Authorization header
   - Password hashed using bcrypt (via Werkzeug)
   - Credentials stored in `persist/admin_credentials.json`

2. **Token Authentication**:
   - UUID-based token generated with `secrets.token_urlsafe(24)`
   - Token sent in `X-Admin-Token` header
   - Stored in `persist/admin_token.txt`

### Password Hashing
```python
generate_password_hash(password, method='pbkdf2:sha256')
check_password_hash(hash, password)
```

## Configuration Management

### Environment Variables (`.env`)
- `FLASK_ENV`: development/production/testing
- `SECRET_KEY`: Flask secret key for sessions
- `ADMIN_USER`: Default admin username
- `ADMIN_PASS`: Default admin password
- `ADMIN_TOKEN`: Pre-set admin token
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 5000)

### Config Classes (`config/config.py`)
- `DevelopmentConfig`: Debug mode enabled
- `ProductionConfig`: Debug disabled, requires SECRET_KEY
- `TestingConfig`: Testing mode enabled

## Deployment Architecture

### Development
```
python run.py
  ↓
Flask Development Server (Werkzeug)
  ↓
localhost:5000
```

### Production
```
gunicorn -w 4 -b 0.0.0.0:5000 "app.main:app"
  ↓
Gunicorn WSGI Server (4 workers)
  ↓
Production Server
```

### Docker
```
Dockerfile → Python 3.9 Image
  ↓
Install Requirements
  ↓
Copy Application Files
  ↓
Gunicorn Command
  ↓
Container on Port 5000
```

## Performance Considerations

### Optimization Strategies

1. **Index Persistence**:
   - TF-IDF index built once and cached to disk
   - Subsequent startups load from `.joblib` files
   - Reduces startup time by ~70%

2. **Pagination**:
   - Results limited by page size (default: 10)
   - Reduces response payload size
   - Improves frontend rendering speed

3. **Field Selection**:
   - Optional parameter to return only specific fields
   - Reduces JSON response size
   - Bandwidth optimization for mobile clients

4. **Sparse Matrix**:
   - TF-IDF matrix stored as sparse matrix (scipy.sparse)
   - Memory-efficient for large datasets
   - Fast cosine similarity computation

## Error Handling

### Common Scenarios

1. **CSV Files Missing**:
   - `load_data()` returns None
   - API endpoints return graceful error messages
   - Application continues with empty dataset

2. **TF-IDF Build Failure**:
   - Falls back to keyword-based search
   - Simple token matching as backup
   - No index persistence

3. **Authentication Failure**:
   - Returns 401 Unauthorized
   - Clear error message in JSON response
   - Logs authentication attempts

4. **Invalid Query Parameters**:
   - Default values applied
   - Validation for page numbers, page size
   - Error messages for malformed requests

## Testing Strategy

### Unit Tests (`tests/test_search_engine.py`)
- Data loading validation
- Corpus building verification
- Price parsing accuracy
- TF-IDF index construction
- Retrieval result validation

### API Tests (`tests/test_api.py`)
- Endpoint availability
- Request/response validation
- Authentication checks
- Error handling verification
- Status code validation

### Running Tests
```powershell
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_api.py -v
```

## Future Enhancements

### Planned Features
1. **Multi-language Support**: Expand beyond English
2. **Advanced Filters**: Brand, RAM, storage in UI
3. **User Sessions**: Save search history
4. **Analytics Dashboard**: Track popular queries
5. **Recommendation Engine**: Collaborative filtering
6. **GraphQL API**: Alternative to REST endpoints
7. **WebSocket Support**: Real-time updates
8. **Elasticsearch Integration**: For larger datasets

### Scalability Improvements
1. **Redis Caching**: Cache frequent queries
2. **Database Migration**: Move from CSV to PostgreSQL
3. **Load Balancing**: Multiple Gunicorn instances
4. **CDN Integration**: Serve static assets via CDN
5. **Async Processing**: Celery for index rebuilding

## Monitoring & Logging

### Current Implementation
- Flask development server logs to console
- Error stack traces in debug mode
- Authentication attempts logged

### Production Recommendations
1. **Structured Logging**: JSON format with timestamps
2. **Log Aggregation**: ELK Stack or Splunk
3. **Performance Monitoring**: New Relic, Datadog
4. **Error Tracking**: Sentry for exception tracking
5. **Uptime Monitoring**: Pingdom, StatusCake

## Maintenance

### Regular Tasks
1. **Update Dependencies**: Monthly security patches
2. **Rebuild Index**: When CSV data changes
3. **Rotate Tokens**: Quarterly admin token rotation
4. **Backup Data**: Weekly backup of `persist/` and `data/`
5. **Review Logs**: Check for anomalies and errors

### Troubleshooting Guide

**Problem**: Index not loading
- **Solution**: Check `persist/` directory permissions, rebuild index via `/admin/rebuild`

**Problem**: Search returns no results
- **Solution**: Verify CSV files in `data/`, check query formatting

**Problem**: Authentication fails
- **Solution**: Reset password via `/admin/reset_password`, check token in `persist/admin_token.txt`

**Problem**: Slow search response
- **Solution**: Reduce `top_k` parameter, enable pagination, rebuild index with lower `max_features`

---

**Last Updated**: November 2025
**Version**: 1.0.0
