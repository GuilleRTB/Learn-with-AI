"""
Learn with AI - Application pour apprendre l'anglais
"""

import toga
from toga.style.pack import COLUMN, ROW
from .views.home_view import HomeView
from .services.ai_service import AIChatService


class LearnwithAI(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Initialize the app with the home view containing navigation options.
        """
        # Initialize AI service (shared across all views)
        self.ai_service = AIChatService()
        
        # Create the home view
        home_view = HomeView(self)
        main_box = home_view.create_view()

        # Create and show the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()


def main():
    return LearnwithAI()
