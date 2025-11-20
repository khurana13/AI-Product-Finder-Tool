"""
search_engine.py

Student Project file — simple TF-IDF search engine and a thin wrapper
around a generative API. This file includes a few student-style TODOs
and comments to make it obvious this is a learning project.

Author: Student Name
TODO: annotate functions and add unit tests for parse_price_constraints
"""

import os
import re
import json
import time
import traceback
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
import pandas as pd
from dotenv import load_dotenv

# Optional import: Google Generative AI (Gemini) client. Not all environments
# will have this package available. Fall back gracefully if missing so the
# rest of the search engine (TF-IDF retrieval) continues to work.
try:
    import google.generativeai as genai
except Exception:
    genai = None
    print("⚠️ google.generativeai package not installed — generative features disabled.")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from duckduckgo_search import DDGS

# --- Environment and API Configuration ---

# Load environment variables from .env file
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path, override=True)
print(f"Attempting to load .env file from: {dotenv_path}")
print(f"GEMINI_API_KEY found: {'YES' if os.getenv('GEMINI_API_KEY') else 'NO'}")

# Configure the Gemini API (only if the package is available)
gemini_api_key = os.getenv("GEMINI_API_KEY")
if genai is None:
    print("⚠️ Skipping Gemini API configuration because the client library is not installed.")
else:
    try:
        if not gemini_api_key or gemini_api_key == "YOUR_API_KEY":
            print("⚠️ Warning: GEMINI_API_KEY not found or is a placeholder. Generative AI features will be disabled.")
            # Configure with a dummy key to avoid crashing on later calls
            genai.configure(api_key="DUMMY_KEY_BECAUSE_WE_HAVE_TO")
        else:
            genai.configure(api_key=gemini_api_key)
    except Exception as e:
        print(f"⚠️ Error configuring Gemini API: {e}")

# Choose a working Gemini model dynamically to avoid hardcoding names that may not be
# available for the account or API version. This will try to pick the first model
# that supports generateContent, otherwise fall back to the first model name.
GEMINI_MODEL: Optional[str] = None
def _select_gemini_model_once() -> Optional[str]:
    global GEMINI_MODEL
    if GEMINI_MODEL:
        return GEMINI_MODEL
    if genai is None:
        print("⚠️ Gemini client not available; cannot list models.")
        return None

    try:
        models = genai.list_models()
        # Prefer models that explicitly support generateContent
        for m in models:
            # model objects may expose supported_generation_methods or similar
            try:
                methods = getattr(m, 'supported_generation_methods', None)
            except Exception:
                methods = None
            if methods and 'generateContent' in methods:
                GEMINI_MODEL = getattr(m, 'name', None)
                break

        # If nothing picked, pick first available model name
        if not GEMINI_MODEL and models:
            GEMINI_MODEL = getattr(models[0], 'name', None)

        print(f"Selected Gemini model: {GEMINI_MODEL}")
        return GEMINI_MODEL
    except Exception as e:
        print(f"⚠️ Could not list Gemini models: {e}")
        return None

# Pre-select model at import/startup (best-effort)
_select_gemini_model_once()

# --- Data Loading and Preprocessing ---

