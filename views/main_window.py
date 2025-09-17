import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTabWidget, QMenuBar, QMenu, QAction, QStatusBar,
                            QMessageBox, QFileDialog, QSplitter, QDockWidget)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence

from .styles import AppStyles
from .data_view import DataView
from .portfolio_view import PortfolioView
from .analysis_view import AnalysisView
from .overfitting_view import OverfittingView
from controllers.main_controller import MainController


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        self.controller = MainController()
        self.init_ui()
        self.connect_signals()
        self.controller.initialize_app()
        
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("Quant Finance Platform - Omega Ratio Trading System")
        self.setGeometry(100, 100, 1600, 900)
        
        # Appliquer le style
        self.setStyleSheet(AppStyles.MAIN_STYLE)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Menu supprimé - Plus besoin avec les onglets
        
        # Créer les onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # Créer les vues
        self.data_view = DataView(self.controller.data_controller)
        self.portfolio_view = PortfolioView(self.controller.portfolio_controller)
        self.analysis_view = AnalysisView(self.controller.analysis_controller)
        self.overfitting_view = OverfittingView()
        
        # Configurer les références croisées
        self.portfolio_view.set_main_window(self)
        
        # Ajouter les onglets
        self.tab_widget.addTab(self.data_view, "📊 Données")
        self.tab_widget.addTab(self.portfolio_view, "💼 Portfolio & Formules")
        self.tab_widget.addTab(self.analysis_view, "📈 Analyse")
        self.tab_widget.addTab(self.overfitting_view, "🔍 Détection Overfitting")
        
        # Ajouter les onglets au layout principal
        main_layout.addWidget(self.tab_widget)
        
        # Créer la barre de statut
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt")
        
        # Timer pour les mises à jour périodiques
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(5000)  # Mise à jour toutes les 5 secondes
        
    # Méthode supprimée - plus de barre de menu
        
    def connect_signals(self):
        """Connecte les signaux du contrôleur"""
        self.controller.status_message.connect(self.update_status_message)
        self.controller.error_message.connect(self.show_error)
        self.controller.progress_update.connect(self.update_progress)
        self.controller.app_ready.connect(self.on_app_ready)
        
        # Connecter le changement d'onglet
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        
    def open_files(self):
        """Ouvre une boîte de dialogue pour sélectionner des fichiers CSV"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Sélectionner des fichiers CSV",
            self.controller.config['data_directory'],
            "Fichiers CSV (*.csv)"
        )
        
        if files:
            self.controller.load_data_files(files)
            self.data_view.refresh_data()
            self.update_strategies_in_views()
            
    def save_portfolio(self):
        """Sauvegarde le portfolio"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder Portfolio",
            "",
            "Fichiers JSON (*.json)"
        )
        
        if file_path:
            self.controller.portfolio_controller.save_portfolio(file_path)
            self.update_status_message("Portfolio sauvegardé")
            
    def export_results(self):
        """Exporte les résultats"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter Résultats",
            "",
            "Fichiers Excel (*.xlsx)"
        )
        
        if file_path:
            self.controller.export_results(file_path)
            
    def optimize_portfolio(self):
        """Lance l'optimisation du portfolio"""
        self.portfolio_view.optimize_portfolio()
        
    def rebalance_portfolio(self):
        """Rééquilibre le portfolio"""
        self.controller.portfolio_controller.execute_rebalance()
        self.portfolio_view.update_view()
        
    def run_full_analysis(self):
        """Lance une analyse complète"""
        self.controller.run_full_analysis()
        self.analysis_view.update_view()
        self.tab_widget.setCurrentIndex(3)  # Passer à l'onglet Analyse
        
    def calculate_omega(self):
        """Calcule le ratio Omega"""
        portfolio_returns = self.controller.portfolio_controller.portfolio.calculate_portfolio_returns()
        if len(portfolio_returns) > 0:
            omega = self.controller.analysis_controller.calculate_omega_ratio(portfolio_returns)
            QMessageBox.information(
                self,
                "Omega Ratio",
                f"Le ratio Omega du portfolio est: {omega:.4f}"
            )
            
    def show_documentation(self):
        """Affiche la documentation"""
        QMessageBox.information(
            self,
            "Documentation",
            "Documentation de la plateforme Quant Finance\n\n"
            "Cette plateforme permet:\n"
            "- Le chargement et l'analyse de données de trading\n"
            "- La gestion de portfolios multi-stratégies\n"
            "- Le backtesting de stratégies\n"
            "- L'analyse quantitative avancée avec Omega Ratio\n"
            "- L'optimisation d'allocations\n\n"
            "Pour plus d'informations, consultez le guide utilisateur."
        )
        
    def show_about(self):
        """Affiche la boîte de dialogue À propos"""
        QMessageBox.about(
            self,
            "À propos",
            "Quant Finance Platform v1.0\n\n"
            "Plateforme d'analyse quantitative pour le trading\n"
            "Spécialisée dans le calcul du ratio Omega\n\n"
            "Développée avec Python, PyQt5 et pandas\n"
            "Architecture MVC pour une maintenance optimale"
        )
        
    def on_tab_changed(self, index):
        """Gère le changement d'onglet"""
        tabs = ["data", "portfolio", "analysis", "overfitting"]
        if 0 <= index < len(tabs):
            self.controller.set_current_tab(tabs[index])

            # Rafraîchir la vue si nécessaire
            if index == 1:  # Portfolio
                self.portfolio_view.update_view()
                self.update_strategies_in_views()
            elif index == 2:  # Analyse
                self.analysis_view.update_view()
            elif index == 3:  # Overfitting Detection
                self.update_strategies_in_views()  # S'assurer que les données sont à jour
                self.overfitting_view.analyze_current_formula()
                
    def update_strategies_in_views(self):
        """Met à jour les stratégies dans toutes les vues"""
        try:
            # Récupérer les stratégies du contrôleur de données
            strategies_data = {}
            
            for name, strategy_model in self.controller.data_controller.strategy_models.items():
                if strategy_model and hasattr(strategy_model, 'metrics'):
                    strategies_data[name] = {
                        'sharpe': strategy_model.metrics.get('sharpe_ratio', 0),
                        'omega': strategy_model.metrics.get('omega_ratio', 0),
                        'win_rate': strategy_model.metrics.get('win_rate', 0),
                        'volatility': strategy_model.metrics.get('volatility', 0),
                        'drawdown': strategy_model.metrics.get('max_drawdown', 0),
                        'total_return': strategy_model.metrics.get('total_return', 0)
                    }
                    
            
            # Mettre à jour le portfolio
            for name, strategy in self.controller.data_controller.strategy_models.items():
                if strategy and name not in self.controller.portfolio_controller.portfolio.strategies:
                    self.controller.portfolio_controller.add_strategy_to_portfolio(name, strategy, 0.0)
                    
        except Exception as e:
            print(f"Erreur mise à jour stratégies: {e}")
                
    def on_app_ready(self):
        """Appelé quand l'application est prête"""
        self.update_status_message("Application prête")
        
        # Charger automatiquement les fichiers CSV du répertoire
        csv_files = self.controller.data_controller.scan_directory()
        if csv_files:
            reply = QMessageBox.question(
                self,
                "Charger les données",
                f"{len(csv_files)} fichiers CSV trouvés. Voulez-vous les charger?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.controller.load_data_files(csv_files)
                
    def update_status(self):
        """Met à jour périodiquement le statut"""
        state = self.controller.get_app_state()
        num_files = len(state['loaded_files'])
        portfolio_value = state['portfolio_summary'].get('current_capital', 0)
        
        status_text = f"Fichiers: {num_files} | Capital: {portfolio_value:,.0f}€"
        self.status_bar.showMessage(status_text)
        
    def update_status_message(self, message):
        """Met à jour le message de statut"""
        self.status_bar.showMessage(message)
        
    def update_progress(self, value):
        """Met à jour la barre de progression"""
        # Implémentation future d'une barre de progression
        pass
        
    def show_error(self, message):
        """Affiche un message d'erreur"""
        QMessageBox.critical(self, "Erreur", message)
        
    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        reply = QMessageBox.question(
            self,
            "Confirmer la fermeture",
            "Voulez-vous vraiment quitter l'application?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.controller.cleanup()
            event.accept()
        else:
            event.ignore()