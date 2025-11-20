"""
Test suite for search_engine.py
"""
import pytest
import pandas as pd
from app import search_engine


def test_load_data():
    """Test that data loads correctly from CSV files"""
    data = search_engine.load_data()
    assert data is not None
    assert 'laptop' in data
    assert 'mobile' in data
    assert 'headphone' in data
    assert isinstance(data['laptop'], pd.DataFrame)
    assert len(data['laptop']) > 0


def test_build_corpus():
    """Test corpus building from data"""
    data = search_engine.load_data()
    corpus, metadata = search_engine.build_corpus_from_data(data)
    assert corpus is not None
    assert metadata is not None
    assert len(corpus) == len(metadata)
    assert len(corpus) > 0


def test_parse_price_constraints():
    """Test price parsing from queries"""
    # Test "under X"
    min_p, max_p = search_engine.parse_price_constraints("laptop under 50000")
    assert min_p == 0
    assert max_p == 50000
    
    # Test "between X and Y"
    min_p, max_p = search_engine.parse_price_constraints("phone between 10000 and 20000")
    assert min_p == 10000
    assert max_p == 20000
    
    # Test "above/over X"
    min_p, max_p = search_engine.parse_price_constraints("laptop above 30000")
    assert min_p == 30000
    assert max_p == float('inf')


def test_build_tfidf_index():
    """Test TF-IDF index building"""
    data = search_engine.load_data()
    corpus, metadata = search_engine.build_corpus_from_data(data)
    vectorizer, tfidf_matrix = search_engine.build_tfidf_index(corpus)
    
    assert vectorizer is not None
    assert tfidf_matrix is not None
    assert tfidf_matrix.shape[0] == len(corpus)


def test_retrieve_with_index():
    """Test retrieval using TF-IDF index"""
    data = search_engine.load_data()
    corpus, metadata = search_engine.build_corpus_from_data(data)
    vectorizer, tfidf_matrix = search_engine.build_tfidf_index(corpus)
    
    # Test basic query
    results = search_engine.retrieve_with_index(
        "gaming laptop", 
        vectorizer, 
        tfidf_matrix, 
        metadata, 
        top_k=5
    )
    
    assert isinstance(results, list)
    assert len(results) <= 5
    if len(results) > 0:
        assert 'score' in results[0]
        assert 'data' in results[0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
