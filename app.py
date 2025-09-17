#!/usr/bin/env python3
"""
Quant Finance Platform - Omega Ratio Trading System
Application principale avec architecture MVC
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor

# Ajouter le répertoire racine au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.main_window import MainWindow
from views.styles import AppStyles


class QuantFinanceApp(QApplication):
    """Application principale"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Quant Finance Platform")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Trading Analytics")
        
        # Configuration de l'application
        self.setup_application()
        
        # Créer la fenêtre principale
        self.main_window = MainWindow()
        
    def setup_application(self):
        """Configure l'application"""
        # Style Fusion pour un look moderne
        self.setStyle('Fusion')
        
        # Appliquer le thème sombre
        self.apply_dark_theme()
        
        # Les attributs DPI sont déjà configurés dans main()
        
    def apply_dark_theme(self):
        """Applique le thème sombre"""
        dark_palette = QPalette()
        
        # Couleurs principales
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(45, 45, 48))
        dark_palette.setColor(QPalette.AlternateBase, QColor(60, 63, 65))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        
        self.setPalette(dark_palette)
        
        # Appliquer les styles CSS personnalisés
        self.setStyleSheet(AppStyles.MAIN_STYLE)
        
    def run(self):
        """Lance l'application"""
        self.main_window.show()
        return self.exec_()


def main():
    """Point d'entrée principal"""
    try:
        # Configuration pour les écrans haute résolution
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            
        # Créer et lancer l'application
        app = QuantFinanceApp(sys.argv)
        
        print("🚀 Démarrage de la Quant Finance Platform...")
        print("📊 Architecture MVC initialisée")
        print("💼 Prêt pour l'analyse de vos stratégies de trading")
        
        return app.run()
        
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())