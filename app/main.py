"""
Student Project: Simple Product Search & Chatbot (Flask)

Author: Aditya Tripathi
Course: Introduction to Information Retrieval / AI PBL
Date: 2025-11-09

Developed for AI PBL by a team of 5th Sem Students.

This is a student implementation of a small product search + chatbot
service. It uses CSV files as the dataset, a TF-IDF retrieval engine,
and a simple generative fallback. The code contains TODOs and
notes intended for a student-maintained repository.

TODOs:
- [ ] Add unit tests for search functions
- [ ] Add CI configuration (GitHub Actions)
- [ ] Add caching for TF-IDF artifacts in production

Notes:
- Keep modifications limited to comments and docstrings unless fixing bugs.
"""
from __future__ import annotations
import traceback
from flask import Flask, request, jsonify, send_from_directory
from app import search_engine
import atexit
import os
import joblib
import secrets
from functools import wraps
import json
from werkzeug.security import generate_password_hash, check_password_hash


def _check_basic_auth():
    """Return (username,password) if Basic auth provided, else (None,None)."""
    auth = request.authorization
    if auth and auth.username:
        return auth.username, auth.password
    return None, None


def is_admin_authenticated(req=None) -> bool:
    """Check admin authentication.

    Priority:
    1) If ADMIN_USER and ADMIN_PASS are set in env, require Basic auth matching them.
    2) Else require token via X-Admin-Token header, ?token=, or form token matching ADMIN_TOKEN.
    """
    # Basic auth mode: prefer persisted credentials if available
    creds = load_admin_credentials()
    u, p = _check_basic_auth()
    if creds and creds.get('username'):
        if u and p:
            return check_password_hash(creds.get('password_hash', ''), p) and u == creds.get('username')
    # Fallback to env ADMIN_USER/ADMIN_PASS if not using persisted creds
    admin_user = os.environ.get('ADMIN_USER')
    admin_pass = os.environ.get('ADMIN_PASS')
    if admin_user and admin_pass:
        if u and p:
            return bool(u == admin_user and p == admin_pass)

    # token mode (still allowed)
    if req is None:
        req = request
    token = req.headers.get('X-Admin-Token') or req.args.get('token') or req.form.get('token')
    return bool(token and ADMIN_TOKEN and token == ADMIN_TOKEN)

# BASE_DIR is the project root (parent of app/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'))

# Load data and build corpus/index at startup
print("Loading CSV data and preparing search index...")
DATA = search_engine.load_data() or {}
CORPUS, METADATA = search_engine.build_corpus_from_data(DATA)

# Persistence: store vectorizer, tfidf matrix, corpus and metadata to disk for faster restarts
# BASE_DIR is the project root (parent of app/)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PERSIST_DIR = os.path.join(BASE_DIR, 'persist')
os.makedirs(PERSIST_DIR, exist_ok=True)
VECTORIZER_PATH = os.path.join(PERSIST_DIR, 'tfidf_vectorizer.joblib')
TFIDF_MATRIX_PATH = os.path.join(PERSIST_DIR, 'tfidf_matrix.joblib')
METADATA_PATH = os.path.join(PERSIST_DIR, 'metadata.joblib')
CORPUS_PATH = os.path.join(PERSIST_DIR, 'corpus.joblib')

CREDENTIALS_PATH = os.path.join(PERSIST_DIR, 'admin_credentials.json')

VECTORIZER = None
TFIDF_MATRIX = None

