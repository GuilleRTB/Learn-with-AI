"""
AI Chat view for LearnwithAI - Conversation with chatbot and audio recording
"""

import json
import re
import toga
from toga.style.pack import COLUMN, ROW, Pack
from ..services.ai_service import AIChatService


class AIChatView:
    def __init__(self, app):
        self.app = app
        self.conversation_history = []
        self.recording = False
        # Use the shared AI service from the app
        self.ai_service = app.ai_service
        
    def create_view(self):
        """Create the AI chat page with text and audio capabilities"""
        # Header with back button
        back_button = toga.Button(
            "← Retour",
            on_press=self.go_back,
            style=Pack(padding=10)
        )
        
        title = toga.Label(
            "🤖 Talk with AI",
            style=Pack(
                text_align="center",
                font_size=20,
                font_weight="bold",
                padding=20
            )
        )
        
        header_box = toga.Box(
            children=[back_button, title],
            style=Pack(direction=ROW, alignment="center")
        )
        
        # Chat display area
        self.chat_display = toga.MultilineTextInput(
            readonly=True,
            style=Pack(
                flex=1,
                padding=10,
                height=300
            )
        )
        
        # Text input for typing messages
        self.message_input = toga.TextInput(
            placeholder="Tapez votre message en anglais...",
            style=Pack(
                flex=1,
                padding=5
            )
        )
        
        # Send button
        send_button = toga.Button(
            "Envoyer",
            on_press=self.send_message,
            style=Pack(padding=5, width=100)
        )
        
        # Text input container
        text_input_box = toga.Box(
            children=[self.message_input, send_button],
            style=Pack(direction=ROW, padding=10)
        )
        
        # Audio recording buttons
        record_button = toga.Button(
            "🎤 Enregistrer Audio",
            on_press=self.start_recording,
            style=Pack(padding=5, width=150)
        )
        
        stop_button = toga.Button(
            "⏹️ Arrêter",
            on_press=self.stop_recording,
            style=Pack(padding=5, width=100)
        )
        
        play_button = toga.Button(
            "▶️ Écouter",
            on_press=self.play_recording,
            style=Pack(padding=5, width=100)
        )
        
        # Audio controls container
        audio_box = toga.Box(
            children=[record_button, stop_button, play_button],
            style=Pack(direction=ROW, padding=10, alignment="center")
        )
        
        # Recording status
        self.recording_status = toga.Label(
            "Prêt à enregistrer",
            style=Pack(
                text_align="center",
                padding=5,
                color="#666666"
            )
        )
        
        # Main container
        main_box = toga.Box(
            children=[
                header_box,
                self.chat_display,
                text_input_box,
                audio_box,
                self.recording_status
            ],
            style=Pack(
                direction=COLUMN,
                padding=20
            )
        )
        
        # Initialize chat with welcome message
        self.add_message("AI Assistant", "Hi there! How’s your day going? I'm your English practice partner. You can write or speak — let's start improving your English together!")

        return main_box
    
    def go_back(self, widget):
        """Return to home view"""
        from .home_view import HomeView
        home_view = HomeView(self.app)
        self.app.main_window.content = home_view.create_view()
        
    def send_message(self, widget):
        """Send text message to AI"""
        message = self.message_input.value.strip()
        if message:
            # Add user message to chat
            self.add_message("Vous", message)
            
            # Clear input
            self.message_input.value = ""
            
            # Show thinking indicator
            self.add_message("AI Assistant", "🤔 Thinking...")
            
            try:
                # Get AI response using Groq
                ai_response = self.ai_service.send_message(message, self.conversation_history)
                
                # Remove thinking indicator first
                self.remove_last_message()
                
                # Process and display the response
                self.process_ai_response(ai_response)
                
            except Exception as e:
                # Remove thinking indicator and show error
                self.remove_last_message()
                self.add_message("AI Assistant", f"Sorry, I encountered an error: {str(e)}")
                print(f"AI Service error: {e}")
    
    def add_message(self, sender, message):
        """Add a message to the chat display"""
        timestamp = "now"  # TODO: Add proper timestamp
        formatted_message = f"[{timestamp}] {sender}: {message}\n\n"
        
        current_text = self.chat_display.value or ""
        self.chat_display.value = current_text + formatted_message
        
        # Store in conversation history
        self.conversation_history.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        })
    
    def add_tip_message(self, tips):
        """Add a tip message with gray styling"""
        timestamp = "now"
        
        # Créer un label pour les conseils avec style gris
        tip_label = toga.Label(
            f"💡 Conseil: {tips}",
            style=Pack(
                padding=5,
                color="#666666",  # Couleur grise
                font_style="italic"
            )
        )
        
        # Pour l'instant, on utilise le système normal mais avec un préfixe spécial
        # TODO: Améliorer avec un vrai widget stylé quand Toga le supportera mieux
        formatted_message = f"[{timestamp}] 💡 Conseil: {tips}\n\n"
        
        current_text = self.chat_display.value or ""
        self.chat_display.value = current_text + formatted_message
        
        # Store in conversation history avec un type spécial
        self.conversation_history.append({
            'sender': '💡 Conseil',
            'message': tips,
            'timestamp': timestamp,
            'type': 'tip'  # Marquer comme conseil
        })
    
    def remove_last_message(self):
        """Remove the last message from chat display (for removing thinking indicator)"""
        if self.conversation_history:
            # Remove from history
            self.conversation_history.pop()
            
            # Rebuild chat display
            self.chat_display.value = ""
            for msg in self.conversation_history:
                formatted_message = f"[{msg['timestamp']}] {msg['sender']}: {msg['message']}\n\n"
                current_text = self.chat_display.value or ""
                self.chat_display.value = current_text + formatted_message
    
    def start_recording(self, widget):
        """Start audio recording"""
        self.recording_status.text = "🔴 Enregistrement en cours..."
        # TODO: Implement audio recording functionality
        # This would require additional libraries like pyaudio or similar
        self.app.main_window.info_dialog("Info", "Fonctionnalité d'enregistrement à implémenter")
    
    def stop_recording(self, widget):
        """Stop audio recording"""
        self.recording_status.text = "⏹️ Enregistrement arrêté"
        # TODO: Stop recording and process audio
        # Convert speech to text and send to AI
    
    def play_recording(self, widget):
        """Play the last recording"""
        # TODO: Implement audio playback
        self.app.main_window.info_dialog("Info", "Fonctionnalité de lecture à implémenter")
    
    def process_ai_response(self, ai_response):
        """Process AI response and update chat display"""
        try:
            # Nettoyer la réponse (enlever les balises markdown si présentes)
            cleaned_response = ai_response.strip()
            
            # Chercher du JSON dans la réponse (même s'il y a du texte autour)
            json_pattern = r'\{[^{}]*"response"[^{}]*\}'
            json_match = re.search(json_pattern, cleaned_response, re.DOTALL)
            
            if json_match:
                try:
                    json_str = json_match.group(0)
                    parsed_response = json.loads(json_str)
                    
                    # Récupérer la réponse principale
                    main_response = parsed_response.get('response', '')
                    tips = parsed_response.get('tips', '')
                    
                    # Afficher la réponse principale si elle existe
                    if main_response and main_response.strip():
                        self.add_message("AI Assistant", main_response)
                    else:
                        # Si pas de réponse dans le JSON, utiliser la réponse complète
                        self.add_message("AI Assistant", ai_response)
                    
                    # Si des conseils existent et ne sont pas vides, les afficher en gris
                    if tips and tips.strip():
                        self.add_tip_message(tips)
                    
                    return  # Succès, on sort de la fonction
                    
                except json.JSONDecodeError as e:
                    print(f"Erreur de parsing JSON: {e}")
                    # Continuer vers le traitement normal
            
            # Vérifier si c'est du JSON complet et valide
            if cleaned_response.startswith('{') and cleaned_response.endswith('}'):
                try:
                    parsed_response = json.loads(cleaned_response)
                    
                    # Récupérer la réponse principale
                    main_response = parsed_response.get('response', ai_response)
                    tips = parsed_response.get('tips', '')
                    
                    # Afficher la réponse principale
                    self.add_message("AI Assistant", main_response)
                    
                    # Si des conseils existent et ne sont pas vides, les afficher en gris
                    if tips and tips.strip():
                        self.add_tip_message(tips)
                    
                    return  # Succès, on sort de la fonction
                    
                except json.JSONDecodeError:
                    # Si le parsing JSON échoue, continuer vers le traitement normal
                    pass
            
            # Traitement normal si ce n'est pas du JSON valide
            self.add_message("AI Assistant", ai_response)
                
        except Exception as e:
            print(f"Erreur lors du traitement de la réponse AI: {e}")
            # En cas d'erreur, afficher la réponse brute
            self.add_message("AI Assistant", str(ai_response))
