import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COGNEE_API_KEY = os.getenv("COGNEE_API_KEY")

# Database Configuration
LANCEDB_PATH = "./lancedb_data"
VECTOR_DIMENSION = 384  # sentence-transformers/all-MiniLM-L6-v2

# Document Processing
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MAX_TOKENS = 4000

# Supported file types
SUPPORTED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.md']

# Product categories and brands
SUPPORTED_BRANDS = ['Samsung', 'LG']
PRODUCT_CATEGORIES = ['TV', 'Refrigerator', 'Washing Machine', 'Speaker', 'Air Conditioner']

# Document types
DOCUMENT_TYPES = ['SOP', 'FAQ', 'User Manual', 'Troubleshooting Guide'] 