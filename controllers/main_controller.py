from PyQt5.QtCore import QObject, pyqtSignal
from .data_controller import DataController
from .portfolio_controller import PortfolioController
from .analysis_controller import AnalysisController
import json
import os
from typing import Dict, Any


class MainController(QObject):
    """Contrôleur principal qui coordonne tous les autres contrôleurs"""
    
    # Signaux globaux
    status_message = pyqtSignal(str)
    error_message = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    app_ready = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Initialiser les sous-contrôleurs
        self.data_controller = DataController()
        self.portfolio_controller = PortfolioController()
        self.analysis_controller = AnalysisController()
        
        # Configuration de l'application
        self.config = self._load_config()
        
        # Connecter les signaux
        self._connect_signals()
        
        # État de l'application
        self.current_state = {
            'active_tab': 'data',
            'loaded_files': [],
            'portfolio_name': None,
        }
        
    def _load_config(self) -> Dict:
        """Charge la configuration de l'application"""
        config_path = "config.json"
        default_config = {
            'initial_capital': 100000,
            'default_allocation_method': 'equal_weight',
            'risk_free_rate': 0.02,
            'target_volatility': 0.15,
            'rebalance_frequency': 'monthly',
            'data_directory': '/mnt/c/Users/sacha/Desktop/Trading/Omega ratio',
            'auto_save': True,
            'theme': 'dark'
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                self.error_message.emit(f"Erreur chargement config: {str(e)}")
                
        return default_config
        
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            with open("config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
            self.status_message.emit("Configuration sauvegardée")
        except Exception as e:
            self.error_message.emit(f"Erreur sauvegarde config: {str(e)}")
            
    def _connect_signals(self):
        """Connecte les signaux entre contrôleurs"""
        
        # Data Controller
        self.data_controller.data_loaded.connect(self._on_data_loaded)
        self.data_controller.data_error.connect(self.error_message.emit)
        self.data_controller.progress_update.connect(self.progress_update.emit)
        self.data_controller.data_cleared.connect(self._on_data_cleared)
        self.data_controller.file_removed.connect(self._on_file_removed)
        
        # Portfolio Controller
        self.portfolio_controller.portfolio_updated.connect(self._on_portfolio_updated)
        self.portfolio_controller.optimization_complete.connect(self._on_optimization_complete)
        
        
        # Analysis Controller
        self.analysis_controller.analysis_completed.connect(self._on_analysis_complete)
        
    def initialize_app(self):
        """Initialise l'application"""
        self.status_message.emit("Initialisation de l'application...")
        
        # Initialiser le portfolio avec le capital par défaut
        self.portfolio_controller.initialize_portfolio(
            "Portfolio Principal",
            self.config['initial_capital']
        )
        
        # Scanner le répertoire de données
        csv_files = self.data_controller.scan_directory(self.config['data_directory'])
        if csv_files:
            self.status_message.emit(f"{len(csv_files)} fichiers CSV trouvés")
            
        self.app_ready.emit()
        
    def load_data_files(self, file_paths: list):
        """Charge plusieurs fichiers de données"""
        self.status_message.emit(f"Chargement de {len(file_paths)} fichiers...")
        loaded = self.data_controller.load_multiple_csv(file_paths)
        
        if loaded > 0:
            self.current_state['loaded_files'] = self.data_controller.get_loaded_files()
            
            # Ajouter les stratégies au portfolio
            for file_name in self.current_state['loaded_files']:
                strategy = self.data_controller.get_strategy_model(file_name)
                if strategy:
                    self.portfolio_controller.add_strategy_to_portfolio(file_name, strategy)
                    
            self.status_message.emit(f"{loaded} fichiers chargés avec succès")
            
    def _on_data_loaded(self, file_name: str):
        """Gère le chargement d'un fichier"""
        self.status_message.emit(f"Fichier chargé: {file_name}")
        
        # Mettre à jour l'état
        if file_name not in self.current_state['loaded_files']:
            self.current_state['loaded_files'].append(file_name)
            
    def _on_portfolio_updated(self):
        """Gère la mise à jour du portfolio"""
        summary = self.portfolio_controller.get_portfolio_summary()
        self.status_message.emit(f"Portfolio mis à jour: {summary['num_trades']} trades")
        
    def _on_optimization_complete(self, result: Dict):
        """Gère la fin d'une optimisation"""
        method = result.get('method', 'unknown')
        self.status_message.emit(f"Optimisation {method} terminée")
        
        
    def _on_analysis_complete(self, metrics: Dict):
        """Gère la fin d'une analyse"""
        omega = metrics.get('omega_ratios', {}).get('omega_0', 0)
        self.status_message.emit(f"Analyse terminée - Omega Ratio: {omega:.2f}")
        
    def _on_data_cleared(self):
        """Gère l'effacement de toutes les données"""
        # Vider aussi le portfolio
        for strategy_name in list(self.portfolio_controller.portfolio.strategies.keys()):
            self.portfolio_controller.remove_strategy_from_portfolio(strategy_name)
        self.current_state['loaded_files'].clear()
        self.status_message.emit("Toutes les données ont été effacées")
        
    def _on_file_removed(self, file_name: str):
        """Gère la suppression d'un fichier spécifique"""
        # Retirer la stratégie correspondante du portfolio
        if file_name in self.portfolio_controller.portfolio.strategies:
            self.portfolio_controller.remove_strategy_from_portfolio(file_name)
        if file_name in self.current_state['loaded_files']:
            self.current_state['loaded_files'].remove(file_name)
        self.status_message.emit(f"Fichier supprimé: {file_name}")
        
    def run_full_analysis(self):
        """Lance une analyse complète"""
        self.status_message.emit("Démarrage de l'analyse complète...")
        
        # 1. Calculer les métriques du portfolio
        portfolio_metrics = self.portfolio_controller.calculate_portfolio_metrics()
        
        # 2. Analyser les corrélations
        correlation_matrix = self.portfolio_controller.calculate_correlation_matrix()
        
        # 3. Effectuer l'analyse de risque
        risk_analysis = self.portfolio_controller.perform_risk_analysis()
        
        # 4. Calculer les métriques avancées
        portfolio_returns = self.portfolio_controller.portfolio.calculate_portfolio_returns()
        if len(portfolio_returns) > 0:
            advanced_metrics = self.analysis_controller.calculate_comprehensive_metrics(portfolio_returns)
            
        self.status_message.emit("Analyse complète terminée")
        
    def optimize_portfolio(self, method: str = None):
        """Optimise le portfolio"""
        if method is None:
            method = self.config['default_allocation_method']
            
        self.status_message.emit(f"Optimisation du portfolio: {method}")
        self.portfolio_controller.optimize_portfolio(method)
        
        
    def export_results(self, file_path: str):
        """Exporte tous les résultats"""
        self.status_message.emit("Export des résultats...")
        
        try:
            # Export des données
            self.data_controller.export_analysis(
                file_path.replace('.xlsx', '_data.xlsx')
            )
            
            # Export du portfolio
            self.portfolio_controller.save_portfolio(
                file_path.replace('.xlsx', '_portfolio.json')
            )
            
            self.status_message.emit("Export terminé")
        except Exception as e:
            self.error_message.emit(f"Erreur export: {str(e)}")
            
    def set_current_tab(self, tab_name: str):
        """Change l'onglet actif"""
        self.current_state['active_tab'] = tab_name
        
    def get_app_state(self) -> Dict:
        """Retourne l'état de l'application"""
        return {
            'config': self.config,
            'state': self.current_state,
            'loaded_files': self.data_controller.get_loaded_files(),
            'portfolio_summary': self.portfolio_controller.get_portfolio_summary()
        }
        
    def cleanup(self):
        """Nettoie les ressources avant fermeture"""
        if self.config['auto_save']:
            self.save_config()
            
        self.status_message.emit("Fermeture de l'application...")