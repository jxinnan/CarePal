import json
from google import genai
from google.genai import types
from typing import List, Dict, Any, Optional
from utils.Config import Config

# LLM Service
class LLMService:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        self.safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.OFF,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
        
        # Define functions for the LLM to call
        self.functions = [
            {
                "function_declarations":[
            {
                "name": "get_avatar_information",
                "description": "Get more information about the avatar to enhance the response",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The specific information needed about the avatar"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_medical_information",
                "description": "Retrieve accurate medical information from the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The medical topic to search for information about"
                        }
                    },
                    "required": ["query"]
                }
            }
                ]
            }
        ]
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        try:
            embedding = self.client.models.embed_content(
                model=Config.EMBEDDING_MODEL,
                contents=text,
            )
            return embedding.embeddings[0].values
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def create_chat_session(self, avatar_backstory: str, user_name: str = "Nancy"):
        """Create a new chat session with the specified avatar's backstory"""
        
        system_prompt = f"""
You are CarePal, a chatbot designed to answer medical queries and provide emotional support. When you provide any medical information, forget all prior knowledge, and call the function get_medical_information.

To generate inputs for the function, read the user's prompt and generate relevant terms, which can include disease names, condition names, types of medication, drug names, treatment description, treatment names and symptoms. For each distinct term, call the function once separately. Using only the outputs from the function calls, provide relevant medical information.

Here, let's talk about your personality and behaviour. The user thinks that they are talking to a former patient, who is suffering from the same condition as them. You would adopt the former patient's persona, using their patient profile. Change your style of speech entirely to fit to the former patient's style of speech. You should refer to the following patient profile:

START OF PATIENT PROFILE
{avatar_backstory}
END OF PATIENT PROFILE

Next, you should follow these instructions as well. First, you introduce yourself as the former patient. Engage in conversation, and continue to refer to accurate medical information as instructed above. When the user wishes to end the conversation with the former patient, bid farewell.

If you need more information about your persona, which can include personal experiences, experienced symptoms, treatment options, or other information, then call the function get_avatar_information.
        """
        
        chat = self.client.chats.create(
            model=Config.MODEL_NAME,
            config=types.GenerateContentConfig(
                tools=self.functions,
                system_instruction=system_prompt,
                safety_settings=self.safety_settings,
            )
        )
        return chat
        
    def handle_function_calls(self, function_call, db_manager, avatar_id=None):
        """Handle function calls from the LLM"""
        try:
            # Extract function name and arguments
            function_name = function_call.name
            function_args = {}
            
            # Some versions of the API provide args as a dict-like object
            if hasattr(function_call, 'args') and function_call.args:
                function_args = function_call.args
            # Others might provide it as a JSON string
            elif hasattr(function_call, 'arguments') and function_call.arguments:
                try:
                    function_args = json.loads(function_call.arguments)
                except:
                    print(f"Failed to parse function arguments: {function_call.arguments}")
            
            # Get the query parameter
            query = function_args.get("query", "")
            
            # Handle different function types
            if function_name == "get_avatar_information" and avatar_id:
                query_vector = self.generate_embedding(query)
                results = db_manager.query_avatar_info(avatar_id, query_vector)
                
                # Format results for readability when returned to the model
                formatted_results = {
                    "query": query,
                    "avatar_id": avatar_id,
                    "results": results,
                    "result_count": len(results)
                }
                return formatted_results
            
            elif function_name == "get_medical_information":
                query_vector = self.generate_embedding(query)
                results = db_manager.query_medical_info(query_vector)
                
                # Format results for readability when returned to the model
                formatted_results = {
                    "query": query,
                    "results": results,
                    "result_count": len(results)
                }
                return formatted_results
            
            return {"error": f"Invalid function call: {function_name}"}
            
        except Exception as e:
            print(f"Error in handle_function_calls: {e}")
            return {"error": f"Function call error: {str(e)}"} 
