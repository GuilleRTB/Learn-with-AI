"""
Settings page view for LearnwithAI
"""

import toga
import json
import os
from toga.style.pack import COLUMN, ROW, Pack


class SettingsView:
    def __init__(self, app):
        self.app = app
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'settings.json')
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Load settings from JSON file"""
        # Create default settings
        default_settings = {
            "level": "Beginner",
            "focus": "Conversation"
        }
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        
        # Try to load existing settings
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            else:
                # Create file with default settings
                with open(self.settings_file, 'w') as f:
                    json.dump(default_settings, f, indent=4)
                return default_settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings
        
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print(f"✅ Settings saved to {self.settings_file}")
        except Exception as e:
            print(f"❌ Error saving settings: {e}")
            self.app.main_window.info_dialog(
                "Error",
                f"Could not save settings: {e}"
            )
    
    def create_view(self):
        """Create the settings page"""
        # Title
        title = toga.Label(
            "Settings",
            style=Pack(
                text_align="center",
                font_size=24,
                font_weight="bold",
                padding_top=20,
                padding_bottom=20
            )
        )
        
        # Level selection
        level_label = toga.Label(
            "Your English Level:",
            style=Pack(
                text_align="left",
                font_size=16,
                padding_bottom=10,
                padding_top=10
            )
        )
        
        self.level_selection = toga.Selection(
            items=["Beginner", "Intermediate", "Advanced"],
            style=Pack(width=200, padding=5),
            on_change=self.on_level_change
        )
        
        # Set initial selection from saved settings
        self.level_selection.value = self.settings.get("level", "Beginner")
        
        level_box = toga.Box(
            children=[level_label, self.level_selection],
            style=Pack(
                direction=COLUMN,
                padding=10
            )
        )
        
        # Focus selection
        focus_label = toga.Label(
            "What would you like to improve:",
            style=Pack(
                text_align="left",
                font_size=16,
                padding_bottom=10,
                padding_top=10
            )
        )
        
        self.focus_selection = toga.Selection(
            items=["School", "Conversation", "Travel", "Business", "Job Interview"],
            style=Pack(width=200, padding=5),
            on_change=self.on_focus_change
        )
        
        # Set initial selection from saved settings
        self.focus_selection.value = self.settings.get("focus", "Conversation")
        
        focus_box = toga.Box(
            children=[focus_label, self.focus_selection],
            style=Pack(
                direction=COLUMN,
                padding=10
            )
        )
        
        # Save button
        save_button = toga.Button(
            "Save Settings",
            on_press=self.save_and_go_back,
            style=Pack(
                padding=10,
                width=150,
                font_size=14
            )
        )
        
        # Cancel button
        cancel_button = toga.Button(
            "Cancel",
            on_press=self.go_back,
            style=Pack(
                padding=10,
                width=150,
                font_size=14
            )
        )
        
        # Button container
        button_box = toga.Box(
            children=[save_button, cancel_button],
            style=Pack(
                direction=ROW,
                alignment="center",
                padding=20
            )
        )
        
        # Main container
        main_box = toga.Box(
            children=[title, level_box, focus_box, button_box],
            style=Pack(
                direction=COLUMN,
                alignment="center",
                padding=20
            )
        )
        
        return main_box
    
    def on_level_change(self, widget):
        """Handle level selection change"""
        self.settings["level"] = self.level_selection.value
        
    def on_focus_change(self, widget):
        """Handle focus selection change"""
        self.settings["focus"] = self.focus_selection.value
        
    def save_and_go_back(self, widget):
        """Save settings and return to home view"""
        self.save_settings()
        
        # Notify AI Service to refresh settings if it exists in the app
        if hasattr(self.app, 'ai_service'):
            self.app.ai_service.refresh_settings()
            prompt_info = self.app.ai_service.get_current_prompt_info()
            prompt_type = prompt_info.get('type', 'default')
            message = f"Your settings have been saved.\nLevel: {self.settings['level']}\nFocus: {self.settings['focus']}\nPrompt type: {prompt_type}"
        else:
            message = f"Your settings have been saved.\nLevel: {self.settings['level']}\nFocus: {self.settings['focus']}"
        
        self.app.main_window.info_dialog(
            "Settings Saved",
            message
        )
        self.go_back(widget)
        
    def go_back(self, widget):
        """Return to home view"""
        from .home_view import HomeView
        home_view = HomeView(self.app)
        self.app.main_window.content = home_view.create_view()