# API Reference

Complete API documentation for the AI Product Search & Chatbot.

_Developed for AI PBL by Aditya Tripathi (Team: 5th Sem Students)_

## Base URL

```
Development: http://localhost:5000
Production: https://your-domain.com
```

## Authentication

Admin endpoints require authentication via one of two methods:

### Method 1: Token Authentication (Recommended)

Include the admin token in the request header:

```http
X-Admin-Token: your-admin-token-here
```

**Getting the Token**:
1. Check `persist/admin_token.txt` file
2. Or set via environment variable: `ADMIN_TOKEN=your-token`

### Method 2: Basic Authentication

Include username and password in the Authorization header:

```http
Authorization: Basic base64(username:password)
```

**Setting Credentials**:
- Use `/admin/reset_password` endpoint to set initial credentials
- Or set via environment variables: `ADMIN_USER` and `ADMIN_PASS`

---

## Public Endpoints

### GET /

Serves the web user interface.

**Response**: HTML page

**Example**:
```bash
curl http://localhost:5000/
```

---

### GET /search

Search for products with optional pagination and field selection.

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | - | Search query (e.g., "gaming laptop under 50000") |
| `page` | integer | No | 1 | Page number for pagination |
| `per_page` | integer | No | 10 | Results per page (max: 100) |
| `fields` | string | No | all | Comma-separated field names to return |

**Response**: JSON

```json
{
  "query": "gaming laptop under 50000",
  "results": [
    {
      "Brand": "Dell",
      "Model": "Inspiron 15",
      "Price": 45000,
      "RAM": "8GB",
      "Storage": "512GB SSD"
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 10,
  "total_pages": 2
}
```

**Examples**:

Basic search:
```bash
curl "http://localhost:5000/search?q=laptop"
```

Search with pagination:
```bash
curl "http://localhost:5000/search?q=mobile&page=2&per_page=5"
```

Search with specific fields:
```bash
curl "http://localhost:5000/search?q=headphones&fields=Brand,Model,Price"
```

Search with price constraints:
```bash
curl "http://localhost:5000/search?q=laptop under 50000"
curl "http://localhost:5000/search?q=phone between 10000 and 20000"
curl "http://localhost:5000/search?q=headphones above 2000"
```

**Error Responses**:

```json
{
  "error": "Missing query parameter 'q'"
}
```

---

### POST /chat

Interactive chatbot for conversational product search.

**Request Body**:

```json
{
  "message": "What are the best laptops for gaming?",
  "top_k": 5
}
```

**Parameters**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `message` | string | Yes | - | User's query or question |
| `top_k` | integer | No | 10 | Maximum number of results to return |

**Response**: JSON

```json
{
  "query": "What are the best laptops for gaming?",
  "reply": "Based on your query, here are relevant products:",
  "hits": [
    {
      "score": 0.85,
      "data": {
        "Brand": "ASUS",
        "Model": "ROG Strix G15",
        "Price": 89000,
        "Processor": "AMD Ryzen 7",
        "RAM": "16GB"
      }
    }
  ]
}
```

**Examples**:

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "laptop for programming under 60000"}'
```

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "best mobile camera", "top_k": 3}'
```

**Error Responses**:

```json
{
  "error": "Missing 'message' field in request"
}
```

---

## Admin Endpoints

All admin endpoints require authentication.

### POST /admin/rebuild

Rebuild the TF-IDF search index from CSV files.

**Use Cases**:
- After updating product CSV files
- When index becomes corrupted
- To refresh cached data

**Headers**:
```http
X-Admin-Token: your-admin-token
```

**Response**: JSON

```json
{
  "message": "TF-IDF index rebuilt successfully",
  "documents_indexed": 1250
}
```

**Example**:

```bash
curl -X POST http://localhost:5000/admin/rebuild \
  -H "X-Admin-Token: your-admin-token-here"
```

**Error Responses**:

Unauthorized (401):
```json
{
  "error": "Unauthorized. Admin authentication required."
}
```

Server Error (500):
```json
{
  "error": "Failed to rebuild index: <error details>"
}
```

---

### POST /admin/rotate

Generate a new admin authentication token.

**Use Cases**:
- Security best practice (rotate periodically)
- Token compromised or leaked
- Revoking old token access

**Headers**:
```http
X-Admin-Token: current-admin-token
```

**Response**: JSON

```json
{
  "message": "Admin token rotated successfully",
  "new_token": "new-generated-token-here"
}
```

**Example**:

```bash
curl -X POST http://localhost:5000/admin/rotate \
  -H "X-Admin-Token: current-token"
```

**Important**: Save the new token immediately. The old token becomes invalid.

---

### POST /admin/reset_password

Reset admin username and password for Basic Auth.

**Headers**:
```http
X-Admin-Token: your-admin-token
```

**Request Body**:

```json
{
  "new_username": "admin",
  "new_password": "SecurePassword123!"
}
```

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `new_username` | string | Yes | New admin username |
| `new_password` | string | Yes | New admin password (will be hashed) |

**Response**: JSON

```json
{
  "message": "Admin password reset successfully"
}
```

**Example**:

```bash
curl -X POST http://localhost:5000/admin/reset_password \
  -H "X-Admin-Token: your-token" \
  -H "Content-Type: application/json" \
  -d '{"new_username": "admin", "new_password": "NewPass123"}'
```

