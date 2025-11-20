import pandas as pd
import re
from typing import List, Dict, Any

def load_data():
    """Load all CSV files"""
    try:
        laptops = pd.read_csv('laptop.csv')
        mobiles = pd.read_csv('mobile.csv')
        headphones = pd.read_csv('headphone.csv')

        # Normalize column names for consistency
        for df in [laptops, mobiles, headphones]:
            df.columns = df.columns.str.strip().str.lower()

        return {'laptop': laptops, 'mobile': mobiles, 'headphone': headphones}
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure laptop.csv, mobile.csv, and headphone.csv are in the same folder as this script.")
        return None


def get_category():
    """Ask user to select a category"""
    print("\n" + "=" * 50)
    print("PRODUCT SEARCH TOOL")
    print("=" * 50)
    print("\nSelect a product category:")
    print("1. Laptop")
    print("2. Mobile")
    print("3. Headphone")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    categories = {'1': 'laptop', '2': 'mobile', '3': 'headphone'}
    return categories.get(choice)


def get_price_range():
    """Get price range from user"""
    print("\nEnter price range:")
    try:
        min_price = float(input("Minimum price (₹): ").strip() or 0)
        max_price = float(input("Maximum price (₹): ").strip() or float('inf'))
        return min_price, max_price
    except ValueError:
        print("Invalid input. Using default range (0 to unlimited)")
        return 0, float('inf')


def get_filters(category, data):
    """Get filter options from user based on category"""
    filters = {}
    df = data[category]
    
    print(f"\nColumns in {category} dataset: {df.columns.tolist()}")

    if category == 'laptop':
        brands = sorted(df['brand'].dropna().unique()) if 'brand' in df.columns else []
        if brands:
            print(f"\nAvailable brands: {', '.join(map(str, brands))}")
            brand = input("Enter brand (or press Enter for all): ").strip()
            if brand:
                filters['brand'] = brand

        rams = sorted(df['ram'].dropna().unique()) if 'ram' in df.columns else []
        if rams:
            print(f"\nAvailable RAM: {', '.join(map(str, rams))}")
            ram = input("Enter RAM (or press Enter for all): ").strip()
            if ram:
                filters['ram'] = ram

        processors = sorted(df['processor_name'].dropna().unique()) if 'processor_name' in df.columns else []
        if processors:
            print(f"\nAvailable processors: {', '.join(map(str, processors))}")
            processor = input("Enter processor (or press Enter for all): ").strip()
            if processor:
                filters['processor_name'] = processor

    elif category == 'mobile':
        brands = sorted(df['brand'].dropna().unique()) if 'brand' in df.columns else []
        if brands:
            print(f"\nAvailable brands: {', '.join(map(str, brands))}")
            brand = input("Enter brand (or press Enter for all): ").strip()
            if brand:
                filters['brand'] = brand

        memories = sorted(df['memory'].dropna().unique()) if 'memory' in df.columns else []
        if memories:
            print(f"\nAvailable Memory: {', '.join(map(str, memories))}")
            memory = input("Enter memory (or press Enter for all): ").strip()
            if memory:
                filters['memory'] = memory

        storages = sorted(df['storage'].dropna().unique()) if 'storage' in df.columns else []
        if storages:
            print(f"\nAvailable Storage: {', '.join(map(str, storages))}")
            storage = input("Enter storage (or press Enter for all): ").strip()
            if storage:
                filters['storage'] = storage

    elif category == 'headphone':
        brands = sorted(df['brand'].dropna().unique()) if 'brand' in df.columns else []
        if brands:
            print(f"\nAvailable brands: {', '.join(map(str, brands))}")
            brand = input("Enter brand (or press Enter for all): ").strip()
            if brand:
                filters['brand'] = brand

        types = sorted(df['form_factor'].dropna().unique()) if 'form_factor' in df.columns else []
        if types:
            print(f"\nAvailable types: {', '.join(map(str, types))}")
            headphone_type = input("Enter type (or press Enter for all): ").strip()
            if headphone_type:
                filters['form_factor'] = headphone_type

    return filters


