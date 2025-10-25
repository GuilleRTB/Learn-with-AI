"""
AI Chat view for LearnwithAI - Conversation with chatbot and audio recording
"""

import json
import os
import re
import toga
from toga.style.pack import COLUMN, ROW, Pack
from ..services.ai_service import AIChatService
import pyaudio
import wave
import threading
import time
from datetime import datetime


class AudioService:
    def __init__(self):
        self.pyaudio_instance = None
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.current_file = None
        self.recordings_dir = os.path.join(os.path.dirname(__file__), "..", "recordings")
        
        # Configuration audio adaptative
        self.chunk = 1024
        self.channels = 1  # Mono pour la plupart des micros intégrés
        self.sample_width = 2  # 16-bit
        
        # Détection automatique du taux d'échantillonnage
        self.sample_rate = self._detect_best_sample_rate()
        
        # Créer le dossier d'enregistrements s'il n'existe pas
        os.makedirs(self.recordings_dir, exist_ok=True)
        
        print(f"🎤 AudioService initialized with sample rate: {self.sample_rate} Hz")
    
    def _detect_best_sample_rate(self):
        """Détecte le meilleur taux d'échantillonnage supporté par le microphone"""
        p = pyaudio.PyAudio()
        
        try:
            # Obtenir le périphérique d'entrée par défaut
            default_device = p.get_default_input_device_info()
            device_index = default_device['index']
            
            print(f"🎤 Testing audio device: {default_device['name']}")
            
            # Tester différents taux d'échantillonnage par ordre de préférence
            test_rates = [44100, 48000, 22050, 16000, 8000]
            
            for rate in test_rates:
                try:
                    # Tester si ce taux est supporté
                    if p.is_format_supported(
                        rate=rate,
                        input_device=device_index,
                        input_channels=1,
                        input_format=pyaudio.paInt16
                    ):
                        print(f"✓ Sample rate {rate} Hz is supported")
                        p.terminate()
                        return rate
                except Exception as e:
                    print(f"✗ Sample rate {rate} Hz not supported: {e}")
                    continue
            
            # Si aucun taux standard ne fonctionne, utiliser le taux par défaut
            default_rate = int(default_device['defaultSampleRate'])
            print(f"⚠️ Using device default sample rate: {default_rate} Hz")
            p.terminate()
            return default_rate
            
        except Exception as e:
            print(f"❌ Error detecting sample rate: {e}")
            p.terminate()
            return 44100  # Fallback
    
    def _get_best_input_device(self):
        """Trouve le meilleur périphérique d'entrée disponible"""
        if not self.pyaudio_instance:
            self.pyaudio_instance = pyaudio.PyAudio()
        
        try:
            # Essayer le périphérique par défaut d'abord
            default_device = self.pyaudio_instance.get_default_input_device_info()
            return default_device['index']
        except:
            # Si pas de périphérique par défaut, chercher le premier avec entrée
            for i in range(self.pyaudio_instance.get_device_count()):
                device_info = self.pyaudio_instance.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    return i
            return None
    
    def start_recording(self):
        """Démarre l'enregistrement audio"""
        if self.is_recording:
            print("⚠️ Recording already in progress")
            return False
        
        try:
            # Initialiser PyAudio si nécessaire
            if not self.pyaudio_instance:
                self.pyaudio_instance = pyaudio.PyAudio()
            
            # Obtenir le meilleur périphérique d'entrée
            input_device = self._get_best_input_device()
            if input_device is None:
                print("❌ No input device available")
                return False
            
            # Configuration du stream avec détection automatique
            stream_params = {
                'format': pyaudio.paInt16,
                'channels': self.channels,
                'rate': self.sample_rate,
                'input': True,
                'input_device_index': input_device,
                'frames_per_buffer': self.chunk
            }
            
            print(f"🎤 Starting recording with params: {stream_params}")
            
            # Créer le stream
            self.stream = self.pyaudio_instance.open(**stream_params)
            
            # Réinitialiser les frames
            self.frames = []
            self.is_recording = True
            
            # Démarrer l'enregistrement dans un thread séparé
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.start()
            
            print("🔴 Recording started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error starting recording: {e}")
            self.is_recording = False
            if self.stream:
                self.stream.close()
                self.stream = None
            return False
    
    def _record_audio(self):
        """Thread function pour enregistrer l'audio"""
        try:
            while self.is_recording:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
        except Exception as e:
            print(f"❌ Error during recording: {e}")
            self.is_recording = False
    
    def stop_recording(self):
        """Arrête l'enregistrement et sauvegarde le fichier"""
        if not self.is_recording:
            print("⚠️ No recording in progress")
            return None
        
        try:
            # Arrêter l'enregistrement
            self.is_recording = False
            
            # Attendre que le thread se termine
            if hasattr(self, 'recording_thread'):
                self.recording_thread.join(timeout=2.0)
            
            # Fermer le stream
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            # Sauvegarder le fichier
            if self.frames:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recording_{timestamp}.wav"
                self.current_file = os.path.join(self.recordings_dir, filename)
                
                # Écrire le fichier WAV
                with wave.open(self.current_file, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(self.pyaudio_instance.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(b''.join(self.frames))
                
                print(f"💾 Recording saved: {self.current_file}")
                return self.current_file
            else:
                print("⚠️ No audio data recorded")
                return None
                
        except Exception as e:
            print(f"❌ Error stopping recording: {e}")
            return None
    
    def play_audio(self, file_path=None):
        """Lit un fichier audio"""
        if file_path is None:
            file_path = self.current_file
        
        if not file_path or not os.path.exists(file_path):
            print("❌ Audio file not found")
            return False
        
        try:
            # Initialiser PyAudio si nécessaire
            if not self.pyaudio_instance:
                self.pyaudio_instance = pyaudio.PyAudio()
            
            # Ouvrir le fichier WAV
            with wave.open(file_path, 'rb') as wf:
                # Créer un stream de lecture
                stream = self.pyaudio_instance.open(
                    format=self.pyaudio_instance.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                # Lire et jouer le fichier
                chunk_size = 1024
                data = wf.readframes(chunk_size)
                
                while data:
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                
                # Nettoyer
                stream.stop_stream()
                stream.close()
                
            print(f"▶️ Playback completed: {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
            return False
    
    def get_recording_duration(self):
        """Retourne la durée d'enregistrement actuelle en secondes"""
        if self.is_recording and self.frames:
            return len(self.frames) * self.chunk / self.sample_rate
        return 0
    
    def list_recordings(self):
        """Liste tous les enregistrements disponibles"""
        if not os.path.exists(self.recordings_dir):
            return []
        
        recordings = []
        for filename in os.listdir(self.recordings_dir):
            if filename.endswith('.wav'):
                file_path = os.path.join(self.recordings_dir, filename)
                recordings.append({
                    'filename': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'modified': os.path.getmtime(file_path)
                })
        
        # Trier par date de modification (plus récent en premier)
        recordings.sort(key=lambda x: x['modified'], reverse=True)
        return recordings
    
    def delete_recording(self, file_path):
        """Supprime un enregistrement"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Recording deleted: {os.path.basename(file_path)}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error deleting recording: {e}")
            return False
    
    def cleanup(self):
        """Nettoie les ressources"""
        self.is_recording = False
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None
        
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
            except:
                pass
            self.pyaudio_instance = None
        
        print("🧹 AudioService cleanup completed")
    
    def __del__(self):
        """Destructeur pour nettoyer automatiquement"""
        self.cleanup()


class AIChatView:
    def __init__(self, app):
        self.app = app
        self.conversation_history = []
        self.recording = False
        # Use the shared services from the app
        self.ai_service = app.ai_service
        self.audio_service = app.audio_service
        
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
        if self.audio_service.start_recording():
            self.recording_status.text = "🔴 Enregistrement en cours..."
            self.recording = True
            # Update button states or interface as needed
        else:
            # Use the new dialog method instead of deprecated info_dialog
            self.app.main_window.dialog(toga.InfoDialog(
                "Erreur Audio", 
                "Impossible de démarrer l'enregistrement. Vérifiez votre microphone."
            ))
    
    def stop_recording(self, widget):
        """Stop audio recording"""
        if self.recording:
            file_path = self.audio_service.stop_recording()
            self.recording = False
            
            if file_path:
                self.recording_status.text = f"⏹️ Enregistrement sauvé: {os.path.basename(file_path)}"
                # TODO: Add speech-to-text conversion here
                # For now, just notify the user
                self.app.main_window.dialog(toga.InfoDialog(
                    "Enregistrement", 
                    f"Audio sauvé: {os.path.basename(file_path)}\n\nLa conversion parole-texte sera implémentée prochainement."
                ))
            else:
                self.recording_status.text = "❌ Erreur lors de l'enregistrement"
        else:
            self.recording_status.text = "⚠️ Aucun enregistrement en cours"
    
    def play_recording(self, widget):
        """Play the last recording"""
        if self.audio_service.play_audio():
            self.recording_status.text = "▶️ Lecture en cours..."
        else:
            self.app.main_window.dialog(toga.InfoDialog(
                "Erreur", 
                "Aucun enregistrement à lire ou erreur de lecture"
            ))
    
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
