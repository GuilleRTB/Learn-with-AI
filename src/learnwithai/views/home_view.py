"""
Home page view for LearnwithAI
"""

import toga
from toga.style.pack import COLUMN, ROW, Pack


class HomeView:
    def __init__(self, app):
        self.app = app
        
    def create_view(self):
        """Create the home page with navigation options"""
        # Title
        title = toga.Label(
            "Learn with AI",
            style=Pack(
                text_align="center",
                font_size=24,
                font_weight="bold",
                padding_top=50,
                padding_bottom=30
            )
        )
        
        # Description
        description = toga.Label(
            "Choisissez votre mode d'apprentissage",
            style=Pack(
                text_align="center",
                font_size=16,
                padding_bottom=40
            )
        )
        
        # Course button
        course_button = toga.Button(
            "📚 Cours",
            on_press=self.open_courses,
            style=Pack(
                padding=20,
                width=200,
                font_size=16
            )
        )
        
        # AI Chat button
        ai_chat_button = toga.Button(
            "🤖 Talk with AI",
            on_press=self.open_ai_chat,
            style=Pack(
                padding=20,
                width=200,
                font_size=16
            )
        )
        
        # Settings button
        settings_button = toga.Button(
            "⚙️ Settings",
            on_press=self.open_settings,
            style=Pack(
                padding=20,
                width=200,
                font_size=16
            )
        )
        
        # Button container
        button_box = toga.Box(
            children=[course_button, ai_chat_button, settings_button],
            style=Pack(
                direction=COLUMN,
                alignment="center",
                padding=20
            )
        )
        
        # Main container
        main_box = toga.Box(
            children=[title, description, button_box],
            style=Pack(
                direction=COLUMN,
                alignment="center",
                padding=20
            )
        )
        
        return main_box
    
    def open_courses(self, widget):
        """Navigate to courses view"""
        from .courses_view import CoursesView
        courses_view = CoursesView(self.app)
        self.app.main_window.content = courses_view.create_view()
        
    def open_ai_chat(self, widget):
        """Navigate to AI chat view"""
        from .ai_chat_view import AIChatView
        ai_chat_view = AIChatView(self.app)
        self.app.main_window.content = ai_chat_view.create_view()
        
    def open_settings(self, widget):
        """Navigate to settings view"""
        from .settings_view import SettingsView
        settings_view = SettingsView(self.app)
        self.app.main_window.content = settings_view.create_view()