def search_products(category, data, filters, min_price, max_price):
    """Search products based on filters"""
    df = data[category].copy()

    # Identify price column dynamically
    if category == 'laptop':
        price_col = 'price'
    elif category == 'mobile':
        price_col = 'selling price'
    else:  # headphone
        price_col = 'selling_price'

    if price_col not in df.columns:
        print(f"⚠️ Warning: price column '{price_col}' not found.")
        return pd.DataFrame()

    # Apply filters
    for key, value in filters.items():
        if key in df.columns:
            df = df[df[key].astype(str).str.lower() == value.lower()]

    # Apply price filter
    df = df[(df[price_col] >= min_price) & (df[price_col] <= max_price)]

    # Sort by price
    df = df.sort_values(price_col)
    return df


def display_results(results, category):
    """Display search results"""
    print("\n" + "=" * 50)
    print(f"SEARCH RESULTS: {len(results)} products found")
    print("=" * 50)

    if len(results) == 0:
        print("\nNo products found matching your criteria.")
        return

    for _, row in results.iterrows():
        print(f"\n{'-' * 50}")
        if category == 'laptop':
            print(f"Product: {row.get('name', 'Unknown')} | Price: ₹{row['price']:,.2f}")
            print(f"Brand: {row.get('brand', '')} | RAM: {row.get('ram', '')} | Processor: {row.get('processor_name', '')}")
        elif category == 'mobile':
            print(f"Product: {row.get('model', 'Unknown')} | Price: ₹{row['selling price']:,.2f}")
            print(f"Brand: {row.get('brand', '')} | Memory: {row.get('memory', '')} | Storage: {row.get('storage', '')}")
        elif category == 'headphone':
            print(f"Product: {row.get('model', 'Unknown')} | Price: ₹{row['selling_price']:,.2f}")
            print(f"Brand: {row.get('brand', '')} | Type: {row.get('form_factor', '')}")


def main():
    """Main function"""
    data = load_data()
    if data is None:
        return
    # Offer modes: product search (existing) or chatbot (new)
    while True:
        print("\nChoose mode:")
        print("1. Product search (original)")
        print("2. Chatbot (ask natural language queries about products)")
        print("3. Exit")
        mode = input("Enter choice (1/2/3): ").strip()
        if mode == '1':
            while True:
                category = get_category()
                if not category:
                    print("Invalid choice. Please try again.")
                    continue

                filters = get_filters(category, data)
                min_price, max_price = get_price_range()
                results = search_products(category, data, filters, min_price, max_price)
                display_results(results, category)

                again = input("\nDo you want to search again? (yes/no): ").strip().lower()
                if again not in ['yes', 'y']:
                    print("\nReturning to main menu.")
                    break

        elif mode == '2':
            run_chatbot(data)

        elif mode == '3':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Enter 1, 2, or 3.")


if __name__ == "__main__":
    main()


def build_corpus_from_data(data: Dict[str, pd.DataFrame]):
    """Build a corpus (list of texts) from all rows in all dataframes.

    Returns a tuple (corpus_texts, metadata_list) where metadata_list contains dicts with keys:
    - category, index, row (Series)
    """
    corpus: List[str] = []
    metadata: List[Dict[str, Any]] = []

    for category, df in data.items():
        # use a copy to avoid modifying original
        for idx, row in df.reset_index(drop=True).iterrows():
            # join all non-null fields into a single text blob
            parts = [str(category)]
            for col in df.columns:
                val = row.get(col, '')
                if pd.isna(val):
                    continue
                parts.append(str(col))
                parts.append(str(val))
            text = ' '.join(parts)
            corpus.append(text)
            metadata.append({'category': category, 'index': idx, 'row': row})

    return corpus, metadata


