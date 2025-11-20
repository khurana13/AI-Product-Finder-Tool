# Quick Reference Card

## 🚀 Running the Application

### Development Mode
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run the app
python run.py

# Access at: http://localhost:5000
```

### Production Mode
```powershell
# Using Gunicorn (Linux/Mac)
gunicorn -w 4 -b 0.0.0.0:5000 "app.main:app"

# Using Waitress (Windows)
waitress-serve --host=0.0.0.0 --port=5000 app.main:app
```

---

## 📁 Project Structure

```
AI PBL/
├── app/              # Application code
├── config/           # Configuration
├── data/             # CSV datasets
├── docs/             # Documentation
├── persist/          # Runtime data (TF-IDF cache, admin credentials)
├── static/           # Web UI (HTML, CSS, JS)
├── tests/            # Test suite
├── run.py            # Application entrypoint
└── README.md         # Main documentation
```

---

## 🔑 Admin Token Location

```
persist/admin_token.txt
```

Use this token in `X-Admin-Token` header for admin endpoints.

---

## 🌐 API Endpoints

### Public
- `GET /` - Web UI
- `GET /search?q=laptop&page=1&per_page=10` - Search products
- `POST /chat` - Chatbot (JSON: `{"message": "..."}`)

### Admin (require authentication)
- `POST /admin/rebuild` - Rebuild TF-IDF index
- `POST /admin/rotate` - Rotate admin token
- `POST /admin/reset_password` - Reset admin credentials

---

## 🧪 Testing

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_api.py -v
```

---

## 📚 Documentation Files

1. **README.md** - Main project overview
2. **docs/API.md** - Complete API reference
3. **docs/ARCHITECTURE.md** - System design
4. **docs/DEPLOYMENT.md** - Deployment guide
5. **docs/PROJECT_SUMMARY.md** - Reorganization summary

---

## ⚙️ Configuration

### Environment Variables (.env)
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
ADMIN_TOKEN=your-admin-token
HOST=0.0.0.0
PORT=5000
```

Copy `.env.example` to `.env` and customize.

---

## 🔧 Common Commands

### Install Dependencies
```powershell
pip install -r requirements.txt
```

### Update Dependencies
```powershell
pip install --upgrade -r requirements.txt
```

### Freeze Dependencies
```powershell
pip freeze > requirements.txt
```

### Check for Errors
```powershell
python -m pytest tests/
```

### Rebuild Index
```powershell
# Via API
curl -X POST http://localhost:5000/admin/rebuild \
  -H "X-Admin-Token: $(Get-Content persist\admin_token.txt)"
```

---

## 🐛 Troubleshooting

### App won't start
```powershell
# Check virtual environment
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Port already in use
```powershell
# Find process
netstat -ano | findstr :5000

# Kill process
taskkill /PID <PID> /F
```

### Module not found
```powershell
# Ensure you're in project root
cd "C:\Users\0501s\OneDrive\Desktop\AI PBL"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### Index not loading
```powershell
# Check persist directory
dir persist\

# Rebuild index via admin endpoint
# (see "Rebuild Index" above)
```

---

## 📦 File Locations

| Item | Location |
|------|----------|
| **Application entry** | `run.py` |
| **Flask app** | `app/main.py` |
| **Search engine** | `app/search_engine.py` |
| **Configuration** | `config/config.py` |
| **Web UI** | `static/index.html` |
| **CSV data** | `data/*.csv` |
| **TF-IDF cache** | `persist/*.joblib` |
| **Admin token** | `persist/admin_token.txt` |
| **Admin credentials** | `persist/admin_credentials.json` |
| **Tests** | `tests/test_*.py` |
| **Documentation** | `docs/*.md` |

---

## 🔐 Security Notes

- Admin token in `persist/admin_token.txt` - **keep secure**
- Change `SECRET_KEY` before production
- Use HTTPS in production
- Enable `FLASK_ENV=production` for production

---

## 📊 Quick Stats

- **Language**: Python 3.8+
- **Framework**: Flask 2.0+
- **ML Library**: scikit-learn
- **Data**: pandas
- **Server**: Gunicorn (production)
- **Lines of Code**: ~800+ (excluding tests & docs)
- **Documentation**: 1,500+ lines

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: November 2025
