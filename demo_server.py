"""
Simple Flask server to showcase the modern UI design.
This is a minimal version for demonstration purposes.
"""
from flask import Flask, send_from_directory
import os

# Create Flask app
app = Flask(__name__, static_folder='static')

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    """Serve the home page"""
    return send_from_directory(os.path.join(BASE_DIR, 'static'), 'home.html')

@app.route('/search')
def search():
    """Serve the search page"""
    return send_from_directory(os.path.join(BASE_DIR, 'static'), 'search.html')

@app.route('/chat')
def chat():
    """Serve the chat page"""
    return send_from_directory(os.path.join(BASE_DIR, 'static'), 'chat.html')

@app.route('/about')
def about():
    """Serve the about page"""
    return send_from_directory(os.path.join(BASE_DIR, 'static'), 'about.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)

if __name__ == '__main__':
    print("🚀 AI Product Finder - Modern Design Demo")
    print("📱 Access the app at: http://localhost:5000")
    print("✨ Features:")
    print("   • Modern Windows UI theme with pitch black design")
    print("   • Responsive layout optimized for all devices")
    print("   • Professional team showcase section")
    print("   • Comprehensive about page with project details")
    print("   • Consistent navigation across all pages")
    print("\n🔧 Developed by Aditya Tripathi for AI PBL")
    app.run(host='0.0.0.0', port=5000, debug=True)