def load_data() -> Optional[Dict[str, pd.DataFrame]]:
    """
    Loads all CSV files from the 'data' directory, normalizes column names,
    and returns a dictionary of DataFrames.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    df_dict = {}
    try:
        for filename in os.listdir(data_dir):
            if filename.endswith('.csv'):
                category = os.path.splitext(filename)[0]
                filepath = os.path.join(data_dir, filename)
                df = pd.read_csv(filepath)
                # Normalize column names for consistency (lowercase, strip spaces, use underscores)
                df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
                df_dict[category] = df
        
        if not df_dict:
            # Student note: make sure CSVs are placed in the `data/` directory.
            print("⚠️ No CSV files found in the 'data' directory.")
            return None
            
        return df_dict
    except FileNotFoundError:
        print(f"❌ CRITICAL: Data directory not found at {data_dir}.")
        return None
    except Exception as e:
        print(f"❌ CRITICAL: Failed to load data. Error: {e}")
        return None

def build_corpus_from_data(data: Dict[str, pd.DataFrame]) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Builds a weighted corpus and metadata list from all rows in all dataframes
    for TF-IDF indexing. Important fields are repeated to give them more weight.
    """
    corpus: List[str] = []
    metadata: List[Dict[str, Any]] = []

    important_fields = {
        'name', 'model', 'brand', 'title', 'processor', 'ram', 'storage', 
        'memory', 'display', 'camera', 'battery', 'os'
    }
    
    for category, df in data.items():
        for idx, row in df.iterrows():
            parts = []
            # Add category multiple times for better category matching
            parts.extend([str(category)] * 3)
            
            for col, val in row.items():
                if pd.isna(val):
                    continue
                
                val_str = str(val).strip()
                if not val_str:
                    continue
                
                # Add column name as context
                parts.append(str(col))
                
                # Repeat important fields for higher weight
                weight = 3 if any(imp in str(col) for imp in important_fields) else 1
                parts.extend([val_str] * weight)
            
            text = ' '.join(parts)
            corpus.append(text)
            metadata.append({'category': category, 'index': idx, 'row': row})

    return corpus, metadata

def build_tfidf_index(corpus: List[str]) -> Optional[Tuple[TfidfVectorizer, Any]]:
    """
    Builds and returns a TF-IDF vectorizer and matrix for the given corpus.
    """
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=15000,
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.9,
            sublinear_tf=True,
            lowercase=True,
            strip_accents='unicode'
        )
        tfidf_matrix = vectorizer.fit_transform(corpus)
        # Student note: the default parameters are chosen for small datasets used in class.
        print(f"✅ TF-IDF index built successfully: {tfidf_matrix.shape[0]} documents, {tfidf_matrix.shape[1]} features.")
        return vectorizer, tfidf_matrix
    except Exception as e:
        print(f"❌ CRITICAL: Failed to build TF-IDF index. Error: {e}")
        traceback.print_exc()
        return None, None

# --- Utility Functions ---

def row_to_json_safe_dict(row: pd.Series) -> Dict[str, Any]:
    """Converts a pandas Series to a JSON-safe dictionary."""
    result = {}
    for key, value in row.items():
        if pd.isna(value):
            result[str(key)] = None
        elif hasattr(value, 'item'): # Handles numpy numeric types
            result[str(key)] = value.item()
        elif value == float('inf') or value == float('-inf'):
            result[str(key)] = None
        else:
            result[str(key)] = value
    return result

def extract_price_value(row: pd.Series) -> Optional[float]:
    """Extracts a numeric price value from a DataFrame row."""
    # Look for columns that contain 'price'
    for col in row.index:
        if 'price' in str(col).lower():
            val = row.get(col)
            if pd.isna(val):
                continue
            
            # Clean the value by removing currency symbols, commas, etc.
            s = re.sub(r'[^\d\.]', '', str(val))
            if s:
                try:
                    return float(s)
                except ValueError:
                    continue
    return None

def parse_price_constraints(query: str) -> Tuple[Optional[float], Optional[float]]:
    """Parses price constraints like 'under 2000' from a user query."""
    q = query.lower()
    
    m = re.search(r"between\s+([\d,]+)\s*(?:and|-)\s*([\d,]+)", q)
    if m:
        low = float(m.group(1).replace(',', ''))
        high = float(m.group(2).replace(',', ''))
        return min(low, high), max(low, high)

    m = re.search(r"([\d,]+)\s*-\s*([\d,]+)", q)
    if m:
        low = float(m.group(1).replace(',', ''))
        high = float(m.group(2).replace(',', ''))
        return min(low, high), max(low, high)

    m = re.search(r"(?:under|below|less than|max|maximum)\s*₹?\s*([\d,]+)", q)
    if m:
        return None, float(m.group(1).replace(',', ''))

    m = re.search(r"(?:over|above|more than|min|minimum)\s*₹?\s*([\d,]+)", q)
    if m:
        return float(m.group(1).replace(',', '')), None

    return None, None