try:
    # Try to load persisted artifacts
    if os.path.exists(VECTORIZER_PATH) and os.path.exists(TFIDF_MATRIX_PATH) and os.path.exists(METADATA_PATH) and os.path.exists(CORPUS_PATH):
        print('Loading persisted TF-IDF index and metadata...')
        VECTORIZER = joblib.load(VECTORIZER_PATH)
        TFIDF_MATRIX = joblib.load(TFIDF_MATRIX_PATH)
        METADATA = joblib.load(METADATA_PATH)
        CORPUS = joblib.load(CORPUS_PATH)
        print('Loaded persisted index.')
    else:
        # Build and persist
        print('Building TF-IDF index (this may take a moment) ...')
        VECTORIZER, TFIDF_MATRIX = search_engine.build_tfidf_index(CORPUS)
        if VECTORIZER is not None and TFIDF_MATRIX is not None:
            try:
                joblib.dump(VECTORIZER, VECTORIZER_PATH)
                joblib.dump(TFIDF_MATRIX, TFIDF_MATRIX_PATH)
                joblib.dump(METADATA, METADATA_PATH)
                joblib.dump(CORPUS, CORPUS_PATH)
                print('Persisted TF-IDF index and metadata to', PERSIST_DIR)
            except Exception as e:
                print('Warning: failed to persist index:', e)
except Exception as e:
    print('Warning while preparing persisted index:', e)
    # fall back to in-memory only

# Admin token: read from env ADMIN_TOKEN if provided; otherwise persist one to persist/admin_token.txt
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')
if not ADMIN_TOKEN:
    token_file = os.path.join(PERSIST_DIR, 'admin_token.txt')
    try:
        if os.path.exists(token_file):
            with open(token_file, 'r', encoding='utf-8') as f:
                ADMIN_TOKEN = f.read().strip()
        else:
            ADMIN_TOKEN = secrets.token_urlsafe(24)
            with open(token_file, 'w', encoding='utf-8') as f:
                f.write(ADMIN_TOKEN)
            print('Admin token generated and saved to', token_file)
            print('Set environment variable ADMIN_TOKEN to avoid generation on startup.')
    except Exception as e:
        print('Warning: unable to create/read admin token file:', e)


