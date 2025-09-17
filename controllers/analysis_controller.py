import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal
from models.strategy_model import StrategyModel
from models.portfolio_model import PortfolioModel


class AnalysisController(QObject):
    """Contrôleur pour l'analyse quantitative avancée"""
    
    # Signaux
    analysis_completed = pyqtSignal(dict)
    omega_calculated = pyqtSignal(float)
    risk_metrics_updated = pyqtSignal(dict)
    optimization_result = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.current_analysis: Dict = {}
        
    def calculate_omega_ratio(self, returns: np.ndarray, 
                            threshold: float = 0) -> float:
        """Calcule le ratio Omega"""
        gains = returns[returns > threshold] - threshold
        losses = threshold - returns[returns <= threshold]
        
        if len(losses) == 0 or np.sum(losses) == 0:
            omega = float('inf')
        else:
            omega = np.sum(gains) / np.sum(losses)
            
        self.omega_calculated.emit(omega)
        return omega
        
    def calculate_comprehensive_metrics(self, returns: np.ndarray) -> Dict:
        """Calcule un ensemble complet de métriques"""
        strategy = StrategyModel("Analysis")
        strategy.set_returns(returns)
        
        metrics = strategy.metrics
        
        # Ajouter des métriques supplémentaires
        metrics['omega_ratios'] = {
            'omega_0': self.calculate_omega_ratio(returns, 0),
            'omega_rf': self.calculate_omega_ratio(returns, 0.02/252),  # Risk-free rate
            'omega_target': self.calculate_omega_ratio(returns, 0.10/252)  # Target return
        }
        
        # Statistiques de distribution
        metrics['distribution'] = {
            'mean': np.mean(returns),
            'median': np.median(returns),
            'std': np.std(returns),
            'skewness': stats.skew(returns),
            'kurtosis': stats.kurtosis(returns),
            'jarque_bera': stats.jarque_bera(returns)
        }
        
        # Métriques de risque avancées
        metrics['advanced_risk'] = self._calculate_advanced_risk_metrics(returns)
        
        self.current_analysis = metrics
        self.analysis_completed.emit(metrics)
        
        return metrics
        
    def _calculate_advanced_risk_metrics(self, returns: np.ndarray) -> Dict:
        """Calcule des métriques de risque avancées"""
        risk_metrics = {}
        
        # Rachev Ratio
        risk_metrics['rachev_ratio'] = self._calculate_rachev_ratio(returns)
        
        # Farinelli-Tibiletti Ratio
        risk_metrics['ft_ratio'] = self._calculate_ft_ratio(returns)
        
        # Kappa 3 (Kaplan-Knowles)
        risk_metrics['kappa3'] = self._calculate_kappa3(returns)
        
        # Generalized Sharpe Ratio
        risk_metrics['generalized_sharpe'] = self._calculate_generalized_sharpe(returns)
        
        # Probabilistic Sharpe Ratio
        risk_metrics['probabilistic_sharpe'] = self._calculate_probabilistic_sharpe(returns)
        
        # Modified Sharpe Ratio
        risk_metrics['modified_sharpe'] = self._calculate_modified_sharpe(returns)
        
        self.risk_metrics_updated.emit(risk_metrics)
        
        return risk_metrics
        
    def _calculate_rachev_ratio(self, returns: np.ndarray, 
                                alpha: float = 0.05, 
                                beta: float = 0.05) -> float:
        """Calcule le ratio de Rachev"""
        upper_tail = np.percentile(returns, (1 - alpha) * 100)
        lower_tail = abs(np.percentile(returns, beta * 100))
        
        if lower_tail == 0:
            return 0
            
        return upper_tail / lower_tail
        
    def _calculate_ft_ratio(self, returns: np.ndarray,
                           p: float = 1,
                           q: float = 2) -> float:
        """Calcule le ratio de Farinelli-Tibiletti"""
        threshold = np.mean(returns)
        
        upper_partial_moment = np.mean(np.maximum(returns - threshold, 0) ** p) ** (1/p)
        lower_partial_moment = np.mean(np.maximum(threshold - returns, 0) ** q) ** (1/q)
        
        if lower_partial_moment == 0:
            return float('inf')
            
        return upper_partial_moment / lower_partial_moment
        
    def _calculate_kappa3(self, returns: np.ndarray, 
                         threshold: float = 0) -> float:
        """Calcule le Kappa 3 (moment partiel d'ordre 3)"""
        excess_returns = returns - threshold
        lower_partial_moment3 = np.mean(np.minimum(excess_returns, 0) ** 3)
        
        if lower_partial_moment3 >= 0:
            return 0
            
        return np.mean(excess_returns) / ((-lower_partial_moment3) ** (1/3))
        
    def _calculate_generalized_sharpe(self, returns: np.ndarray, 
                                     power: float = 3) -> float:
        """Calcule le ratio de Sharpe généralisé"""
        mean_return = np.mean(returns)
        
        if power == 2:
            risk = np.std(returns)
        else:
            risk = np.mean(np.abs(returns - mean_return) ** power) ** (1/power)
            
        if risk == 0:
            return 0
            
        return mean_return / risk
        
    def _calculate_probabilistic_sharpe(self, returns: np.ndarray,
                                       benchmark_sharpe: float = 0) -> float:
        """Calcule le ratio de Sharpe probabiliste"""
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
        n = len(returns)
        
        if n <= 3:
            return 0
            
        sharpe_std = np.sqrt((1 + 0.5 * sharpe ** 2) / n)
        z_score = (sharpe - benchmark_sharpe) / sharpe_std
        
        return stats.norm.cdf(z_score)
        
    def _calculate_modified_sharpe(self, returns: np.ndarray) -> float:
        """Calcule le ratio de Sharpe modifié (avec ajustement pour skewness et kurtosis)"""
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        skewness = stats.skew(returns)
        kurtosis = stats.kurtosis(returns)
        
        if std_return == 0:
            return 0
            
        sharpe = mean_return / std_return
        
        # Ajustement de Cornish-Fisher
        modified_sharpe = sharpe * (1 + (skewness/6) * sharpe - ((kurtosis-3)/24) * sharpe**2)
        
        return modified_sharpe * np.sqrt(252)
        
    def perform_regime_detection(self, returns: pd.Series, 
                                n_regimes: int = 2) -> Dict:
        """Détecte les régimes de marché"""
        from sklearn.mixture import GaussianMixture
        
        # Préparer les données
        features = pd.DataFrame({
            'returns': returns,
            'volatility': returns.rolling(20).std(),
            'momentum': returns.rolling(20).mean()
        }).dropna()
        
        # Ajuster le modèle
        gmm = GaussianMixture(n_components=n_regimes, random_state=42)
        regimes = gmm.fit_predict(features)
        
        # Analyser les régimes
        regime_analysis = {}
        for i in range(n_regimes):
            regime_returns = returns[regimes == i]
            regime_analysis[f'regime_{i}'] = {
                'mean_return': np.mean(regime_returns),
                'volatility': np.std(regime_returns),
                'frequency': len(regime_returns) / len(returns),
                'sharpe': np.mean(regime_returns) / np.std(regime_returns) * np.sqrt(252) if np.std(regime_returns) > 0 else 0
            }
            
        return {
            'regimes': regimes,
            'analysis': regime_analysis,
            'current_regime': regimes[-1]
        }
        
    def calculate_rolling_metrics(self, returns: pd.Series, 
                                 window: int = 252) -> pd.DataFrame:
        """Calcule les métriques sur une fenêtre glissante"""
        rolling_metrics = pd.DataFrame(index=returns.index)
        
        # Métriques de base
        rolling_metrics['return'] = returns.rolling(window).mean() * 252
        rolling_metrics['volatility'] = returns.rolling(window).std() * np.sqrt(252)
        rolling_metrics['sharpe'] = rolling_metrics['return'] / rolling_metrics['volatility']
        
        # Omega ratio roulant
        rolling_metrics['omega'] = returns.rolling(window).apply(
            lambda x: self.calculate_omega_ratio(x.values) if len(x) == window else np.nan
        )
        
        # Drawdown roulant
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.rolling(window, min_periods=1).max()
        rolling_metrics['drawdown'] = (cumulative - rolling_max) / rolling_max
        
        return rolling_metrics
        
    def perform_factor_analysis(self, returns: pd.DataFrame, 
                               factors: pd.DataFrame) -> Dict:
        """Effectue une analyse factorielle"""
        from sklearn.linear_model import LinearRegression
        
        # Aligner les données
        aligned_returns, aligned_factors = returns.align(factors, join='inner')
        
        # Régression
        model = LinearRegression()
        model.fit(aligned_factors, aligned_returns)
        
        # Calculer les métriques
        predictions = model.predict(aligned_factors)
        residuals = aligned_returns - predictions
        r_squared = model.score(aligned_factors, aligned_returns)
        
        # Décomposition de la performance
        factor_contributions = {}
        for i, factor_name in enumerate(factors.columns):
            factor_contributions[factor_name] = {
                'beta': model.coef_[i],
                'contribution': model.coef_[i] * np.mean(aligned_factors.iloc[:, i])
            }
            
        return {
            'alpha': model.intercept_,
            'betas': dict(zip(factors.columns, model.coef_)),
            'r_squared': r_squared,
            'factor_contributions': factor_contributions,
            'residual_volatility': np.std(residuals)
        }
        
    def optimize_omega_ratio(self, returns_matrix: np.ndarray, 
                           threshold: float = 0) -> Dict:
        """Optimise le portfolio pour maximiser le ratio Omega"""
        from scipy.optimize import minimize
        
        n_assets = returns_matrix.shape[0]
        
        def neg_omega(weights):
            portfolio_returns = returns_matrix.T @ weights
            omega = self.calculate_omega_ratio(portfolio_returns, threshold)
            return -omega if not np.isinf(omega) else -1000
            
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        ]
        bounds = [(0, 1) for _ in range(n_assets)]
        initial_guess = np.ones(n_assets) / n_assets
        
        result = minimize(neg_omega, initial_guess, 
                         method='SLSQP', 
                         bounds=bounds, 
                         constraints=constraints)
        
        optimal_weights = result.x
        optimal_omega = -result.fun
        
        optimization_result = {
            'optimal_weights': optimal_weights,
            'optimal_omega': optimal_omega,
            'success': result.success
        }
        
        self.optimization_result.emit(optimization_result)
        
        return optimization_result
        
    def calculate_conditional_metrics(self, returns: pd.Series, 
                                     condition: pd.Series) -> Dict:
        """Calcule des métriques conditionnelles"""
        # Métriques pour condition vraie
        returns_true = returns[condition]
        metrics_true = {
            'mean': np.mean(returns_true),
            'volatility': np.std(returns_true),
            'sharpe': np.mean(returns_true) / np.std(returns_true) * np.sqrt(252) if np.std(returns_true) > 0 else 0,
            'omega': self.calculate_omega_ratio(returns_true.values),
            'frequency': len(returns_true) / len(returns)
        }
        
        # Métriques pour condition fausse
        returns_false = returns[~condition]
        metrics_false = {
            'mean': np.mean(returns_false),
            'volatility': np.std(returns_false),
            'sharpe': np.mean(returns_false) / np.std(returns_false) * np.sqrt(252) if np.std(returns_false) > 0 else 0,
            'omega': self.calculate_omega_ratio(returns_false.values),
            'frequency': len(returns_false) / len(returns)
        }
        
        return {
            'condition_true': metrics_true,
            'condition_false': metrics_false,
            'difference': {
                'mean': metrics_true['mean'] - metrics_false['mean'],
                'volatility': metrics_true['volatility'] - metrics_false['volatility'],
                'sharpe': metrics_true['sharpe'] - metrics_false['sharpe'],
                'omega': metrics_true['omega'] - metrics_false['omega']
            }
        }
        
    def perform_stress_testing(self, returns: np.ndarray, 
                             scenarios: Dict[str, float]) -> Dict:
        """Effectue des tests de stress"""
        results = {}
        
        for scenario_name, shock_magnitude in scenarios.items():
            # Appliquer le choc
            stressed_returns = returns.copy()
            
            if 'volatility' in scenario_name.lower():
                # Augmenter la volatilité
                stressed_returns = returns * shock_magnitude
            elif 'crash' in scenario_name.lower():
                # Simuler un crash
                stressed_returns = np.append(returns, [shock_magnitude])
            elif 'correlation' in scenario_name.lower():
                # Modifier les corrélations (si matrice de rendements)
                stressed_returns = returns + np.random.normal(0, shock_magnitude, len(returns))
            else:
                # Choc générique
                stressed_returns = returns + shock_magnitude
                
            # Calculer les métriques sous stress
            results[scenario_name] = {
                'mean_return': np.mean(stressed_returns),
                'volatility': np.std(stressed_returns),
                'max_drawdown': self._calculate_max_drawdown(stressed_returns),
                'var_95': np.percentile(stressed_returns, 5),
                'omega': self.calculate_omega_ratio(stressed_returns)
            }
            
        return results
        
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calcule le drawdown maximum"""
        cumulative = np.cumprod(1 + returns)
        peak = np.maximum.accumulate(cumulative)
        drawdown = (peak - cumulative) / peak
        return np.max(drawdown)