# --- Core AI and Search Logic ---

def _formalize_text(text: str) -> str:
    """
    Apply lightweight normalization to make responses more formal/professional.
    This avoids casual phrasing, contractions, and emoji characters in replies.
    """
    if not text:
        return text

    # Remove emoji and other pictographs
    try:
        # Basic regex to strip common emoji ranges
        text = re.sub(r"[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]", '', text)
    except re.error:
        # If the regex engine doesn't support these ranges on this Python, fall back to removing a few characters
        text = text.replace('😊', '').replace('💡', '').replace('🤖', '')

    # Replace common contractions with formal equivalents
    contractions = {
        "I'm": "I am",
        "can't": "cannot",
        "won't": "will not",
        "don't": "do not",
        "doesn't": "does not",
        "didn't": "did not",
        "it's": "it is",
        "you're": "you are",
        "I've": "I have",
        "that's": "that is",
        "there's": "there is",
    }
    for k, v in contractions.items():
        text = re.sub(r"\b" + re.escape(k) + r"\b", v, text, flags=re.IGNORECASE)

    # Replace casual phrases
    text = re.sub(r"(?i)try asking", 'for example, you could ask', text)
    text = re.sub(r"(?i)go ahead", 'please', text)
    text = re.sub(r"\s+\n", '\n', text)

    # Trim whitespace
    return text.strip()


def get_gemini_response(query: str, tone: str = 'casual', retries: int = 2, delay: int = 5) -> str:
    """
    Gets a response from the Gemini API, with retry logic.
    tone: 'casual' or 'formal' — when 'formal' the output will be post-processed.
    """
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "DUMMY_KEY_BECAUSE_WE_HAVE_TO":
        return "I am unable to use the generative AI service at this time. I can only provide information based on the available product data."

    for attempt in range(retries):
        try:
            # Use a previously selected model name if available; otherwise attempt to select one now.
            model_name = GEMINI_MODEL or _select_gemini_model_once()
            if not model_name:
                raise RuntimeError('No Gemini model available')
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(query)
            if response and response.text:
                # Return raw/casual text or formalized text depending on tone
                text = response.text
                if tone and tone.lower().startswith('form'):
                    return _formalize_text(text)
                return text
            else:
                print(f"⚠️ Gemini API returned an empty response for query: '{query}'")
                return "I could not generate a response for that request. Please try phrasing your question differently."
        except Exception as e:
            print(f"An error occurred while calling Gemini API (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return "I'm sorry, I'm having trouble connecting to the generative AI service right now."


def fetch_product_from_url(url: str, timeout: int = 8) -> dict:
    """
    Fetch basic product information from a product page URL using OpenGraph/meta tags.
    This is a lightweight best-effort extractor. For accurate/long-term scraping,
    use a dedicated scraper and respect the target site's robots and terms.
    Returns dict with keys: title, image, price, description, raw_html (optionally).
    """
    import requests
    from bs4 import BeautifulSoup

    result = {'title': None, 'image': None, 'price': None, 'description': None, 'url': url}
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; StudentBot/1.0)'}
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, 'lxml')

        # Try OpenGraph tags first
        og_title = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'og:title'})
        if og_title and og_title.get('content'):
            result['title'] = og_title['content'].strip()

        og_image = soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'og:image'})
        if og_image and og_image.get('content'):
            result['image'] = og_image['content'].strip()

        # Price: common meta tags
        price_meta = soup.find('meta', property='product:price:amount') or soup.find('meta', attrs={'itemprop': 'price'})
        if price_meta and price_meta.get('content'):
            result['price'] = price_meta['content'].strip()

        # Description
        desc = soup.find('meta', property='og:description') or soup.find('meta', attrs={'name': 'description'})
        if desc and desc.get('content'):
            result['description'] = desc['content'].strip()

        # Fallbacks: title tag, first image
        if not result['title']:
            t = soup.find('title')
            if t:
                result['title'] = t.text.strip()

        if not result['image']:
            first_img = soup.find('img')
            if first_img and first_img.get('src'):
                src = first_img['src'].strip()
                # Make absolute URL if needed
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    from urllib.parse import urljoin
                    src = urljoin(url, src)
                result['image'] = src

        return result
    except Exception as e:
        print('Warning: failed to fetch product from url:', e)
        return {'error': str(e), 'url': url}