def load_admin_credentials():
    """Load admin credentials from persisted file if present.

    Returns dict {'username':..., 'password_hash':...} or None.
    """
    try:
        if os.path.exists(CREDENTIALS_PATH):
            with open(CREDENTIALS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print('Warning loading admin credentials:', e)
    return None


def save_admin_credentials(username: str, password_plain: str):
    """Hash the password and persist username + password_hash."""
    try:
        data = {'username': username, 'password_hash': generate_password_hash(password_plain)}
        with open(CREDENTIALS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print('Error saving admin credentials:', e)
        return False


@app.route('/', methods=['GET'])
def index():
    # Serve the static home page
    try:
        return send_from_directory(os.path.join(BASE_DIR, 'static'), 'home.html')
    except Exception:
        # fallback to JSON when static file missing
        return jsonify({'status': 'ok', 'info': 'Product search + chatbot API', 'data_loaded': bool(DATA)})


@app.route('/about', methods=['GET'])
def about():
    # Serve the static about page
    try:
        return send_from_directory(os.path.join(BASE_DIR, 'static'), 'about.html')
    except Exception:
        # fallback to JSON when static file missing
        return jsonify({'error': 'About page not found'}), 404


@app.route('/search', methods=['GET', 'POST'])
def api_search():
    try:
        # Support both GET (query params) and POST (JSON body)
        if request.method == 'GET':
            query = request.args.get('q', '')
            category = request.args.get('category', '')
            min_price = float(request.args.get('min_price', 0)) if request.args.get('min_price') else 0
            max_price = float(request.args.get('max_price', float('inf'))) if request.args.get('max_price') else float('inf')
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('per_page', 10))
            fields = request.args.get('fields', '')
            if fields:
                fields = [f.strip() for f in fields.split(',') if f.strip()]
            else:
                fields = None
            
            # Use TF-IDF retrieval for natural language search
            if query and VECTORIZER is not None and TFIDF_MATRIX is not None:
                # Pass category filter to improve accuracy
                category_filter = category if category else None
                # Use a larger top_k to ensure we have enough results for pagination
                hits = search_engine.retrieve_with_index(
                    query, VECTORIZER, TFIDF_MATRIX, METADATA, 
                    top_k=min(1000, len(METADATA)), 
                    category_filter=category_filter
                )
                
                # Filter by price range if specified
                filtered_results = []
                for hit in hits:
                    data = hit['data']
                    # Extract price from various field names
                    price_value = data.get('Price') or data.get('Selling Price') or data.get('Selling_Price') or data.get('price')
                    if price_value and price_value != 'N/A':
                        try:
                            # Clean and parse price
                            price_num = float(str(price_value).replace(',', '').replace('₹', '').strip())
                            if min_price <= price_num <= max_price:
                                filtered_results.append(data)
                        except (ValueError, TypeError):
                            # If price parsing fails, include the item if no price filter is set
                            if min_price == 0 and max_price == float('inf'):
                                filtered_results.append(data)
                    else:
                        # Include items without price if no price filter is set
                        if min_price == 0 and max_price == float('inf'):
                            filtered_results.append(data)
                
                all_results = filtered_results
                total = len(all_results)
                
                # Apply pagination
                start = (page - 1) * page_size
                end = start + page_size
                page_results = all_results[start:end]
                
                # Apply field filtering if requested
                if fields:
                    page_results = [{k: r.get(k, '') for k in fields if k in r} for r in page_results]
                
                total_pages = (total + page_size - 1) // page_size
                return jsonify({
                    'query': query,
                    'results': page_results,
                    'total': total,
                    'page': page,
                    'per_page': page_size,
                    'total_pages': total_pages
                })
            else:
                return jsonify({'error': 'Missing query parameter'}), 400
        
        # POST method (original functionality)
        payload = request.get_json(force=True)
        category = payload.get('category')
        filters = payload.get('filters', {})
        min_price = payload.get('min_price', 0)
        max_price = payload.get('max_price', float('inf'))
        # pagination & fields
        page = int(payload.get('page', 1))
        page_size = int(payload.get('page_size', 20))
        fields = payload.get('fields')  # optional list of field names or comma-separated string
        if isinstance(fields, str):
            fields = [f.strip() for f in fields.split(',') if f.strip()]

        if not category or category not in DATA:
            return jsonify({'error': 'Invalid or missing category. Must be one of: ' + ','.join(DATA.keys())}), 400

        results_df = search_engine.search_products(category, DATA, filters, min_price, max_price)
        # convert to list of dicts and apply field selection
        all_results = results_df.fillna('').to_dict(orient='records')
        total = len(all_results)
        # pagination
        if page_size <= 0:
            page_size = 20
        if page <= 0:
            page = 1
        start = (page - 1) * page_size
        end = start + page_size
        page_results = all_results[start:end]
        # apply field filtering if requested
        if fields:
            filtered = []
            for r in page_results:
                filtered.append({k: r.get(k, '') for k in fields if k in r})
            page_results = filtered
        return jsonify({'count': total, 'page': page, 'page_size': page_size, 'results': page_results})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/chat', methods=['POST'])
def api_chat():
    try:
        payload = request.get_json(force=True)
        query = payload.get('message') or payload.get('query', '')
        if not query:
            return jsonify({'error': 'Missing message'}), 400

        # The new generate_chat_response handles all the logic internally
        response = search_engine.generate_chat_response(query, VECTORIZER, TFIDF_MATRIX, METADATA)
        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/admin/rebuild', methods=['POST'])
def admin_rebuild():
    """Secure admin endpoint to rebuild the TF-IDF index on demand.

    Provide the admin token either in header `X-Admin-Token` or as query param `?token=`.
    If ADMIN_TOKEN was generated on this host, you can find it in `persist/admin_token.txt`.
    """
    # authenticate (support Basic auth or token depending on configuration)
    if not is_admin_authenticated():
        return jsonify({'error': 'Forbidden: invalid admin credentials'}), 403

    try:
        # reload data from CSVs in case files changed
        global DATA, CORPUS, METADATA, VECTORIZER, TFIDF_MATRIX
        DATA = search_engine.load_data() or {}
        CORPUS, METADATA = search_engine.build_corpus_from_data(DATA)
        VECTORIZER, TFIDF_MATRIX = search_engine.build_tfidf_index(CORPUS)
        if VECTORIZER is not None and TFIDF_MATRIX is not None:
            joblib.dump(VECTORIZER, VECTORIZER_PATH)
            joblib.dump(TFIDF_MATRIX, TFIDF_MATRIX_PATH)
            joblib.dump(METADATA, METADATA_PATH)
            joblib.dump(CORPUS, CORPUS_PATH)
        return jsonify({'status': 'ok', 'message': 'index rebuilt', 'data_loaded': bool(DATA)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/search_web', methods=['POST'])
def api_search_web():
    """Search the web for product pages matching a query and return fetched metadata.

    Request JSON: { "query": "best noise cancelling headphones", "top_n": 3 }
    Response: { "query": ..., "results": [ {title,image,price,description,url}, ... ] }
    """
    try:
        payload = request.get_json(force=True)
        query = payload.get('query') or payload.get('message')
        top_n = int(payload.get('top_n', 3)) if payload.get('top_n') else 3
        if not query:
            return jsonify({'error': 'Missing query field'}), 400

        web_results = search_engine.search_web_and_fetch(query, top_n=top_n)
        return jsonify({'query': query, 'results': web_results, 'count': len(web_results)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/admin/reset_password', methods=['POST'])
def admin_reset_password():
    """Reset admin username/password (stores hashed password).

    Requires current admin authentication (token or Basic auth). Accepts JSON {username, password}.
    """
    if not is_admin_authenticated():
        return jsonify({'error': 'Forbidden: invalid admin credentials'}), 403

    body = request.get_json(force=True)
    username = body.get('username')
    password = body.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password are required'}), 400

    ok = save_admin_credentials(username, password)
    if ok:
        return jsonify({'status': 'ok', 'message': 'credentials updated'})
    else:
        return jsonify({'error': 'failed to save credentials'}), 500


@app.route('/admin/rotate', methods=['POST'])
def admin_rotate():
    """Rotate the admin token. Requires current admin creds. Returns the new token.

    If ADMIN_USER/ADMIN_PASS are used (basic auth), rotation still generates a token
    but the app will continue to accept Basic auth. The token is an alternative
    mechanism for auth when Basic auth not set.
    """
    if not is_admin_authenticated():
        return jsonify({'error': 'Forbidden: invalid admin credentials'}), 403

    try:
        global ADMIN_TOKEN
        ADMIN_TOKEN = secrets.token_urlsafe(24)
        token_file = os.path.join(PERSIST_DIR, 'admin_token.txt')
        with open(token_file, 'w', encoding='utf-8') as f:
            f.write(ADMIN_TOKEN)
        # Also save any provided new username/password (optional)
        body = request.get_json(silent=True) or {}
        new_user = body.get('username')
        new_pass = body.get('password')
        if new_user and new_pass:
            saved = save_admin_credentials(new_user, new_pass)
            note = f'saved to {token_file}; credentials saved: {saved}'
        else:
            note = f'saved to {token_file}'
        return jsonify({'status': 'ok', 'token': ADMIN_TOKEN, 'note': note})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/fetch_product', methods=['POST'])
def api_fetch_product():
    """Fetch product metadata (title, image, price) from a public product URL.

    This is a best-effort endpoint that extracts OpenGraph/meta tags. It should
    be used with care and only for URLs you have permission to access.
    """
    try:
        payload = request.get_json(force=True)
        url = payload.get('url')
        if not url:
            return jsonify({'error': 'Missing url field'}), 400

        data = search_engine.fetch_product_from_url(url)
        return jsonify(data)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Run development server
    app.run(host='0.0.0.0', port=5000, debug=True)
