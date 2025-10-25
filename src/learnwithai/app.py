"""
Learn with AI - Application pour apprendre l'anglais
"""

import toga
from toga.style.pack import COLUMN, ROW
from .views.home_view import HomeView
from .services.ai_service import AIChatService
from .services.audio_service import AudioService


class LearnwithAI(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Initialize the app with the home view containing navigation options.
        """
        # Initialize services (shared across all views)
        self.ai_service = AIChatService()
        self.audio_service = AudioService()
        
        # Create the home view
        home_view = HomeView(self)
        main_box = home_view.create_view()

        # Create and show the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
    
    def on_exit(self):
        """Clean up resources when the app exits"""
        try:
            if hasattr(self, 'audio_service'):
                self.audio_service.cleanup()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        return True  # Allow the app to exit


def main():
    return LearnwithAI()