def search_web_for_products(query: str, max_results: int = 8) -> List[str]:
    """
    Use DuckDuckGo to search the web for product pages related to `query`.
    Returns a list of result URLs (best-effort). This does not require an API key.
    """
    try:
        # Add a hint to prefer product pages
        q = f"{query} product"
        urls: List[str] = []
        with DDGS() as ddgs:
            results = ddgs.text(q, max_results=max_results)
            if results:
                for r in results:
                    # result keys use 'href' for links
                    href = r.get('href') or r.get('url') or r.get('link')
                    if href:
                        urls.append(href)
        return urls
    except Exception as e:
        print('Warning: web search failed:', e)
        return []


def search_web_and_fetch(query: str, top_n: int = 3) -> List[Dict[str, Any]]:
    """
    High-level pipeline: perform a web search for the query, then fetch
    OpenGraph/meta data for the top result pages. Returns a list of
    product-like dicts with keys title/image/price/description/url.
    """
    urls = search_web_for_products(query, max_results=top_n * 4)
    results: List[Dict[str, Any]] = []
    for u in urls[: top_n * 3]:
        info = fetch_product_from_url(u)
        # Keep only useful results that have a title or image
        if not info:
            continue
        if info.get('title') or info.get('image'):
            results.append(info)
        if len(results) >= top_n:
            break
    return results

