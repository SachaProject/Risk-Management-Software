"""Styles et thèmes pour l'application"""

class AppStyles:
    """Styles globaux de l'application"""
    
    # Couleurs du thème sombre
    PRIMARY_BG = "#1e1e1e"
    SECONDARY_BG = "#2d2d30"
    TERTIARY_BG = "#3e3e42"
    ACCENT = "#007ACC"
    ACCENT_HOVER = "#1e8ad6"
    SUCCESS = "#4CAF50"
    WARNING = "#FFC107"
    DANGER = "#F44336"
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#CCCCCC"
    BORDER = "#555555"
    
    # Styles des widgets
    MAIN_STYLE = f"""
    QMainWindow {{
        background-color: {PRIMARY_BG};
    }}
    
    QWidget {{
        background-color: {PRIMARY_BG};
        color: {TEXT_PRIMARY};
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 12px;
    }}
    
    QTabWidget::pane {{
        border: 1px solid {BORDER};
        background-color: {SECONDARY_BG};
        border-radius: 4px;
    }}
    
    QTabBar::tab {{
        background-color: {TERTIARY_BG};
        color: {TEXT_SECONDARY};
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {ACCENT};
        color: {TEXT_PRIMARY};
    }}
    
    QTabBar::tab:hover {{
        background-color: {ACCENT_HOVER};
    }}
    
    QPushButton {{
        background-color: {ACCENT};
        color: {TEXT_PRIMARY};
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: 500;
    }}
    
    QPushButton:hover {{
        background-color: {ACCENT_HOVER};
    }}
    
    QPushButton:pressed {{
        background-color: {TERTIARY_BG};
    }}
    
    QPushButton:disabled {{
        background-color: {TERTIARY_BG};
        color: {TEXT_SECONDARY};
    }}
    
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: {TERTIARY_BG};
        border: 1px solid {BORDER};
        padding: 6px;
        border-radius: 4px;
        color: {TEXT_PRIMARY};
    }}
    
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
        border: 1px solid {ACCENT};
    }}
    
    QTableWidget {{
        background-color: {SECONDARY_BG};
        alternate-background-color: {TERTIARY_BG};
        gridline-color: {BORDER};
        border: 1px solid {BORDER};
        border-radius: 4px;
    }}
    
    QTableWidget::item {{
        padding: 4px;
    }}
    
    QTableWidget::item:selected {{
        background-color: {ACCENT};
    }}
    
    QHeaderView::section {{
        background-color: {TERTIARY_BG};
        color: {TEXT_PRIMARY};
        padding: 8px;
        border: none;
        font-weight: 600;
    }}
    
    QScrollBar:vertical {{
        background-color: {SECONDARY_BG};
        width: 12px;
        border: none;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {TERTIARY_BG};
        min-height: 20px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {ACCENT};
    }}
    
    QScrollBar:horizontal {{
        background-color: {SECONDARY_BG};
        height: 12px;
        border: none;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {TERTIARY_BG};
        min-width: 20px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {ACCENT};
    }}
    
    QGroupBox {{
        border: 1px solid {BORDER};
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
        font-weight: 600;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
        color: {ACCENT};
    }}
    
    QLabel {{
        color: {TEXT_PRIMARY};
    }}
    
    QCheckBox {{
        color: {TEXT_PRIMARY};
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 2px;
        border: 1px solid {BORDER};
        background-color: {TERTIARY_BG};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {ACCENT};
        border-color: {ACCENT};
    }}
    
    QProgressBar {{
        border: 1px solid {BORDER};
        border-radius: 4px;
        text-align: center;
        background-color: {TERTIARY_BG};
    }}
    
    QProgressBar::chunk {{
        background-color: {ACCENT};
        border-radius: 3px;
    }}
    
    QMenuBar {{
        background-color: {SECONDARY_BG};
        color: {TEXT_PRIMARY};
    }}
    
    QMenuBar::item:selected {{
        background-color: {ACCENT};
    }}
    
    QMenu {{
        background-color: {SECONDARY_BG};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
    }}
    
    QMenu::item:selected {{
        background-color: {ACCENT};
    }}
    
    QStatusBar {{
        background-color: {SECONDARY_BG};
        color: {TEXT_SECONDARY};
        border-top: 1px solid {BORDER};
    }}
    
    QSplitter::handle {{
        background-color: {BORDER};
        width: 2px;
    }}
    
    QTextEdit, QPlainTextEdit {{
        background-color: {TERTIARY_BG};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 8px;
        color: {TEXT_PRIMARY};
    }}
    
    QSlider::groove:horizontal {{
        background-color: {TERTIARY_BG};
        height: 6px;
        border-radius: 3px;
    }}
    
    QSlider::handle:horizontal {{
        background-color: {ACCENT};
        width: 16px;
        height: 16px;
        border-radius: 8px;
        margin: -5px 0;
    }}
    
    QSlider::handle:horizontal:hover {{
        background-color: {ACCENT_HOVER};
    }}
    
    QToolTip {{
        background-color: {TERTIARY_BG};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        padding: 4px;
        border-radius: 2px;
    }}
    """
    
    @staticmethod
    def get_button_style(style_type="primary"):
        """Retourne le style pour un bouton spécifique"""
        if style_type == "primary":
            return f"""
            QPushButton {{
                background-color: {AppStyles.ACCENT};
                color: {AppStyles.TEXT_PRIMARY};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {AppStyles.ACCENT_HOVER};
            }}
            """
        elif style_type == "success":
            return f"""
            QPushButton {{
                background-color: {AppStyles.SUCCESS};
                color: {AppStyles.TEXT_PRIMARY};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
            """
        elif style_type == "danger":
            return f"""
            QPushButton {{
                background-color: {AppStyles.DANGER};
                color: {AppStyles.TEXT_PRIMARY};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #da190b;
            }}
            """
        else:
            return f"""
            QPushButton {{
                background-color: {AppStyles.TERTIARY_BG};
                color: {AppStyles.TEXT_PRIMARY};
                border: 1px solid {AppStyles.BORDER};
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {AppStyles.SECONDARY_BG};
            }}
            """
    
    @staticmethod
    def get_table_style():
        """Retourne le style pour les tableaux"""
        return f"""
        QTableWidget {{
            background-color: {AppStyles.SECONDARY_BG};
            alternate-background-color: {AppStyles.TERTIARY_BG};
            gridline-color: {AppStyles.BORDER};
            border: 1px solid {AppStyles.BORDER};
            border-radius: 4px;
            selection-background-color: {AppStyles.ACCENT};
        }}
        
        QTableWidget::item {{
            padding: 6px;
        }}
        
        QHeaderView::section {{
            background-color: {AppStyles.TERTIARY_BG};
            color: {AppStyles.TEXT_PRIMARY};
            padding: 8px;
            border: none;
            font-weight: 600;
        }}
        """
    
    @staticmethod
    def get_card_style():
        """Retourne le style pour les cartes/panels"""
        return f"""
        QFrame {{
            background-color: {AppStyles.SECONDARY_BG};
            border: 1px solid {AppStyles.BORDER};
            border-radius: 8px;
            padding: 16px;
        }}
        """