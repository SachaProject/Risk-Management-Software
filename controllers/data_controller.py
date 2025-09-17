import os
import glob
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from PyQt5.QtCore import QObject, pyqtSignal
from models.trade_model import TradeModel
from models.strategy_model import StrategyModel


class DataController(QObject):
    """Contrôleur pour la gestion des données"""
    
    # Signaux pour communiquer avec la vue
    data_loaded = pyqtSignal(str)  # Nom du fichier chargé
    data_error = pyqtSignal(str)   # Message d'erreur
    progress_update = pyqtSignal(int)  # Pourcentage de progression
    data_cleared = pyqtSignal()  # Signal quand toutes les données sont effacées
    file_removed = pyqtSignal(str)  # Signal quand un fichier est supprimé
    
    def __init__(self):
        super().__init__()
        self.trade_models: Dict[str, TradeModel] = {}
        self.strategy_models: Dict[str, StrategyModel] = {}
        self.current_data: Optional[pd.DataFrame] = None
        self.data_directory = "/mnt/c/Users/sacha/Desktop/Trading/Omega ratio"
        
    def load_csv_file(self, file_path: str) -> bool:
        """Charge un fichier CSV de trades"""
        try:
            # Créer un nouveau modèle de trades
            trade_model = TradeModel()
            success = trade_model.load_from_csv(file_path)
            
            if success:
                file_name = os.path.basename(file_path)
                self.trade_models[file_name] = trade_model
                
                # Créer un modèle de stratégie associé
                strategy = StrategyModel(file_name)
                
                # Passer les données du DataFrame à la stratégie
                if trade_model.df is not None:
                    strategy.set_data(trade_model.df)
                
                returns = trade_model.get_returns()
                if len(returns) > 0:
                    strategy.set_returns(returns)
                    self.strategy_models[file_name] = strategy
                    
                self.data_loaded.emit(file_name)
                return True
            else:
                self.data_error.emit(f"Erreur lors du chargement de {file_path}")
                return False
                
        except Exception as e:
            self.data_error.emit(f"Erreur: {str(e)}")
            return False
            
    def load_multiple_csv(self, file_paths: List[str]) -> int:
        """Charge plusieurs fichiers CSV"""
        loaded_count = 0
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths):
            if self.load_csv_file(file_path):
                loaded_count += 1
                
            # Émettre la progression
            progress = int((i + 1) / total_files * 100)
            self.progress_update.emit(progress)
            
        return loaded_count
        
    def scan_directory(self, directory: Optional[str] = None) -> List[str]:
        """Scanne un répertoire pour trouver des fichiers CSV"""
        if directory is None:
            directory = self.data_directory
            
        csv_files = glob.glob(os.path.join(directory, "*.csv"))
        return csv_files
        
    def get_combined_data(self) -> pd.DataFrame:
        """Combine toutes les données de trades chargées"""
        all_dfs = []
        
        for name, model in self.trade_models.items():
            if model.df is not None:
                df = model.df.copy()
                df['source'] = name
                all_dfs.append(df)
                
        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)
        return pd.DataFrame()
        
    def get_statistics_summary(self) -> pd.DataFrame:
        """Retourne un résumé des statistiques pour toutes les stratégies"""
        summaries = []
        
        for name, model in self.trade_models.items():
            stats = model.get_statistics()
            stats['strategy'] = name
            summaries.append(stats)
            
        if summaries:
            return pd.DataFrame(summaries)
        return pd.DataFrame()
        
    def filter_trades(self, 
                     strategy_name: Optional[str] = None,
                     start_date: Optional[pd.Timestamp] = None,
                     end_date: Optional[pd.Timestamp] = None,
                     min_pl: Optional[float] = None,
                     max_pl: Optional[float] = None) -> pd.DataFrame:
        """Filtre les trades selon les critères"""
        
        df = self.get_combined_data()
        
        if df.empty:
            return df
            
        if strategy_name:
            df = df[df['source'] == strategy_name]
            
        if start_date:
            df = df[pd.to_datetime(df['Date Opened']) >= start_date]
            
        if end_date:
            df = df[pd.to_datetime(df['Date Closed']) <= end_date]
            
        if min_pl is not None:
            df = df[df['P/L'] >= min_pl]
            
        if max_pl is not None:
            df = df[df['P/L'] <= max_pl]
            
        return df
        
    def calculate_correlations(self) -> pd.DataFrame:
        """Calcule les corrélations entre stratégies"""
        returns_dict = {}
        
        for name, model in self.trade_models.items():
            daily_returns = model.get_daily_returns()
            if len(daily_returns) > 0:
                returns_dict[name] = daily_returns
                
        if returns_dict:
            # Aligner les séries temporelles
            df = pd.DataFrame(returns_dict)
            return df.corr()
        return pd.DataFrame()
        
    def export_analysis(self, file_path: str, include_trades: bool = True, 
                       include_stats: bool = True, include_correlations: bool = True):
        """Exporte l'analyse complète vers Excel"""
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            
            if include_trades:
                trades_df = self.get_combined_data()
                if not trades_df.empty:
                    trades_df.to_excel(writer, sheet_name='Trades', index=False)
                    
            if include_stats:
                stats_df = self.get_statistics_summary()
                if not stats_df.empty:
                    stats_df.to_excel(writer, sheet_name='Statistics', index=False)
                    
            if include_correlations:
                corr_df = self.calculate_correlations()
                if not corr_df.empty:
                    corr_df.to_excel(writer, sheet_name='Correlations')
                    
    def clear_all_data(self):
        """Efface toutes les données chargées"""
        self.trade_models.clear()
        self.strategy_models.clear()
        self.current_data = None
        self.data_cleared.emit()  # Émettre le signal
        
    def get_loaded_files(self) -> List[str]:
        """Retourne la liste des fichiers chargés"""
        return list(self.trade_models.keys())
        
    def remove_file(self, file_name: str):
        """Supprime un fichier des données chargées"""
        if file_name in self.trade_models:
            del self.trade_models[file_name]
        if file_name in self.strategy_models:
            del self.strategy_models[file_name]
        self.file_removed.emit(file_name)  # Émettre le signal
            
    def get_trade_model(self, name: str) -> Optional[TradeModel]:
        """Récupère un modèle de trades spécifique"""
        return self.trade_models.get(name)
        
    def get_strategy_model(self, name: str) -> Optional[StrategyModel]:
        """Récupère un modèle de stratégie spécifique"""
        return self.strategy_models.get(name)