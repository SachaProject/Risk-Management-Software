import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from .strategy_model import StrategyModel
from .trade_model import TradeModel


class PortfolioModel:
    """Modèle pour gérer un portfolio de stratégies"""
    
    def __init__(self, name: str = "Portfolio", initial_capital: float = 100000):
        self.name = name
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.strategies: Dict[str, StrategyModel] = {}
        self.trade_models: Dict[str, TradeModel] = {}
        self.allocations: Dict[str, float] = {}
        self.equity_curve: Optional[pd.Series] = None
        self.portfolio_metrics: Dict = {}
        self.correlation_matrix: Optional[pd.DataFrame] = None
        
    def add_strategy(self, name: str, strategy: StrategyModel, allocation: float = 0):
        """Ajoute une stratégie au portfolio"""
        self.strategies[name] = strategy
        self.allocations[name] = allocation
        self._normalize_allocations()
        
    def add_trade_model(self, name: str, trade_model: TradeModel):
        """Ajoute un modèle de trades au portfolio"""
        self.trade_models[name] = trade_model
        
        # Créer une stratégie basée sur les trades
        strategy = StrategyModel(name)
        
        # Passer les données du DataFrame à la stratégie
        if trade_model.df is not None:
            strategy.set_data(trade_model.df)
        
        returns = trade_model.get_returns()
        if len(returns) > 0:
            strategy.set_returns(returns)
            self.add_strategy(name, strategy)
            
    def remove_strategy(self, name: str):
        """Supprime une stratégie du portfolio"""
        if name in self.strategies:
            del self.strategies[name]
            del self.allocations[name]
            # PAS de normalisation - on garde les allocations exactes
            
    def set_allocation(self, allocations: Dict[str, float]):
        """Définit l'allocation du portfolio"""
        self.allocations = allocations
        # PAS de normalisation - on garde les allocations exactes
        
    def _normalize_allocations(self):
        """Normalise les allocations pour qu'elles somment à 1"""
        total = sum(self.allocations.values())
        if total > 0:
            for key in self.allocations:
                self.allocations[key] /= total
                
    def optimize_allocations(self, method: str = 'equal_weight', **kwargs):
        """Optimise l'allocation du portfolio selon la méthode choisie"""
        methods = {
            'equal_weight': self._equal_weight_allocation,
            'risk_parity': self._risk_parity_allocation,
            'min_variance': self._min_variance_allocation,
            'max_sharpe': self._max_sharpe_allocation,
            'max_omega': self._max_omega_allocation,
            'kelly': self._kelly_allocation
        }
        
        if method in methods:
            self.allocations = methods[method](**kwargs)
            self._normalize_allocations()
            
    def _equal_weight_allocation(self, **kwargs) -> Dict[str, float]:
        """Allocation équipondérée"""
        n = len(self.strategies)
        if n == 0:
            return {}
        weight = 1.0 / n
        return {name: weight for name in self.strategies}
        
    def _risk_parity_allocation(self, **kwargs) -> Dict[str, float]:
        """Allocation par parité des risques"""
        allocations = {}
        total_inv_vol = 0
        
        for name, strategy in self.strategies.items():
            if strategy.returns is not None and len(strategy.returns) > 0:
                vol = np.std(strategy.returns)
                if vol > 0:
                    inv_vol = 1.0 / vol
                    allocations[name] = inv_vol
                    total_inv_vol += inv_vol
                    
        if total_inv_vol > 0:
            for name in allocations:
                allocations[name] /= total_inv_vol
                
        return allocations
        
    def _min_variance_allocation(self, **kwargs) -> Dict[str, float]:
        """Allocation de variance minimale"""
        returns_matrix = self._get_returns_matrix()
        if returns_matrix is None:
            return self._equal_weight_allocation()
            
        cov_matrix = np.cov(returns_matrix)
        n = len(self.strategies)
        
        # Solution analytique pour le portfolio de variance minimale
        ones = np.ones(n)
        inv_cov = np.linalg.pinv(cov_matrix)
        weights = inv_cov @ ones / (ones @ inv_cov @ ones)
        
        # Contraindre les poids entre 0 et 1
        weights = np.maximum(weights, 0)
        weights = weights / weights.sum()
        
        return {name: float(weight) for name, weight in zip(self.strategies.keys(), weights)}
        
    def _max_sharpe_allocation(self, **kwargs) -> Dict[str, float]:
        """Allocation maximisant le ratio de Sharpe"""
        from scipy.optimize import minimize
        
        returns_matrix = self._get_returns_matrix()
        if returns_matrix is None:
            return self._equal_weight_allocation()
            
        mean_returns = np.mean(returns_matrix, axis=1)
        cov_matrix = np.cov(returns_matrix)
        n = len(self.strategies)
        
        def neg_sharpe(weights):
            portfolio_return = weights @ mean_returns
            portfolio_vol = np.sqrt(weights @ cov_matrix @ weights)
            return -portfolio_return / portfolio_vol if portfolio_vol > 0 else 0
            
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        ]
        bounds = [(0, 1) for _ in range(n)]
        initial_guess = np.ones(n) / n
        
        result = minimize(neg_sharpe, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            return {name: float(weight) for name, weight in zip(self.strategies.keys(), result.x)}
        return self._equal_weight_allocation()
        
    def _max_omega_allocation(self, threshold: float = 0, **kwargs) -> Dict[str, float]:
        """Allocation maximisant le ratio Omega"""
        from scipy.optimize import minimize
        
        returns_matrix = self._get_returns_matrix()
        if returns_matrix is None:
            return self._equal_weight_allocation()
            
        n = len(self.strategies)
        
        def neg_omega(weights):
            portfolio_returns = returns_matrix.T @ weights
            gains = portfolio_returns[portfolio_returns > threshold] - threshold
            losses = threshold - portfolio_returns[portfolio_returns <= threshold]
            
            if len(losses) == 0 or np.sum(losses) == 0:
                return -100  # Grande valeur négative pour maximisation
                
            return -np.sum(gains) / np.sum(losses)
            
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        ]
        bounds = [(0, 1) for _ in range(n)]
        initial_guess = np.ones(n) / n
        
        result = minimize(neg_omega, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            return {name: float(weight) for name, weight in zip(self.strategies.keys(), result.x)}
        return self._equal_weight_allocation()
        
    def _kelly_allocation(self, **kwargs) -> Dict[str, float]:
        """Allocation selon le critère de Kelly"""
        allocations = {}
        
        for name, strategy in self.strategies.items():
            if 'kelly_criterion' in strategy.metrics:
                kelly = strategy.metrics['kelly_criterion']
                # Appliquer une fraction de Kelly pour la sécurité
                allocations[name] = max(0, min(kelly * 0.25, 0.25))
            else:
                allocations[name] = 0.02
                
        total = sum(allocations.values())
        if total > 0:
            for name in allocations:
                allocations[name] /= total
                
        return allocations
        
    def _get_returns_matrix(self) -> Optional[np.ndarray]:
        """Construit la matrice des rendements alignés"""
        try:
            if not self.strategies:
                return None
                
            returns_list = []
            min_length = float('inf')
            
            # Collecter les returns valides et trouver la longueur minimale
            for strategy in self.strategies.values():
                if (strategy.returns is not None and 
                    isinstance(strategy.returns, (list, np.ndarray)) and 
                    len(strategy.returns) > 0):
                    returns_array = np.array(strategy.returns)
                    if len(returns_array) > 0:
                        returns_list.append(returns_array)
                        min_length = min(min_length, len(returns_array))
                        
            if not returns_list or min_length == float('inf') or min_length < 1:
                return None
                
            # Aligner toutes les séries sur la longueur minimale
            aligned_returns = []
            for returns in returns_list:
                aligned_returns.append(returns[-min_length:])
                
            return np.array(aligned_returns)
            
        except Exception as e:
            print(f"Erreur construction matrice returns: {e}")
            return None
        
    def calculate_portfolio_returns(self) -> np.ndarray:
        """Calcule les rendements du portfolio"""
        try:
            returns_matrix = self._get_returns_matrix()
            if returns_matrix is None or returns_matrix.size == 0:
                return np.array([])
                
            weights = np.array([self.allocations.get(name, 0) for name in self.strategies.keys()])
            
            # Vérifier la cohérence des dimensions
            if len(weights) != returns_matrix.shape[0]:
                print(f"Dimensions incompatibles: weights={len(weights)}, returns_matrix={returns_matrix.shape}")
                return np.array([])
                
            if np.sum(weights) == 0:
                return np.array([])
                
            portfolio_returns = returns_matrix.T @ weights
            return portfolio_returns
            
        except Exception as e:
            print(f"Erreur calcul returns portfolio: {e}")
            return np.array([])
        
    def calculate_portfolio_metrics(self):
        """Calcule les métriques du portfolio"""
        portfolio_returns = self.calculate_portfolio_returns()
        
        if len(portfolio_returns) == 0:
            return
            
        portfolio_strategy = StrategyModel("Portfolio")
        portfolio_strategy.set_returns(portfolio_returns)
        
        self.portfolio_metrics = portfolio_strategy.metrics
        
        # Ajouter des métriques spécifiques au portfolio
        self.portfolio_metrics['num_strategies'] = len(self.strategies)
        self.portfolio_metrics['diversification_ratio'] = self._calculate_diversification_ratio()
        self.portfolio_metrics['concentration'] = self._calculate_concentration()
        
    def _calculate_diversification_ratio(self) -> float:
        """Calcule le ratio de diversification"""
        returns_matrix = self._get_returns_matrix()
        if returns_matrix is None:
            return 1.0
            
        weights = np.array([self.allocations.get(name, 0) for name in self.strategies.keys()])
        individual_vols = np.array([np.std(returns) for returns in returns_matrix])
        
        weighted_avg_vol = weights @ individual_vols
        
        portfolio_returns = self.calculate_portfolio_returns()
        portfolio_vol = np.std(portfolio_returns)
        
        if portfolio_vol == 0:
            return 1.0
            
        return weighted_avg_vol / portfolio_vol
        
    def _calculate_concentration(self) -> float:
        """Calcule l'indice de concentration (Herfindahl-Hirschman)"""
        weights = list(self.allocations.values())
        return sum(w**2 for w in weights)
        
    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """Calcule la matrice de corrélation entre stratégies"""
        returns_matrix = self._get_returns_matrix()
        if returns_matrix is None:
            return pd.DataFrame()
            
        corr_matrix = np.corrcoef(returns_matrix)
        self.correlation_matrix = pd.DataFrame(
            corr_matrix,
            index=list(self.strategies.keys()),
            columns=list(self.strategies.keys())
        )
        
        return self.correlation_matrix
        
    def generate_equity_curve(self) -> pd.Series:
        """Génère la courbe d'équité du portfolio"""
        portfolio_returns = self.calculate_portfolio_returns()
        
        if len(portfolio_returns) == 0:
            return pd.Series([self.initial_capital])
            
        equity_values = [self.initial_capital]
        for ret in portfolio_returns:
            equity_values.append(equity_values[-1] * (1 + ret))
            
        dates = pd.date_range(end=datetime.now(), periods=len(equity_values), freq='D')
        self.equity_curve = pd.Series(equity_values, index=dates)
        
        return self.equity_curve
        
    def rebalance(self, frequency: str = 'monthly'):
        """Rééquilibre le portfolio selon la fréquence spécifiée"""
        frequencies = {
            'daily': 1,
            'weekly': 5,
            'monthly': 21,
            'quarterly': 63,
            'yearly': 252
        }
        
        if frequency not in frequencies:
            return
            
        # Logique de rééquilibrage à implémenter selon les besoins
        self._normalize_allocations()
        
    def get_summary(self) -> Dict:
        """Retourne un résumé du portfolio"""
        self.calculate_portfolio_metrics()
        
        return {
            'name': self.name,
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'strategies': list(self.strategies.keys()),
            'allocations': self.allocations,
            'metrics': self.portfolio_metrics,
            'num_trades': sum(len(tm.trades) for tm in self.trade_models.values())
        }
        
    def export_to_json(self, filepath: str):
        """Exporte le portfolio au format JSON"""
        summary = self.get_summary()
        
        # Convertir les arrays numpy en listes
        def convert_to_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            return obj
            
        summary_serializable = convert_to_serializable(summary)
        
        with open(filepath, 'w') as f:
            json.dump(summary_serializable, f, indent=2)
            
    def load_from_json(self, filepath: str):
        """Charge un portfolio depuis un fichier JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        self.name = data.get('name', 'Portfolio')
        self.initial_capital = data.get('initial_capital', 100000)
        self.current_capital = data.get('current_capital', self.initial_capital)
        self.allocations = data.get('allocations', {})
        self.portfolio_metrics = data.get('metrics', {})