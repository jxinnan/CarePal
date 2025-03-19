import csv
import iris
from typing import List, Dict, Any, Optional
from utils.Config import Config

# Database handler
class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.llm_service = None  # Will be initialized later
        self.connect()
        
    def connect(self):
        """Connect to the IRIS database"""
        try:
            self.conn = iris.connect(
                Config.CONNECTION_STRING, 
                Config.DB_USERNAME, 
                Config.DB_PASSWORD
            )
            self.cursor = self.conn.cursor()
            print(f"Connected to {Config.CONNECTION_STRING}")
        except Exception as e:
            print(f"Database connection failed: {e}")
            
    def initialize_tables(self):
        """Create necessary tables if they don't exist"""
        # Avatar basic information table
        self.create_table(
            Config.AVATAR_TABLE,
            """(
                id INT PRIMARY KEY, 
                name VARCHAR(255), 
                category VARCHAR(255),
                backstory LONGVARCHAR
            )"""
        )
        
        # Avatar detailed information with vector embeddings
        self.create_table(
            Config.AVATAR_INFO_TABLE,
            f"""(
                id INT PRIMARY KEY,
                avatar_id INT,
                info_type VARCHAR(255),
                content LONGVARCHAR,
                content_vector VECTOR(DOUBLE, {Config.EMBEDDING_DIMENSION}),
                FOREIGN KEY (avatar_id) REFERENCES {Config.AVATAR_TABLE}(id)
            )"""
        )
        
        # Medical information with vector embeddings
        self.create_table(
            Config.MEDICAL_INFO_TABLE,
            f"""(
                id INT PRIMARY KEY,
                topic VARCHAR(255),
                subtopic VARCHAR(255),
                content LONGVARCHAR,
                content_vector VECTOR(DOUBLE, {Config.EMBEDDING_DIMENSION}),
                source VARCHAR(255),
                last_updated DATE
            )"""
        )
    
    def create_table(self, table_name, table_definition):
        """Create a table if it doesn't exist"""
        try:
            
            # self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.cursor.execute(f"CREATE TABLE {table_name} {table_definition}")
            print(f"Table {table_name} created successfully")
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")
    
    def set_llm_service(self, llm_service):
        """Set the LLM service for embedding generation"""
        self.llm_service = llm_service

    def import_avatars(self, csv_path):
        """Import avatar data from CSV file"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Insert avatar data
                    sql = f"""
                        INSERT INTO {Config.AVATAR_TABLE} 
                        (id, name, category, backstory) 
                        VALUES (?, ?, ?, ?)
                    """
                    self.cursor.execute(sql, [
                        int(row['id']), 
                        str(row['name']), 
                        str(row['category']), 
                        row['backstory']
                    ])
            
            print(f"Successfully imported {csv_path}")
        except Exception as e:
            print(f"Error importing avatars: {e}")
            self.conn.rollback()

    def import_avatar_info(self, csv_path):
        """Import avatar information from CSV file and generate embeddings"""
        if not self.llm_service:
            print("LLM service not set. Cannot generate embeddings.")
            return
            
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Generate embedding for the content
                    try:
                        embedding = self.llm_service.generate_embedding(row['content'])
                    except Exception as e:
                        print(f"Failed to generate embedding for avatar info id {row['id']}: {e}")
                        continue
                    if not embedding:
                        print(f"Failed to generate embedding for avatar info id {row['id']}")
                        continue
                        
                    # Insert avatar info with embedding
                    sql = f"""
                        INSERT INTO {Config.AVATAR_INFO_TABLE} 
                        (id, avatar_id, info_type, content, content_vector) 
                        VALUES (?, ?, ?, ?, TO_VECTOR(?))
                    """
                    self.cursor.execute(sql, [
                        int(row['id']), 
                        int(row['avatar_id']), 
                        str(row['info_type']), 
                        str(row['content']),
                        str(embedding)
                    ])
            
            print(f"Successfully imported {csv_path}")
        except Exception as e:
            print(f"Error importing avatar info: {e}")
            self.conn.rollback()

    def import_medical_info(self, csv_path):
        """Import medical information from CSV file and generate embeddings"""
        if not self.llm_service:
            print("LLM service not set. Cannot generate embeddings.")
            return
            
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Generate embedding for the content
                    embedding = self.llm_service.generate_embedding(row['content'])
                    
                    if not embedding:
                        print(f"Failed to generate embedding for medical info id {row['id']}")
                        continue
                        
                    # Insert medical info with embedding
                    sql = f"""
                        INSERT INTO {Config.MEDICAL_INFO_TABLE} 
                        (id, topic, subtopic, content, content_vector, source, last_updated) 
                        VALUES (?, ?, ?, ?, TO_VECTOR(?), ?, ?)
                    """
                    self.cursor.execute(sql, [
                        int(row['id']), 
                        str(row['topic']), 
                        str(row['subtopic']), 
                        str(row['content']),
                        str(embedding),
                        str(row['source']),
                        str(row['last_updated'])
                    ])
            
            print(f"Successfully imported {csv_path}")
        except Exception as e:
            print(f"Error importing medical info: {e}")
            self.conn.rollback()
    def query_avatar_info(self, avatar_id: int, query_vector: List[float]) -> List[Dict]:
        """Retrieve avatar information based on vector similarity"""
        try:
            sql = f"""
                SELECT TOP {Config.MAX_RESULTS} info_type, content
                FROM {Config.AVATAR_INFO_TABLE}
                WHERE avatar_id = ?
                ORDER BY VECTOR_DOT_PRODUCT(content_vector, TO_VECTOR(?)) DESC
            """
            self.cursor.execute(sql, [avatar_id, str(query_vector)])
            results = self.cursor.fetchall()
            return [{"info_type": r[0], "content": r[1]} for r in results]
        except Exception as e:
            print(f"Error querying avatar info: {e}")
            return []
    
    def query_medical_info(self, query_vector: List[float]) -> List[Dict]:
        """Retrieve relevant medical information based on vector similarity"""
        try:
            sql = f"""
                SELECT TOP ? topic, subtopic, content, source
                FROM {Config.MEDICAL_INFO_TABLE}
                ORDER BY VECTOR_DOT_PRODUCT(content_vector, TO_VECTOR(?)) DESC
            """
            # check data type of query_vector
            numberOfResults = 3
            self.cursor.execute(sql, [numberOfResults, str(query_vector)])
            results = self.cursor.fetchall()
            return [
                {
                    "topic": r[0], 
                    "subtopic": r[1], 
                    "content": r[2], 
                    "source": r[3]
                } 
                for r in results
            ]
        except Exception as e:
            print(f"Error querying medical info: {e}")
            return []

    def get_avatar_backstory(self, avatar_name: str) -> str:
        """Get the backstory for a specific avatar"""
        try:
            sql = f"""
                SELECT *
                FROM {Config.AVATAR_TABLE}
                WHERE category = ?
            """
            self.cursor.execute(sql, [avatar_name])

            rows = self.cursor.fetchall()
            result_string = "\n".join([str(row) for row in rows])

            return result_string if result_string else ""
        except Exception as e:
            print(f"Error getting avatar backstory: {e}")
            return ""
