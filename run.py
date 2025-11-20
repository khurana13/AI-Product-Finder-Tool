"""
Student Project Entrypoint

Small wrapper to run the Flask app for local development. Part of a
student assignment. Replace or remove this comment when preparing
for production.
"""
from app.main import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
