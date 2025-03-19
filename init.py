from utils.Config import Config
from utils.DatabaseManager import DatabaseManager
from utils.LLMService import LLMService
from utils.MedicalChatbot import MedicalChatbot

def populate_database():
    """Main function to populate the database from CSV files"""
    try:        
        # Initialize database and LLM service
        db_manager = DatabaseManager()
        db_manager.initialize_tables()
        
        llm_service = LLMService()
        db_manager.set_llm_service(llm_service)
        
        # Import data from CSVs
        print("Importing avatar data...")
        db_manager.import_avatars(Config.AVATAR_CSV)
        
        print("Importing avatar info data...")
        db_manager.import_avatar_info(Config.AVATAR_INFO_CSV)
        
        print("Importing medical info data...")
        db_manager.import_medical_info(Config.MEDICAL_INFO_CSV)
        
        print("Database population completed successfully!")
        
    except Exception as e:
        print(f"Error populating database: {e}")

def main():
    # Populate the database
    populate_database()

    # Initialize the chatbot and associated databases
    chatbot = MedicalChatbot()
    chatbot.initialize()

if __name__ == "__main__":
    main()