def find_price_in_row(row: pd.Series) -> str:
    """Try to find a price-like column in a row and return formatted price string, else empty."""
    for col in row.index:
        if 'price' in str(col).lower():
            val = row.get(col)
            try:
                return f"₹{float(val):,.2f}"
            except Exception:
                return str(val)
    return ''


def extract_price_value(row: pd.Series) -> float | None:
    """Extract a numeric price value from a DataFrame row if possible.

    Returns a float price (in the same units as present in the CSV) or None.
    """
    for col in row.index:
        col_lower = str(col).lower()
        if 'price' in col_lower or 'selling' in col_lower or 'mrp' in col_lower:
            val = row.get(col)
            if pd.isna(val):
                continue
            s = str(val)
            # find first number-like substring
            m = re.search(r"(\d[\d,\.]+)", s)
            if m:
                num = m.group(1).replace(',', '')
                try:
                    return float(num)
                except Exception:
                    continue
    return None


def parse_price_constraints(query: str) -> tuple[float | None, float | None]:
    """Parse price constraints from a user query.

    Recognizes patterns like:
    - 'under 2000', 'below 2,000' -> (None, 2000)
    - 'over 5000', 'above 5,000' -> (5000, None)
    - 'between 1000 and 3000' or '1000-3000' -> (1000, 3000)
    Returns (min_price, max_price) where either can be None.
    """
    q = query.lower()
    # between X and Y
    m = re.search(r"between\s+([\d,\.]+)\s*(?:and|-)\s*([\d,\.]+)", q)
    if m:
        a = float(m.group(1).replace(',', ''))
        b = float(m.group(2).replace(',', ''))
        return (min(a, b), max(a, b))

    # range like 1000-3000
    m = re.search(r"([\d,\.]+)\s*[-to]+\s*([\d,\.]+)", q)
    if m:
        a = float(m.group(1).replace(',', ''))
        b = float(m.group(2).replace(',', ''))
        return (min(a, b), max(a, b))

    # under / below / less than
    m = re.search(r"(?:under|below|less than)\s*₹?\s*([\d,\.]+)", q)
    if m:
        return (None, float(m.group(1).replace(',', '')))

    # over / above / more than
    m = re.search(r"(?:over|above|more than)\s*₹?\s*([\d,\.]+)", q)
    if m:
        return (float(m.group(1).replace(',', '')), None)

    # plain 'under2000' like
    m = re.search(r"(\d[\d,\.]+)", q)
    # Don't interpret solitary numbers as price constraints by default.
    # Return (None, None) if nothing obvious matched.
    return (None, None)


def summarize_metadata(meta: Dict[str, Any]) -> str:
    """Return a readable single-line summary for a metadata entry."""
    row: pd.Series = meta['row']
    category = meta['category']
    # try common name fields
    name = None
    for candidate in ['name', 'model', 'title']:
        if candidate in row.index:
            name = row.get(candidate)
            if pd.notna(name) and str(name).strip():
                break
    if name is None or pd.isna(name) or str(name).strip() == '':
        # fallback: first non-empty field value
        for val in row.values:
            if pd.notna(val) and str(val).strip():
                name = str(val)
                break

    price = find_price_in_row(row)
    brand = row.get('brand', '') if 'brand' in row.index else ''
    parts = [f"Category: {category}"]
    if brand and pd.notna(brand):
        parts.append(f"Brand: {brand}")
    if name and pd.notna(name):
        parts.append(f"Product: {name}")
    if price:
        parts.append(f"Price: {price}")
    return ' | '.join(parts)


