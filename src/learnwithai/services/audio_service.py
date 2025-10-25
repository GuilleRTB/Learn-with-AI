"""
Audio recording and playback service for LearnwithAI
"""

import os
import wave
import threading
import time
from datetime import datetime

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("PyAudio not available. Install with: pip install pyaudio")

class AudioService:
    def __init__(self):
        """Initialize audio service"""
        self.is_recording = False
        self.current_recording = None
        self.audio = None
        self.stream = None
        self.frames = []
        self.recording_thread = None
        self.recording_start_time = None
        
        # Audio configuration
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None  # 16 bits per sample
        self.channels = 2
        self.fs = 44100  # Record at 44100 samples per second
        
        # Create recordings directory
        self.recordings_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'recordings')
        os.makedirs(self.recordings_dir, exist_ok=True)
        
        # Initialize PyAudio
        self._initialize_audio()
        
    def _initialize_audio(self):
        """Initialize PyAudio"""
        if not PYAUDIO_AVAILABLE:
            print("❌ PyAudio not available. Audio recording disabled.")
            return
            
        try:
            self.audio = pyaudio.PyAudio()
            print("✅ Audio service initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing audio: {e}")
            self.audio = None
            
    def start_recording(self):
        """Start recording audio from microphone"""
        if not PYAUDIO_AVAILABLE or not self.audio:
            print("❌ Audio recording not available")
            return False
            
        if self.is_recording:
            print("⚠️ Already recording")
            return False
            
        try:
            # Start recording
            self.stream = self.audio.open(
                format=self.sample_format,
                channels=self.channels,
                rate=self.fs,
                frames_per_buffer=self.chunk,
                input=True
            )
            
            self.frames = []
            self.is_recording = True
            self.recording_start_time = time.time()
            
            # Start recording thread
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            print("🎤 Recording started...")
            return True
            
        except Exception as e:
            print(f"❌ Error starting recording: {e}")
            self.is_recording = False
            return False
        
    def _record_audio(self):
        """Internal method to record audio in a separate thread"""
        try:
            while self.is_recording:
                data = self.stream.read(self.chunk)
                self.frames.append(data)
        except Exception as e:
            print(f"❌ Error during recording: {e}")
            self.is_recording = False
        
    def stop_recording(self):
        """Stop recording and save file"""
        if not self.is_recording:
            print("⚠️ Not currently recording")
            return None
            
        try:
            self.is_recording = False
            
            # Wait for recording thread to finish
            if self.recording_thread:
                self.recording_thread.join(timeout=1.0)
            
            # Stop and close the stream
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"
            file_path = os.path.join(self.recordings_dir, filename)
            
            # Save the recorded data as a WAV file
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.sample_format))
                wf.setframerate(self.fs)
                wf.writeframes(b''.join(self.frames))
            
            self.current_recording = file_path
            print(f"⏹️ Recording stopped and saved: {filename}")
            return file_path
            
        except Exception as e:
            print(f"❌ Error stopping recording: {e}")
            return None
    
    def play_audio(self, file_path=None):
        """Play audio file"""
        if not PYAUDIO_AVAILABLE or not self.audio:
            print("❌ Audio playback not available")
            return False
            
        # Use current recording if no file specified
        if file_path is None:
            file_path = self.current_recording
            
        if not file_path or not os.path.exists(file_path):
            print("❌ Audio file not found")
            return False
            
        try:
            # Open the audio file
            with wave.open(file_path, 'rb') as wf:
                # Create a stream for playback
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                print(f"▶️ Playing audio: {os.path.basename(file_path)}")
                
                # Read and play the audio data
                data = wf.readframes(self.chunk)
                while data:
                    stream.write(data)
                    data = wf.readframes(self.chunk)
                
                # Stop and close the stream
                stream.stop_stream()
                stream.close()
                
                print("✅ Playback finished")
                return True
                
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
            return False
        
    def get_recording_status(self):
        """Get current recording status"""
        duration = 0
        if self.is_recording and self.recording_start_time:
            duration = time.time() - self.recording_start_time
            
        return {
            'is_recording': self.is_recording,
            'duration': round(duration, 1),
            'current_file': self.current_recording,
            'recordings_dir': self.recordings_dir
        }
    
    def list_recordings(self):
        """List all saved recordings"""
        if not os.path.exists(self.recordings_dir):
            return []
            
        recordings = []
        for filename in os.listdir(self.recordings_dir):
            if filename.endswith('.wav'):
                file_path = os.path.join(self.recordings_dir, filename)
                file_info = {
                    'filename': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'modified': os.path.getmtime(file_path)
                }
                recordings.append(file_info)
        
        # Sort by modification time (newest first)
        recordings.sort(key=lambda x: x['modified'], reverse=True)
        return recordings
    
    def delete_recording(self, file_path):
        """Delete a recording file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                if self.current_recording == file_path:
                    self.current_recording = None
                print(f"🗑️ Recording deleted: {os.path.basename(file_path)}")
                return True
            else:
                print("❌ File not found")
                return False
        except Exception as e:
            print(f"❌ Error deleting file: {e}")
            return False
    
    def cleanup(self):
        """Clean up audio resources"""
        try:
            if self.is_recording:
                self.stop_recording()
                
            if self.stream:
                self.stream.close()
                
            if self.audio:
                self.audio.terminate()
                
            print("🧹 Audio service cleaned up")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
    
    def get_available_devices(self):
        """Get list of available audio devices"""
        if not PYAUDIO_AVAILABLE or not self.audio:
            return []
            
        devices = []
        info = self.audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        
        for i in range(0, numdevices):
            device_info = self.audio.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                devices.append({
                    'index': i,
                    'name': device_info.get('name'),
                    'channels': device_info.get('maxInputChannels'),
                    'sample_rate': device_info.get('defaultSampleRate')
                })
        
        return devices