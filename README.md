# Student Project: Product Search & Chatbot

This repository is a small student project implementing a product search and chatbot using TF-IDF retrieval and a minimal Flask backend.

Author: Sneha Khurana and team
Course: AI PBL / Information Retrieval
Date: 2025-11-09

Credit: Completely developed by Sneha Khurana and team.

Team Members:

1. Sneha Khurana — Roll: 1/23/SET/BCS/502
2. Aaditya Thakaran — Roll: 1/23/SET/BCS/496
3. Manya Anand — Roll: 1/23/SET/BCS/555
4. Sanandita Debnath — Roll: 1/23/SET/BCS/506

All team members are from Manav Rachna International Institute of Research and Studies (MRIIRS).



A Flask-based intelligent product search engine and chatbot powered by TF-IDF (Term Frequency-Inverse Document Frequency) retrieval. Search and chat about laptops, mobiles, and headphones using natural language queries.This project contains simple product CSV datasets and a command-line tool to search and chat with the product data.



## ✨ FeaturesFeatures

- Product search (filter by category, brand, RAM, storage, price range)

- 🔍 **Advanced Product Search**: Search across multiple product categories with natural language- Chatbot mode: ask natural language queries; the bot finds relevant product rows using TF-IDF (scikit-learn) or a keyword fallback.

- 💬 **Intelligent Chatbot**: Ask questions about products and get contextual responses

- 💰 **Price Filtering**: Use queries like "laptops under 2000" or "phones between 5000 and 10000"Requirements

- 🎨 **Modern Dark UI**: Gradient-themed responsive web interface with animations- Python 3.8+

- 🔐 **Admin Controls**: Secure endpoints for index rebuilding and token management- See `requirements.txt` (install with pip install -r requirements.txt)

- 💾 **Persistent Index**: TF-IDF index cached on disk for faster restarts

- 📊 **Paginated Results**: Efficient data presentation with customizable fieldsRunning

1. Ensure the CSV files (`laptop.csv`, `mobile.csv`, `headphone.csv`) are in the same folder as `ai1.py`.

## 📁 Project Structure2. (Optional) Create a virtualenv and install dependencies:



``````powershell

AI PBL/python -m venv .venv; .\.venv\Scripts\Activate; pip install -r requirements.txt

├── app/```

│   ├── __init__.py          # Package initialization

│   ├── main.py              # Flask app & API routes3. Run the script:

│   └── search_engine.py     # TF-IDF search engine core

├── config/```powershell

│   └── (configuration files)python .\ai1.py

├── data/```

│   ├── laptop.csv           # Laptop product data

│   ├── mobile.csv           # Mobile product dataChoose mode 1 for product search or mode 2 for the chatbot.

│   └── headphone.csv        # Headphone product data

├── docs/Notes

│   └── (documentation files)- If `scikit-learn` is not installed, the chatbot will still work with a simpler keyword matching fallback.

├── persist/- The bot is retrieval-based (it returns rows from the CSVs); it's not a generative LLM.
│   ├── tfidf_vectorizer.joblib  # Cached TF-IDF vectorizer
│   ├── tfidf_matrix.joblib      # Cached TF-IDF matrix
│   ├── corpus.joblib            # Cached corpus
│   ├── metadata.joblib          # Cached metadata
│   ├── admin_token.txt          # Admin authentication token
│   └── admin_credentials.json   # Hashed admin credentials
├── static/
│   ├── index.html           # Web UI
│   ├── styles.css           # Dark gradient theme
│   └── app.js               # Frontend JavaScript
├── tests/
│   └── (test files)
├── archive/
│   └── (deprecated files)
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore patterns
├── requirements.txt         # Python dependencies
└── run.py                   # Application entrypoint
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```powershell
   git clone <repository-url>
   cd "AI PBL"
   ```

2. **Create and activate virtual environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (Optional)
   ```powershell
   Copy-Item .env.example .env
   # Edit .env with your preferred settings
   ```

5. **Run the application**
   ```powershell
   python run.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

## 📖 API Documentation

### Public Endpoints

#### `GET /`
Returns the web UI (index.html)

#### `GET /search`
Search for products across all categories.

**Query Parameters:**
- `q` (string, required): Search query
- `page` (int, optional, default=1): Page number
- `per_page` (int, optional, default=10): Results per page
- `fields` (string, optional): Comma-separated field names to return

**Example:**
```bash
GET /search?q=gaming laptop under 50000&page=1&per_page=5&fields=Brand,Model,Price
```

**Response:**
```json
{
  "query": "gaming laptop under 50000",
  "results": [...],
  "total": 15,
  "page": 1,
  "per_page": 5,
  "total_pages": 3
}
```

#### `POST /chat`
Chat with the AI about products.

**Request Body:**
```json
{
  "message": "What are the best laptops for gaming?"
}
```

**Response:**
```json
{
  "reply": "Based on your query, here are relevant products...",
  "suggestions": [...]
}
```

### Admin Endpoints

All admin endpoints require authentication via:
- **Basic Auth**: Username and password (hashed with bcrypt)
- **OR Token Auth**: `X-Admin-Token` header

#### `POST /admin/rebuild`
Rebuild the TF-IDF index from CSV files.

**Headers:**
```
X-Admin-Token: your-admin-token
```

**Response:**
```json
{
  "message": "TF-IDF index rebuilt successfully"
}
```

#### `POST /admin/rotate`
Generate a new admin authentication token.

**Response:**
```json
{
  "message": "Admin token rotated successfully",
  "new_token": "new-token-here"
}
```

#### `POST /admin/reset_password`
Reset admin password.

**Request Body:**
```json
{
  "new_username": "admin",
  "new_password": "newpassword"
}
```

**Response:**
```json
{
  "message": "Admin password reset successfully"
}
```

## 🔐 Security

- **Password Hashing**: Uses Werkzeug's `generate_password_hash` with bcrypt
- **Token Authentication**: UUID-based tokens stored securely
- **Dual Auth**: Supports both Basic Auth and token-based authentication
- **Credential Persistence**: Hashed credentials stored in `persist/admin_credentials.json`

## 🎯 Usage Examples

### Search Queries
```
"gaming laptops"
"laptops under 50000"
"phones between 10000 and 20000"
"headphones with noise cancellation"
"budget laptops"
```

### Chat Queries
```
"What are the best laptops for programming?"
"Recommend a phone with good camera"
"Which headphones are good for music?"
"Compare laptops under 30000"
```

## 🧪 Testing

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## 🔧 Development

### Adding New Product Categories

1. Add CSV file to `data/` directory
2. Update `load_data()` in `app/search_engine.py`
3. Rebuild the TF-IDF index via `/admin/rebuild`

### Customizing the UI

Edit files in the `static/` directory:
- `index.html`: Structure and content
- `styles.css`: Styling and theme
- `app.js`: Frontend logic and interactions

## 📦 Dependencies

- **Flask 2.0+**: Web framework
- **pandas 1.3+**: Data manipulation
- **scikit-learn 1.0+**: TF-IDF vectorization
- **joblib 1.0+**: Model persistence
- **pytest 7.0+**: Testing framework
- **gunicorn 20.0+**: Production server

See `requirements.txt` for complete list.

## 🚢 Deployment

### Production with Gunicorn

```powershell
gunicorn -w 4 -b 0.0.0.0:5000 "app.main:app"
```

### Docker (Optional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.main:app"]
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ using Flask and TF-IDF**
