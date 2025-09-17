import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal
from models.portfolio_model import PortfolioModel
from models.strategy_model import StrategyModel
from models.trade_model import TradeModel


class PortfolioController(QObject):
    """Contrôleur pour la gestion du portfolio"""
    
    # Signaux
    portfolio_updated = pyqtSignal()
    allocation_changed = pyqtSignal(dict)  # Nouvelles allocations
    optimization_complete = pyqtSignal(dict)  # Résultats de l'optimisation
    rebalance_needed = pyqtSignal(str)  # Message de rééquilibrage
    
    def __init__(self):
        super().__init__()
        self.portfolio = PortfolioModel()
        self.optimization_history: List[Dict] = []
        self.rebalance_schedule = None
        
    def initialize_portfolio(self, name: str = "Main Portfolio", 
                           initial_capital: float = 100000):
        """Initialise un nouveau portfolio"""
        self.portfolio = PortfolioModel(name, initial_capital)
        self.portfolio_updated.emit()
        
    def add_strategy_to_portfolio(self, name: str, strategy: StrategyModel, 
                                 allocation: float = 0):
        """Ajoute une stratégie au portfolio"""
        self.portfolio.add_strategy(name, strategy, allocation)
        self.portfolio_updated.emit()
        self.allocation_changed.emit(self.portfolio.allocations)
        print(f"Strategy {name} added to portfolio")
        
    def add_trade_model_to_portfolio(self, name: str, trade_model: TradeModel):
        """Ajoute un modèle de trades au portfolio"""
        self.portfolio.add_trade_model(name, trade_model)
        self.portfolio_updated.emit()
        
    def remove_strategy_from_portfolio(self, name: str):
        """Retire une stratégie du portfolio"""
        self.portfolio.remove_strategy(name)
        self.portfolio_updated.emit()
        self.allocation_changed.emit(self.portfolio.allocations)
        
    def update_allocations(self, allocations: Dict[str, float]):
        """Met à jour les allocations du portfolio"""
        self.portfolio.set_allocation(allocations)
        self.allocation_changed.emit(self.portfolio.allocations)
        self.portfolio_updated.emit()
        
    def optimize_portfolio(self, method: str = 'equal_weight', **kwargs):
        """Optimise les allocations du portfolio"""
        old_allocations = self.portfolio.allocations.copy()
        
        self.portfolio.optimize_allocations(method, **kwargs)
        
        optimization_result = {
            'method': method,
            'old_allocations': old_allocations,
            'new_allocations': self.portfolio.allocations.copy(),
            'parameters': kwargs,
            'timestamp': pd.Timestamp.now()
        }
        
        self.optimization_history.append(optimization_result)
        
        self.allocation_changed.emit(self.portfolio.allocations)
        self.optimization_complete.emit(optimization_result)
        self.portfolio_updated.emit()
        
    def calculate_portfolio_metrics(self) -> Dict:
        """Calcule les métriques du portfolio"""
        self.portfolio.calculate_portfolio_metrics()
        return self.portfolio.portfolio_metrics
        
    def get_portfolio_summary(self) -> Dict:
        """Obtient un résumé du portfolio"""
        return self.portfolio.get_summary()
        
    def generate_equity_curve(self) -> pd.Series:
        """Génère la courbe d'équité du portfolio"""
        return self.portfolio.generate_equity_curve()
        
    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """Calcule la matrice de corrélation"""
        return self.portfolio.calculate_correlation_matrix()
        
    def get_efficient_frontier(self, n_portfolios: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calcule la frontière efficiente"""
        returns_matrix = self.portfolio._get_returns_matrix()
        
        if returns_matrix is None:
            return np.array([]), np.array([]), np.array([])
            
        mean_returns = np.mean(returns_matrix, axis=1)
        cov_matrix = np.cov(returns_matrix)
        n_assets = len(mean_returns)
        
        # Générer des portfolios aléatoires
        returns_array = []
        volatility_array = []
        sharpe_array = []
        
        for _ in range(n_portfolios):
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)
            
            portfolio_return = np.sum(weights * mean_returns) * 252
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
            sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
            
            returns_array.append(portfolio_return)
            volatility_array.append(portfolio_volatility)
            sharpe_array.append(sharpe_ratio)
            
        return np.array(returns_array), np.array(volatility_array), np.array(sharpe_array)
        
    def perform_risk_analysis(self) -> Dict:
        """Effectue une analyse de risque complète"""
        portfolio_returns = self.portfolio.calculate_portfolio_returns()
        
        if len(portfolio_returns) == 0:
            return {}
            
        analysis = {
            'var_95': np.percentile(portfolio_returns, 5),
            'var_99': np.percentile(portfolio_returns, 1),
            'cvar_95': np.mean(portfolio_returns[portfolio_returns <= np.percentile(portfolio_returns, 5)]),
            'expected_shortfall': self._calculate_expected_shortfall(portfolio_returns),
            'tail_risk': self._calculate_tail_risk(portfolio_returns),
            'stress_test_results': self._perform_stress_test(portfolio_returns),
            'risk_contribution': self._calculate_risk_contribution()
        }
        
        return analysis
        
    def _calculate_expected_shortfall(self, returns: np.ndarray, alpha: float = 0.05) -> float:
        """Calcule l'expected shortfall"""
        var = np.percentile(returns, alpha * 100)
        return np.mean(returns[returns <= var])
        
    def _calculate_tail_risk(self, returns: np.ndarray, threshold: float = 0.05) -> Dict:
        """Calcule les métriques de risque de queue"""
        left_tail = returns[returns <= np.percentile(returns, threshold * 100)]
        right_tail = returns[returns >= np.percentile(returns, (1 - threshold) * 100)]
        
        return {
            'left_tail_mean': np.mean(left_tail) if len(left_tail) > 0 else 0,
            'right_tail_mean': np.mean(right_tail) if len(right_tail) > 0 else 0,
            'tail_ratio': abs(np.mean(right_tail) / np.mean(left_tail)) if len(left_tail) > 0 and np.mean(left_tail) != 0 else 0
        }
        
    def _perform_stress_test(self, returns: np.ndarray) -> Dict:
        """Effectue des tests de stress"""
        scenarios = {
            'market_crash': -0.20,  # Chute de 20%
            'flash_crash': -0.10,    # Chute de 10%
            'volatility_spike': 2.0,  # Doublement de la volatilité
            'correlation_breakdown': 1.0  # Corrélation à 1
        }
        
        results = {}
        current_value = self.portfolio.current_capital
        
        for scenario, shock in scenarios.items():
            if 'crash' in scenario:
                stressed_value = current_value * (1 + shock)
            elif scenario == 'volatility_spike':
                # Simuler l'impact d'une augmentation de volatilité
                stressed_returns = returns * shock
                stressed_value = current_value * (1 + np.mean(stressed_returns))
            else:
                stressed_value = current_value
                
            results[scenario] = {
                'value': stressed_value,
                'loss': current_value - stressed_value,
                'loss_percentage': (current_value - stressed_value) / current_value * 100
            }
            
        return results
        
    def _calculate_risk_contribution(self) -> Dict:
        """Calcule la contribution au risque de chaque stratégie"""
        try:
            returns_matrix = self.portfolio._get_returns_matrix()
            
            if returns_matrix is None or returns_matrix.size == 0:
                return {}
                
            weights = np.array([self.portfolio.allocations.get(name, 0) 
                              for name in self.portfolio.strategies.keys()])
            
            # Vérifier que nous avons assez de données
            if len(weights) == 0 or np.sum(weights) == 0:
                return {}
                
            # Calculer la matrice de covariance
            if returns_matrix.ndim == 1:
                returns_matrix = returns_matrix.reshape(-1, 1)
                
            if returns_matrix.shape[1] < len(weights):
                return {}
                
            cov_matrix = np.cov(returns_matrix.T)
            
            # S'assurer que cov_matrix a les bonnes dimensions
            if cov_matrix.ndim == 0:
                cov_matrix = np.array([[cov_matrix]])
            elif cov_matrix.ndim == 1:
                cov_matrix = np.diag(cov_matrix)
                
            portfolio_variance = weights @ cov_matrix @ weights.T
            
            if portfolio_variance <= 0:
                return {}
                
            marginal_contributions = cov_matrix @ weights.T
            contributions = weights * marginal_contributions / portfolio_variance
            
            return {name: float(contrib) 
                    for name, contrib in zip(self.portfolio.strategies.keys(), contributions)}
        except Exception as e:
            print(f"Erreur calcul contribution risque: {e}")
            return {}
        
    def set_rebalance_schedule(self, frequency: str = 'monthly'):
        """Définit la fréquence de rééquilibrage"""
        self.rebalance_schedule = frequency
        self.rebalance_needed.emit(f"Rééquilibrage programmé: {frequency}")
        
    def check_rebalance_needed(self, threshold: float = 0.05) -> bool:
        """Vérifie si un rééquilibrage est nécessaire"""
        if not self.portfolio.allocations:
            return False
            
        # Calculer les allocations actuelles basées sur les valeurs de marché
        current_values = {}
        total_value = 0
        
        for name, strategy in self.portfolio.strategies.items():
            if strategy.equity_curve is not None and len(strategy.equity_curve) > 0:
                current_values[name] = strategy.equity_curve.iloc[-1]
                total_value += current_values[name]
                
        if total_value == 0:
            return False
            
        # Comparer avec les allocations cibles
        for name, target_allocation in self.portfolio.allocations.items():
            if name in current_values:
                current_allocation = current_values[name] / total_value
                drift = abs(current_allocation - target_allocation)
                
                if drift > threshold:
                    self.rebalance_needed.emit(
                        f"Rééquilibrage nécessaire: {name} dévie de {drift*100:.1f}%"
                    )
                    return True
                    
        return False
        
    def execute_rebalance(self):
        """Exécute le rééquilibrage du portfolio"""
        self.portfolio.rebalance(self.rebalance_schedule or 'monthly')
        self.portfolio_updated.emit()
        self.allocation_changed.emit(self.portfolio.allocations)
        
    def save_portfolio(self, filepath: str):
        """Sauvegarde le portfolio"""
        self.portfolio.export_to_json(filepath)
        
    def load_portfolio(self, filepath: str):
        """Charge un portfolio"""
        self.portfolio.load_from_json(filepath)
        self.portfolio_updated.emit()
        self.allocation_changed.emit(self.portfolio.allocations)
        
    def get_optimization_history(self) -> List[Dict]:
        """Retourne l'historique des optimisations"""
        return self.optimization_history