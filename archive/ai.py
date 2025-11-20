"""Flask-based product search + chatbot API using the CSV data.

Endpoints:
- GET / -> simple health/info
- POST /search -> JSON {category, filters, min_price, max_price} returns matching rows
- POST /chat -> JSON {query, top_k} returns retrieval results with scores and row data

This file is the main app entrypoint requested by the user.
"""
from __future__ import annotations
import traceback
from flask import Flask, request, jsonify, send_from_directory
import ai1
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

app = Flask(__name__)

# Load data and build corpus/index at startup
print("Loading CSV data and preparing search index...")
DATA = ai1.load_data() or {}
CORPUS, METADATA = ai1.build_corpus_from_data(DATA)

# Persistence: store vectorizer, tfidf matrix, corpus and metadata to disk for faster restarts
BASE_DIR = os.path.dirname(__file__)
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
        VECTORIZER, TFIDF_MATRIX = ai1.build_tfidf_index(CORPUS)
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
    # Serve the static single-page UI
    try:
        return send_from_directory(os.path.join(BASE_DIR, 'static'), 'index.html')
    except Exception:
        # fallback to JSON when static file missing
        return jsonify({'status': 'ok', 'info': 'Product search + chatbot API', 'data_loaded': bool(DATA)})


@app.route('/search', methods=['POST'])
def api_search():
    try:
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

        results_df = ai1.search_products(category, DATA, filters, min_price, max_price)
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
        query = payload.get('query', '')
        top_k = int(payload.get('top_k', 5))
        if not query:
            return jsonify({'error': 'Missing query'}), 400

        # Use TF-IDF index if available, else fallback to keyword match
        if VECTORIZER is not None and TFIDF_MATRIX is not None:
            hits = ai1.retrieve_with_index(query, VECTORIZER, TFIDF_MATRIX, METADATA, top_k=top_k)
            return jsonify({'query': query, 'hits': hits})
        else:
            # simple keyword fallback: reuse demo logic
            from demo_query import search_with_keywords
            # prepare results in-memory
            # search_with_keywords prints; instead call ai1 functions directly here similarly
            # We'll implement a tiny inline fallback
            tokens = [t.lower() for t in __import__('re').findall(r"\w+", query)]
            scored = []
            for i, text in enumerate(CORPUS):
                t_lower = text.lower()
                score = sum(1 for t in tokens if t in t_lower)
                if score > 0:
                    scored.append((score, i))
            scored.sort(reverse=True)
            results = []
            min_p, max_p = ai1.parse_price_constraints(query)
            for score, i in scored[:top_k]:
                meta = METADATA[i]
                price_val = ai1.extract_price_value(meta['row'])
                if (min_p is not None and price_val is not None and price_val < min_p) or (max_p is not None and price_val is not None and price_val > max_p):
                    continue
                results.append({'score': float(score), 'meta': meta, 'row': meta['row'].to_dict()})
            return jsonify({'query': query, 'hits': results})
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
        DATA = ai1.load_data() or {}
        CORPUS, METADATA = ai1.build_corpus_from_data(DATA)
        VECTORIZER, TFIDF_MATRIX = ai1.build_tfidf_index(CORPUS)
        if VECTORIZER is not None and TFIDF_MATRIX is not None:
            joblib.dump(VECTORIZER, VECTORIZER_PATH)
            joblib.dump(TFIDF_MATRIX, TFIDF_MATRIX_PATH)
            joblib.dump(METADATA, METADATA_PATH)
            joblib.dump(CORPUS, CORPUS_PATH)
        return jsonify({'status': 'ok', 'message': 'index rebuilt', 'data_loaded': bool(DATA)})
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


if __name__ == '__main__':
    # Run development server
    app.run(host='0.0.0.0', port=5000, debug=True)
