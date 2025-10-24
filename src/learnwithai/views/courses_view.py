"""
Courses view for LearnwithAI
"""

import toga
from toga.style.pack import COLUMN, ROW, Pack


class CoursesView:
    def __init__(self, app):
        self.app = app
        
    def create_view(self):
        """Create the courses page"""
        # Header with back button
        back_button = toga.Button(
            "← Retour",
            on_press=self.go_back,
            style=Pack(padding=10)
        )
        
        title = toga.Label(
            "📚 Cours d'Anglais",
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
        
        # Course categories
        beginner_button = toga.Button(
            "🌱 Débutant",
            on_press=self.open_beginner_courses,
            style=Pack(padding=10, width=200)
        )
        
        intermediate_button = toga.Button(
            "📈 Intermédiaire", 
            on_press=self.open_intermediate_courses,
            style=Pack(padding=10, width=200)
        )
        
        advanced_button = toga.Button(
            "🎓 Avancé",
            on_press=self.open_advanced_courses,
            style=Pack(padding=10, width=200)
        )
        
        # Course list container
        course_box = toga.Box(
            children=[beginner_button, intermediate_button, advanced_button],
            style=Pack(
                direction=COLUMN,
                alignment="center",
                padding=20
            )
        )
        
        # Main container
        main_box = toga.Box(
            children=[header_box, course_box],
            style=Pack(
                direction=COLUMN,
                padding=20
            )
        )
        
        return main_box
    
    def go_back(self, widget):
        """Return to home view"""
        from .home_view import HomeView
        home_view = HomeView(self.app)
        self.app.main_window.content = home_view.create_view()
        
    def open_beginner_courses(self, widget):
        """Open beginner courses"""
        # TODO: Implement beginner courses view
        self.app.main_window.info_dialog("Info", "Cours débutant - À implémenter")
        
    def open_intermediate_courses(self, widget):
        """Open intermediate courses"""
        # TODO: Implement intermediate courses view
        self.app.main_window.info_dialog("Info", "Cours intermédiaire - À implémenter")
        
    def open_advanced_courses(self, widget):
        """Open advanced courses"""
        # TODO: Implement advanced courses view
        self.app.main_window.info_dialog("Info", "Cours avancé - À implémenter")