import json
from utils.DatabaseManager import DatabaseManager
from utils.LLMService import LLMService
# Chatbot Main Class
class MedicalChatbot:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.llm_service = LLMService()
        self.current_avatar = None
        self.current_avatar_id = None
        self.chat_session = None
    
    def initialize(self):
        """Initialize the chatbot system"""
        self.db_manager.initialize_tables()
        # Here you would load avatar data and medical information
    
    def select_avatar(self, avatar_name: str):
        """Select an avatar to chat with"""
        # Get avatar ID and backstory
        backstory = self.db_manager.get_avatar_backstory(avatar_name)
        if backstory:
            self.current_avatar = avatar_name
            # In a real implementation, you'd get the actual ID from the database
            self.current_avatar_id = 1  # Placeholder
            
            # Create a new chat session with this avatar
            self.chat_session = self.llm_service.create_chat_session(backstory)
            return True
        return False
    
    def chat(self, user_input: str) -> str:
        """Process a user message and return the response"""
        if not self.chat_session:
            return "Please select an avatar first."
        
        try:
            # Send the message to the LLM
            response = self.chat_session.send_message(user_input)
            # print(response)
            # Initialize response text
            response_text = ""
            
            # Check if we have candidates in the response
            if hasattr(response, 'candidates') and response.candidates:
                # Get the first candidate
                candidate = response.candidates[0]
                
                # Check for function calls in the content parts
                if hasattr(candidate, 'content') and candidate.content.parts:
                    for part in candidate.content.parts:
                        # print("-------------------")
                        # print(part)
                        # print("-------------------")

                        # If part contains a function call
                        if hasattr(part, 'function_call') and part.function_call:
                            # Handle the function call
                            function_results = self.llm_service.handle_function_calls(
                                part.function_call, 
                                self.db_manager,
                                self.current_avatar_id
                            )
                            print("###################")
                            print(f"function call {part.function_call}")
                            print("###################")
                            # print(function_results)
                            # print("###################")
                            # print(function_results['results'])
                            formatted_message = json.dumps(function_results['results'], indent=2)
                            # Send function results back to continue the conversation
                            follow_up_response = self.chat_session.send_message(
                                # function_name=part.function_call.name,
                                # function_response=function_results
                                "Retrieved from database:" + formatted_message
                            )
                            
                            # Update response with the follow-up
                            response = follow_up_response
                        
                        # If part contains text, add it to the response
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
            
            # If we didn't get text from parts, try the response.text property
            if not response_text and hasattr(response, 'text'):
                response_text = response.text
            
            return response_text
        
        except Exception as e:
            print(f"Error in chat: {e}")
            return "I'm sorry, I encountered an error. Please try again."
