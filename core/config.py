import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # GitHub
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  

    # API Keys
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    
    # Performance Settings
    MAX_FILES_TO_FETCH = int(os.getenv('MAX_FILES_TO_FETCH', '20'))  # Show scalability
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '5'))  # Process in batches
    CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes
    
    # Thresholds
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.6'))
    
config = Config()