def run_chatbot(data: Dict[str, pd.DataFrame]):
    """Run a simple retrieval-based chatbot over the product CSVs.

    It will try to use scikit-learn's TF-IDF + cosine similarity. If scikit-learn
    isn't available, it falls back to a simple keyword match ranking.
    """
    print("\nBuilding product knowledge base from CSVs...")
    corpus, metadata = build_corpus_from_data(data)

    use_tfidf = True
    vectorizer = None
    tfidf_matrix = None

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        print(f"Built TF-IDF index with {tfidf_matrix.shape[0]} documents.")
    except Exception:
        use_tfidf = False
        print("Note: scikit-learn not available or failed to import. Falling back to keyword matching.")

    print("\nChatbot ready. Ask about products (type 'help' for tips, 'exit' to return).")
    while True:
        query = input("\nYou: ").strip()
        if not query:
            continue
        if query.lower() in ['exit', 'quit', 'q']:
            print("Exiting chatbot and returning to main menu.")
            break
        if query.lower() in ['help', '?']:
            print("Tips: Ask things like 'best headphones under 2000', 'laptops with 16gb ram', or 'price of iPhone 12'.")
            continue

        # retrieve
        top_k = 3
        results = []

        if use_tfidf and vectorizer is not None and tfidf_matrix is not None:
            q_vec = vectorizer.transform([query])
            sims = cosine_similarity(q_vec, tfidf_matrix).flatten()
            top_idxs = sims.argsort()[::-1][:top_k]
            for idx in top_idxs:
                score = float(sims[idx])
                if score <= 0:
                    continue
                results.append((score, metadata[idx]))
        else:
            # keyword fallback: count matched tokens
            tokens = [t.lower() for t in re.findall(r"\w+", query)]
            scored = []
            for i, text in enumerate(corpus):
                t_lower = text.lower()
                score = sum(1 for t in tokens if t in t_lower)
                if score > 0:
                    scored.append((score, i))
            scored.sort(reverse=True)
            for score, i in scored[:top_k]:
                results.append((float(score), metadata[i]))

        if not results:
            print("Bot: I couldn't find closely matching products. Try different keywords or a simpler query.")
            continue

        # present results
        print(f"Bot: I found {len(results)} likely matches:")
        for score, meta in results:
            print(f"\n- Score: {score:.3f} | {summarize_metadata(meta)}")
            # show a few key fields as details
            row = meta['row']
            # show up to 5 non-empty columns
            shown = 0
            for col in row.index:
                val = row.get(col)
                if pd.isna(val) or str(val).strip() == '':
                    continue
                print(f"    {col}: {val}")
                shown += 1
                if shown >= 5:
                    break

        # small follow-up suggestion
        print("\nIf you'd like more details about one of these, ask 'tell me more about <product name>' or 'show price of <product name>'.")


def build_tfidf_index(corpus: List[str]):
    """Build and return a TF-IDF vectorizer and matrix for the given corpus.

    Returns (vectorizer, tfidf_matrix) or (None, None) if scikit-learn isn't available.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        return vectorizer, tfidf_matrix
    except Exception:
        return None, None


def retrieve_with_index(query: str, vectorizer, tfidf_matrix, metadata: List[Dict[str, Any]], top_k: int = 5):
    """Retrieve top_k results for query using provided TF-IDF index.

    Returns list of dicts: {'score': float, 'meta': metadata_dict, 'row': row_dict}
    If vectorizer or tfidf_matrix is None, returns an empty list.
    """
    results = []
    if vectorizer is None or tfidf_matrix is None:
        return results

    from sklearn.metrics.pairwise import cosine_similarity
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, tfidf_matrix).flatten()
    top_idxs = sims.argsort()[::-1][:max(50, top_k)]

    # parse price constraints and apply filtering
    min_p, max_p = parse_price_constraints(query)

    for idx in top_idxs:
        score = float(sims[idx])
        if score <= 0:
            continue
        meta = metadata[idx]
        price_val = extract_price_value(meta['row'])
        if (min_p is not None and price_val is not None and price_val < min_p) or (max_p is not None and price_val is not None and price_val > max_p):
            continue
        results.append({'score': score, 'meta': meta, 'row': meta['row'].to_dict()})
        if len(results) >= top_k:
            break

    return results
