import os

    # Configuration
class Config:
    # Database connection
    DB_USERNAME = 'demo'
    DB_PASSWORD = 'demo'
    DB_HOSTNAME = os.getenv('IRIS_HOSTNAME', 'localhost')
    DB_PORT = '1972'
    DB_NAMESPACE = 'USER'
    CONNECTION_STRING = f"{DB_HOSTNAME}:{DB_PORT}/{DB_NAMESPACE}"
    
    # Tables
    AVATAR_TABLE = "HealthChat.Avatars"
    AVATAR_INFO_TABLE = "HealthChat.AvatarInfo"
    MEDICAL_INFO_TABLE = "HealthChat.MedicalInfo"
    
    # LLM
    GOOGLE_API_KEY = "" # Add API key here
    MODEL_NAME = "gemini-2.0-flash"
    EMBEDDING_MODEL = "text-embedding-004"
    EMBEDDING_DIMENSION = 768  # For text-embedding-001
    
    # System settings
    MAX_RESULTS = 3
    EMBEDDING_CHUNK_SIZE = 1000  # Characters to chunk text for embedding

    # CSV paths
    AVATAR_CSV = "data/avatars.csv"
    AVATAR_INFO_CSV = "data/avatar_info.csv"
    MEDICAL_INFO_CSV = "data/medical_info.csv"
