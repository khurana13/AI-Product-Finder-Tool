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

AI-PBL/
├── app/ # Flask app & TF-IDF search logic
│ ├── main.py
│ └── search_engine.py
├── data/ # Product datasets (CSV)
│ ├── laptop.csv
│ ├── mobile.csv
│ └── headphone.csv
├── persist/ # Cached models & admin data
├── static/ # Frontend (HTML, CSS, JS)
├── tests/ # Test files
├── archive/ # Deprecated files
├── .env.example # Environment variables template
├── requirements.txt
└── run.py # App entry point