**Security Notes**:
- Password is hashed using bcrypt before storage
- Stored in `persist/admin_credentials.json`
- Never transmitted or stored in plain text

---

## Error Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 200 | Success | Request processed successfully |
| 400 | Bad Request | Missing required parameters, invalid JSON |
| 401 | Unauthorized | Invalid or missing authentication |
| 404 | Not Found | Invalid endpoint URL |
| 405 | Method Not Allowed | Wrong HTTP method (GET vs POST) |
| 500 | Internal Server Error | Server-side exception, check logs |

---

## Rate Limiting

Currently, there are no rate limits implemented. For production deployment, consider adding:

- Rate limiting middleware (Flask-Limiter)
- API key authentication for public endpoints
- Request throttling per IP address

---

## Response Headers

All responses include:

```http
Content-Type: application/json
Server: Werkzeug/X.X.X Python/3.X.X
Date: Thu, 09 Nov 2025 12:00:00 GMT
```

---

## Query Language

### Natural Language Queries

The search engine supports natural language with price parsing:

**Price Constraints**:
- `under X` or `below X` → max_price = X
- `above X` or `over X` → min_price = X
- `between X and Y` → min_price = X, max_price = Y
- `around X` or `near X` → min_price = 0.8*X, max_price = 1.2*X

**Examples**:
```
"gaming laptops under 50000"
"mobile phones between 10000 and 20000"
"headphones above 2000"
"laptops around 40000"
```

**Product Features**:
```
"laptop with 16GB RAM"
"phone with good camera"
"wireless headphones noise cancelling"
"gaming laptop RTX graphics"
```

**Brand Queries**:
```
"Dell laptops"
"Samsung mobiles"
"Sony headphones"
```

---

## Best Practices

### 1. Search Optimization

**Use Specific Queries**:
- ✅ Good: "Dell gaming laptop 16GB RAM under 60000"
- ❌ Bad: "laptop"w

**Leverage Price Filters**:
- Reduces result set size
- Faster response times
- More relevant results

### 2. Pagination

**Request Reasonable Page Sizes**:
```bash
# Good - efficient
curl "http://localhost:5000/search?q=laptop&per_page=10"

# Bad - large payload
curl "http://localhost:5000/search?q=laptop&per_page=1000"
```

### 3. Field Selection

**Request Only Needed Fields**:
```bash
# Minimal payload - faster
curl "http://localhost:5000/search?q=laptop&fields=Brand,Model,Price"

# Full payload - slower
curl "http://localhost:5000/search?q=laptop"
```

### 4. Admin Operations

**Rebuild Index Sparingly**:
- Only when CSV data changes
- Schedule during low-traffic periods
- Can take 5-30 seconds depending on data size

**Rotate Tokens Regularly**:
- Recommended: Every 90 days
- After suspected compromise: Immediately
- Keep new token secure

---

## Code Examples

### Python

```python
import requests

# Search request
response = requests.get(
    'http://localhost:5000/search',
    params={
        'q': 'gaming laptop',
        'page': 1,
        'per_page': 5
    }
)
data = response.json()
print(f"Found {data['total']} results")

# Chat request
response = requests.post(
    'http://localhost:5000/chat',
    json={'message': 'best laptop for coding'}
)
chat_data = response.json()
print(chat_data['reply'])

# Admin rebuild (with token)
response = requests.post(
    'http://localhost:5000/admin/rebuild',
    headers={'X-Admin-Token': 'your-token-here'}
)
print(response.json()['message'])
```

### JavaScript (Fetch API)

```javascript
// Search request
fetch('http://localhost:5000/search?q=laptop&page=1&per_page=5')
  .then(res => res.json())
  .then(data => {
    console.log(`Found ${data.total} results`);
    data.results.forEach(product => {
      console.log(`${product.Brand} ${product.Model} - ₹${product.Price}`);
    });
  });

// Chat request
fetch('http://localhost:5000/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: 'best phone under 20000'})
})
  .then(res => res.json())
  .then(data => console.log(data.reply));

// Admin rebuild
fetch('http://localhost:5000/admin/rebuild', {
  method: 'POST',
  headers: {'X-Admin-Token': 'your-token-here'}
})
  .then(res => res.json())
  .then(data => console.log(data.message));
```

### PowerShell

```powershell
# Search request
$response = Invoke-RestMethod -Uri "http://localhost:5000/search?q=laptop" -Method Get
Write-Host "Found $($response.total) results"

# Chat request
$body = @{message = "best laptop for gaming"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:5000/chat" -Method Post -Body $body -ContentType "application/json"
Write-Host $response.reply

# Admin rebuild
$headers = @{"X-Admin-Token" = "your-token-here"}
$response = Invoke-RestMethod -Uri "http://localhost:5000/admin/rebuild" -Method Post -Headers $headers
Write-Host $response.message
```

---

## Webhooks (Future Feature)

**Planned**: Webhook support for index rebuild notifications

```json
{
  "event": "index.rebuilt",
  "timestamp": "2025-11-09T12:00:00Z",
  "documents_indexed": 1250,
  "duration_ms": 2500
}
```

---

## Changelog

### Version 1.0.0 (November 2025)
- Initial release
- Search, chat, and admin endpoints
- TF-IDF retrieval engine
- Pagination and field selection
- Dual authentication (Basic + Token)
- Password hashing and security

---

**Last Updated**: November 2025  
**API Version**: 1.0.0