def retrieve_with_index(
    query: str, 
    vectorizer: TfidfVectorizer, 
    tfidf_matrix: Any, 
    metadata: List[Dict[str, Any]], 
    top_k: int = 5, 
    category_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves top_k results for a query using the TF-IDF index, with category and price filtering.
    """
    if vectorizer is None or tfidf_matrix is None:
        return []

    query_lower = query.lower()
    
    # --- Smart Category Detection ---
    if not category_filter:
        if any(word in query_lower for word in ['headphone', 'headset', 'earbud']):
            category_filter = 'headphone'
        elif any(word in query_lower for word in ['mobile', 'smartphone', 'phone']):
            category_filter = 'mobile'
        elif any(word in query_lower for word in ['laptop', 'notebook', 'pc']):
            category_filter = 'laptop'
    
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, tfidf_matrix).flatten()
    
    # Get more candidates to allow for filtering
    candidate_indices = sims.argsort()[::-1][:min(200, len(sims))]

    min_p, max_p = parse_price_constraints(query)
    
    results = []
    for idx in candidate_indices:
        score = float(sims[idx])
        if score < 0.05:  # Confidence threshold
            continue
            
        meta = metadata[idx]
        
        if category_filter and meta['category'] != category_filter:
            continue
        
        price_val = extract_price_value(meta['row'])
        if (min_p and price_val and price_val < min_p) or \
           (max_p and price_val and price_val > max_p):
            continue
        
        row_dict = row_to_json_safe_dict(meta['row'])
        results.append({
            'score': score,
            'data': row_dict,
            'meta': {'category': meta['category'], 'index': int(meta['index'])},
            'row': row_dict # for backward compatibility
        })
        if len(results) >= top_k:
            break

    return results

def generate_chat_response(
    query: str, 
    vectorizer: TfidfVectorizer, 
    tfidf_matrix: np.ndarray, 
    metadata: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generates a response for the chatbot, routing between product search and generative AI.
    """
    query_lower = query.lower().strip()
    
    # --- Simple Conversational Keywords ---
    greetings = ['hello', 'hi', 'hey']
    farewells = ['bye', 'goodbye', 'see you']
    thanks = ['thank', 'thanks', 'appreciate']
    help_words = ['help', 'guide', 'what can you do']
    identity_words = ['who are you', 'what are you']

    # Friendly but professional canned replies
    if any(word in query_lower for word in greetings) and len(query_lower.split()) < 3:
        return {"type": "general", "response": "Hello. How may I assist you with product search or questions today?"}
    if any(word in query_lower for word in farewells):
        return {"type": "general", "response": "Goodbye. If you need further assistance, please ask anytime."}
    if any(word in query_lower for word in thanks):
        return {"type": "general", "response": "You're welcome. Would you like help with anything else?"}
    if any(word in query_lower for word in help_words):
        return {"type": "general", "response": "I can help you find products, filter by price, or compare items. For example: 'Show me Dell laptops with 16GB RAM under 80000'."}
    if any(word in query_lower for word in identity_words):
        return {"type": "general", "response": "I am a product search assistant that helps locate and compare electronics from the available dataset."}

    # --- Product Keyword Routing ---
    product_keywords = [
        'phone', 'mobile', 'laptop', 'computer', 'headphone', 'earphone', 'gaming', 
        'show', 'find', 'search', 'looking for', 'compare', 'vs', 'or',
        'under', 'budget', 'price', 'cost', 'how much', 'cheap', 'expensive'
    ]
    is_product_query = any(keyword in query_lower for keyword in product_keywords)

    if is_product_query:
        print("INFO: Routing to product search.")
        results = retrieve_with_index(query, vectorizer, tfidf_matrix, metadata, top_k=3)

        if not results:
            # No products found in the dataset — provide a polite fallback to the generative model
            print("INFO: No product results, falling back to Gemini.")
            gemini_response = get_gemini_response(
                f"I could not find matching products in the store for the following query: '{query}'. Please provide general guidance based on product knowledge: {query}"
            )
            return {"type": "general", "response": gemini_response}

        # Return a short professional text reply together with structured product hits
        return {
            "type": "product",
            "response": "Here are the most relevant products matching your query:",
            "results": results
        }
    else:
        print("INFO: Routing to Gemini for general conversation.")
        gemini_response = get_gemini_response(query)
        return {"type": "general", "response": gemini_response}

def get_recommendations(
    product_title: str, 
    vectorizer: TfidfVectorizer, 
    tfidf_matrix: np.ndarray, 
    metadata: List[Dict[str, Any]], 
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Gets product recommendations based on a given product title.
    """
    title_vec = vectorizer.transform([product_title])
    sims = cosine_similarity(title_vec, tfidf_matrix).flatten()
    
    # Exclude the item itself by setting its similarity to 0
    original_idx = -1
    for i, meta in enumerate(metadata):
        row = meta['row']
        # Try to find a name/title/model column to match against
        name = ""
        for col in ['name', 'model', 'title']:
            if col in row:
                name = str(row[col])
                break
        
        if name and name.lower() in product_title.lower():
            original_idx = i
            break # Assume first match is the one
            
    if original_idx != -1:
        sims[original_idx] = 0

    top_indices = sims.argsort()[::-1][:top_n + 1] # Get a few extra in case of self-match

    results = []
    for idx in top_indices:
        # Skip if it's the original item
        if idx == original_idx:
            continue

        score = float(sims[idx])
        if score <= 0.1:
            continue
        
        meta = metadata[idx]
        row_dict = row_to_json_safe_dict(meta['row'])
        results.append({
            'score': score,
            'data': row_dict,
            'meta': {'category': meta['category'], 'index': int(meta['index'])},
            'row': row_dict
        })
        if len(results) >= top_n:
            break

    return results

