"""
AI Chat Service for LearnwithAI
Handles communication with Groq AI API for language learning
"""

import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Groq not available. Install with: pip install groq")

# Import prompts system
from ..prompts.teaching_prompts import get_prompt, get_available_prompt_types

# Load environment variables
load_dotenv()

class AIChatService:
    def __init__(self, prompt_type: str = "default"):
        """Initialize the AI chat service with Groq API"""
        # Load configuration
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "500"))
        
        # Load prompt type from environment or use parameter
        self.prompt_type = os.getenv("PROMPT_TYPE", prompt_type)
        
        # Load user settings if available
        self.settings = self.load_user_settings()
        
        # Adjust prompt type based on settings and get system prompt
        self.apply_settings_to_prompt()
        
        # Log information about the selected prompt
        print(f"🎯 Using prompt type: {self.prompt_type}")
        print(f"� Level: {self.settings.get('level', 'Beginner')}")
        print(f"📝 System prompt activated")
        
        # Initialize Groq client
        self.client = None
        self._initialize_groq()
    
    def _initialize_groq(self):
        """Initialize Groq client"""
        if not GROQ_AVAILABLE:
            print("❌ Groq library not available. Install with: pip install groq")
            return
        
        if not self.api_key:
            print("❌ GROQ_API_KEY not found in environment variables")
            print("💡 Get your free API key at: https://console.groq.com/")
            return
        
        try:
            self.client = Groq(api_key=self.api_key)
            print(f"✅ Groq AI initialized successfully with model: {self.model}")
            
        except Exception as e:
            print(f"❌ Error initializing Groq: {e}")
            self.client = None
            
    def load_user_settings(self):
        """Load user settings from JSON file"""
        settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'settings.json')
        default_settings = {
            "level": "Beginner",
            "focus": "Conversation"
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    return json.load(f)
            else:
                return default_settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings
            
    def apply_settings_to_prompt(self):
        """Apply user settings to the prompt type"""
        # Map user settings to prompt types
        level = self.settings.get('level', 'Beginner').lower()
        focus = self.settings.get('focus', 'Conversation').lower()
        
        # Determine the best prompt type based on settings
        if focus == 'school':
            self.prompt_type = 'school'
        elif focus == 'conversation':
            self.prompt_type = 'conversation'
        elif focus == 'job interview':
            self.prompt_type = 'interview' 
        elif focus == 'business':
            self.prompt_type = 'business'
        elif focus == 'travel':
            self.prompt_type = 'travel'
        else:
            # Default
            self.prompt_type = 'default'
        
        # Update the system prompt with the new settings
        self.system_prompt = get_prompt(self.prompt_type, level)
            
        print(f"🔧 Applied settings - Level: {level}, Focus: {focus} -> Prompt: {self.prompt_type}")
        print(f"📝 Updated system prompt based on settings")
    
    def change_prompt_type(self, prompt_type: str) -> bool:
        """
        Change le type de prompt utilisé
        
        Args:
            prompt_type (str): Nouveau type de prompt
            
        Returns:
            bool: True si le changement a réussi
        """
        available_types = get_available_prompt_types()
        if prompt_type.lower() not in available_types:
            print(f"❌ Type de prompt '{prompt_type}' non disponible")
            print(f"💡 Types disponibles: {', '.join(available_types)}")
            return False
        
        self.prompt_type = prompt_type.lower()
        self.system_prompt = get_prompt(self.prompt_type, self.settings.get('level', 'beginner').lower())
        print(f"✅ Prompt changé vers: {self.prompt_type}")
        return True
        
    def refresh_settings(self):
        """
        Reload user settings and update prompt if necessary
        """
        # Reload settings from file
        self.settings = self.load_user_settings()
        
        # Apply new settings to prompt (this also updates self.system_prompt)
        self.apply_settings_to_prompt()
        
        print(f"🔄 Settings refreshed - Level: {self.settings.get('level', 'Beginner')}, Focus: {self.settings.get('focus', 'Conversation')}")
        print(f"📝 System prompt updated")
    
    def get_current_prompt_info(self) -> Dict[str, str]:
        """
        Retourne les informations sur le prompt actuel
        
        Returns:
            dict: Informations sur le prompt
        """
        from ..prompts.teaching_prompts import get_prompt_description
        return {
            "type": self.prompt_type,
            "description": get_prompt_description(self.prompt_type),
            "prompt": self.system_prompt
        }
    
    def list_available_prompts(self) -> List[Dict[str, str]]:
        """
        Liste tous les prompts disponibles avec leurs descriptions
        
        Returns:
            list: Liste des prompts avec descriptions
        """
        from ..prompts.teaching_prompts import get_prompt_description
        available_types = get_available_prompt_types()
        
        return [
            {
                "type": prompt_type,
                "description": get_prompt_description(prompt_type)
            }
            for prompt_type in available_types
        ]
        
    def send_message(self, message: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Send message to Groq AI and get response
        
        Args:
            message (str): User's message
            conversation_history (list): Previous conversation context
            
        Returns:
            str: AI response
        """
        if not self.client:
            return self._fallback_response(message)
        
        try:
            # Print system prompt to terminal for debugging
            print("\n" + "="*50)
            print("🔍 CURRENT SYSTEM PROMPT:")
            print("-"*50)
            print(self.system_prompt)
            print("="*50 + "\n")
            
            # Build conversation context in Groq format
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history (exclude tips and keep only actual conversation)
            if conversation_history:
                for hist_msg in conversation_history[-10:]:  # Keep last 10 messages for context
                    # Skip tip messages to avoid polluting the conversation context
                    if hist_msg.get('type') == 'tip':
                        continue
                    
                    if hist_msg['sender'] == 'Vous':
                        messages.append({"role": "user", "content": hist_msg['message']})
                    elif hist_msg['sender'] == 'AI Assistant':
                        messages.append({"role": "assistant", "content": hist_msg['message']})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Get response from Groq
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error getting Groq AI response: {e}")
            return self._fallback_response(message)
    
    def _fallback_response(self, message: str) -> str:
        """Fallback response when AI service is not available"""
        responses = [
            f"Thank you for saying: '{message}'. That's great English practice!",
            f"I heard you say '{message}'. Can you try using that in a sentence?",
            f"'{message}' - Good! Can you tell me more about that topic?",
            f"Interesting point about '{message}'. How would you explain that to a friend?",
        ]
        import random
        return random.choice(responses)
    
    def process_audio_to_text(self, audio_file_path):
        """
        Convert audio to text using speech recognition
        
        Args:
            audio_file_path (str): Path to audio file
            
        Returns:
            str: Transcribed text
        """
        # TODO: Implement speech-to-text (Whisper API, Google Speech, etc.)
        return "Audio transcription will be implemented here"
    
    def text_to_speech(self, text, output_path):
        """
        Convert text to speech for pronunciation practice
        
        Args:
            text (str): Text to convert to speech
            output_path (str): Where to save audio file
        """
        # TODO: Implement text-to-speech
        pass
    
    def get_language_correction(self, text):
        """
        Get grammar and vocabulary corrections
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Corrections and suggestions
        """
        # TODO: Implement language correction analysis
        return {
            'corrections': [],
            'suggestions': [],
            'level_assessment': 'intermediate'
        }