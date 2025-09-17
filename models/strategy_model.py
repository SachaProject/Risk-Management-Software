import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Callable
from scipy import stats
from scipy.optimize import minimize_scalar
import warnings
warnings.filterwarnings('ignore')


class StrategyModel:
    """Modèle pour gérer les stratégies de trading et le calcul des métriques avancées"""
    
    def __init__(self, name: str = "Strategy"):
        self.name = name
        self.returns: Optional[np.ndarray] = None
        self.equity_curve: Optional[pd.Series] = None
        self.parameters: Dict = {}
        self.metrics: Dict = {}
        self.data: Optional[pd.DataFrame] = None
        
    def set_returns(self, returns: np.ndarray):
        """Définit les rendements de la stratégie"""
        self.returns = np.array(returns)
        self._calculate_all_metrics()
        
    def set_data(self, data: pd.DataFrame):
        """Définit les données de trading"""
        self.data = data
        
    def set_equity_curve(self, equity_curve: pd.Series):
        """Définit la courbe d'équité"""
        self.equity_curve = equity_curve
        if len(equity_curve) > 1:
            returns = equity_curve.pct_change().dropna().values
            self.set_returns(returns)
            
    def _calculate_all_metrics(self):
        """Calcule toutes les métriques de performance"""
        if self.returns is None or len(self.returns) == 0:
            return
            
        self.metrics = {
            'total_return': self._calculate_total_return(),
            'annualized_return': self._calculate_annualized_return(),
            'volatility': self._calculate_volatility(),
            'sharpe_ratio': self._calculate_sharpe_ratio(),
            'sortino_ratio': self._calculate_sortino_ratio(),
            'calmar_ratio': self._calculate_calmar_ratio(),
            'omega_ratio': self._calculate_omega_ratio(),
            'max_drawdown': self._calculate_max_drawdown(),
            'value_at_risk': self._calculate_var(),
            'conditional_var': self._calculate_cvar(),
            'win_rate': self._calculate_win_rate(),
            'profit_factor': self._calculate_profit_factor(),
            'recovery_factor': self._calculate_recovery_factor(),
            'payoff_ratio': self._calculate_payoff_ratio(),
            'kelly_criterion': self._calculate_kelly_criterion(),
            'tail_ratio': self._calculate_tail_ratio(),
            'common_sense_ratio': self._calculate_common_sense_ratio(),
            'cpc_index': self._calculate_cpc_index(),
            'skewness': stats.skew(self.returns),
            'kurtosis': stats.kurtosis(self.returns),
            'downside_deviation': self._calculate_downside_deviation(),
            'upside_potential': self._calculate_upside_potential(),
            'information_ratio': self._calculate_information_ratio(),
            'treynor_ratio': self._calculate_treynor_ratio(),
            'sterling_ratio': self._calculate_sterling_ratio(),
            'burke_ratio': self._calculate_burke_ratio(),
            'martin_ratio': self._calculate_martin_ratio(),
            'pain_index': self._calculate_pain_index(),
            'gain_to_pain_ratio': self._calculate_gain_to_pain_ratio(),
            'd_ratio': self._calculate_d_ratio(),
            'k_ratio': self._calculate_k_ratio(),
            'expectancy': self._calculate_expectancy(),
            'r_squared': self._calculate_r_squared(),
            'beta': self._calculate_beta(),
            'alpha': self._calculate_alpha()
        }
        
    def _calculate_total_return(self) -> float:
        """Calcule le rendement total"""
        return np.prod(1 + self.returns) - 1
        
    def _calculate_annualized_return(self, periods_per_year: int = 252) -> float:
        """Calcule le rendement annualisé"""
        n_periods = len(self.returns)
        total_return = self._calculate_total_return()
        return (1 + total_return) ** (periods_per_year / n_periods) - 1
        
    def _calculate_volatility(self, periods_per_year: int = 252) -> float:
        """Calcule la volatilité annualisée"""
        return np.std(self.returns) * np.sqrt(periods_per_year)
        
    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0, periods_per_year: int = 252) -> float:
        """Calcule le ratio de Sharpe"""
        excess_returns = self.returns - risk_free_rate / periods_per_year
        if np.std(excess_returns) == 0:
            return 0
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(periods_per_year)
        
    def _calculate_sortino_ratio(self, target_return: float = 0, periods_per_year: int = 252) -> float:
        """Calcule le ratio de Sortino"""
        downside_returns = self.returns[self.returns < target_return]
        if len(downside_returns) == 0:
            return np.inf
        downside_std = np.std(downside_returns)
        if downside_std == 0:
            return 0
        return (np.mean(self.returns) - target_return) / downside_std * np.sqrt(periods_per_year)
        
    def _calculate_calmar_ratio(self, periods_per_year: int = 252) -> float:
        """Calcule le ratio de Calmar"""
        max_dd = self._calculate_max_drawdown()
        if max_dd == 0:
            return 0
        return self._calculate_annualized_return(periods_per_year) / abs(max_dd)
        
    def _calculate_omega_ratio(self, threshold: float = 0) -> float:
        """Calcule le ratio Omega"""
        gains = self.returns[self.returns > threshold] - threshold
        losses = threshold - self.returns[self.returns <= threshold]
        
        if len(losses) == 0 or np.sum(losses) == 0:
            return np.inf
            
        return np.sum(gains) / np.sum(losses)
        
    def _calculate_max_drawdown(self) -> float:
        """Calcule le drawdown maximum"""
        cumulative = np.cumprod(1 + self.returns)
        peak = np.maximum.accumulate(cumulative)
        drawdown = (peak - cumulative) / peak
        return np.max(drawdown)
        
    def _calculate_var(self, confidence_level: float = 0.95) -> float:
        """Calcule la Value at Risk"""
        return np.percentile(self.returns, (1 - confidence_level) * 100)
        
    def _calculate_cvar(self, confidence_level: float = 0.95) -> float:
        """Calcule la Conditional Value at Risk"""
        var = self._calculate_var(confidence_level)
        return np.mean(self.returns[self.returns <= var])
        
    def _calculate_win_rate(self) -> float:
        """Calcule le taux de victoire"""
        return np.sum(self.returns > 0) / len(self.returns)
        
    def _calculate_profit_factor(self) -> float:
        """Calcule le profit factor"""
        gains = np.sum(self.returns[self.returns > 0])
        losses = abs(np.sum(self.returns[self.returns < 0]))
        if losses == 0:
            return np.inf
        return gains / losses
        
    def _calculate_recovery_factor(self) -> float:
        """Calcule le recovery factor"""
        total_return = self._calculate_total_return()
        max_dd = self._calculate_max_drawdown()
        if max_dd == 0:
            return 0
        return total_return / abs(max_dd)
        
    def _calculate_payoff_ratio(self) -> float:
        """Calcule le payoff ratio"""
        wins = self.returns[self.returns > 0]
        losses = self.returns[self.returns < 0]
        if len(losses) == 0:
            return np.inf
        if len(wins) == 0:
            return 0
        return np.mean(wins) / abs(np.mean(losses))
        
    def _calculate_kelly_criterion(self) -> float:
        """Calcule le critère de Kelly"""
        win_rate = self._calculate_win_rate()
        payoff_ratio = self._calculate_payoff_ratio()
        if payoff_ratio == 0:
            return 0
        return (payoff_ratio * win_rate - (1 - win_rate)) / payoff_ratio
        
    def _calculate_tail_ratio(self, percentile: float = 0.05) -> float:
        """Calcule le tail ratio"""
        right_tail = np.percentile(self.returns, 100 - percentile * 100)
        left_tail = np.percentile(self.returns, percentile * 100)
        if left_tail == 0:
            return 0
        return abs(right_tail / left_tail)
        
    def _calculate_common_sense_ratio(self) -> float:
        """Calcule le common sense ratio"""
        tail_ratio = self._calculate_tail_ratio()
        profit_factor = self._calculate_profit_factor()
        return tail_ratio * (profit_factor - 1) if profit_factor > 1 else 0
        
    def _calculate_cpc_index(self) -> float:
        """Calcule le CPC Index (Cumulative Performance Consistency)"""
        win_rate = self._calculate_win_rate()
        payoff_ratio = self._calculate_payoff_ratio()
        profit_factor = self._calculate_profit_factor()
        return win_rate * payoff_ratio * profit_factor
        
    def _calculate_downside_deviation(self, target: float = 0, periods_per_year: int = 252) -> float:
        """Calcule la déviation négative"""
        downside_returns = np.minimum(self.returns - target, 0)
        return np.std(downside_returns) * np.sqrt(periods_per_year)
        
    def _calculate_upside_potential(self, target: float = 0) -> float:
        """Calcule le potentiel de hausse"""
        upside_returns = np.maximum(self.returns - target, 0)
        return np.mean(upside_returns)
        
    def _calculate_information_ratio(self, benchmark_returns: Optional[np.ndarray] = None, periods_per_year: int = 252) -> float:
        """Calcule le ratio d'information"""
        if benchmark_returns is None:
            benchmark_returns = np.zeros_like(self.returns)
        excess_returns = self.returns - benchmark_returns
        tracking_error = np.std(excess_returns)
        if tracking_error == 0:
            return 0
        return np.mean(excess_returns) / tracking_error * np.sqrt(periods_per_year)
        
    def _calculate_treynor_ratio(self, risk_free_rate: float = 0, beta: Optional[float] = None) -> float:
        """Calcule le ratio de Treynor"""
        if beta is None:
            beta = self._calculate_beta()
        if beta == 0:
            return 0
        return (np.mean(self.returns) - risk_free_rate) / beta
        
    def _calculate_sterling_ratio(self, periods_per_year: int = 252) -> float:
        """Calcule le ratio de Sterling"""
        ann_return = self._calculate_annualized_return(periods_per_year)
        avg_dd = self._calculate_average_drawdown()
        if avg_dd == 0:
            return 0
        return ann_return / abs(avg_dd)
        
    def _calculate_burke_ratio(self, periods_per_year: int = 252) -> float:
        """Calcule le ratio de Burke"""
        ann_return = self._calculate_annualized_return(periods_per_year)
        drawdowns = self._get_drawdown_series()
        if len(drawdowns) == 0:
            return 0
        sqrt_sum_dd_squared = np.sqrt(np.sum(drawdowns ** 2))
        if sqrt_sum_dd_squared == 0:
            return 0
        return ann_return / sqrt_sum_dd_squared
        
    def _calculate_martin_ratio(self, periods_per_year: int = 252) -> float:
        """Calcule le ratio de Martin (Ulcer Performance Index)"""
        ann_return = self._calculate_annualized_return(periods_per_year)
        ulcer_index = self._calculate_ulcer_index()
        if ulcer_index == 0:
            return 0
        return ann_return / ulcer_index
        
    def _calculate_pain_index(self) -> float:
        """Calcule l'indice de douleur"""
        drawdowns = self._get_drawdown_series()
        return np.mean(np.abs(drawdowns))
        
    def _calculate_gain_to_pain_ratio(self) -> float:
        """Calcule le ratio gain/douleur"""
        total_return = self._calculate_total_return()
        pain_index = self._calculate_pain_index()
        if pain_index == 0:
            return 0
        return total_return / pain_index
        
    def _calculate_d_ratio(self) -> float:
        """Calcule le D-ratio"""
        n = len(self.returns)
        if n < 2:
            return 0
        x = np.arange(n)
        cumsum = np.cumsum(self.returns)
        slope, intercept = np.polyfit(x, cumsum, 1)
        y_fit = slope * x + intercept
        residuals = cumsum - y_fit
        std_residuals = np.std(residuals)
        if std_residuals == 0:
            return 0
        return slope / std_residuals
        
    def _calculate_k_ratio(self) -> float:
        """Calcule le K-ratio"""
        n = len(self.returns)
        if n < 2:
            return 0
        cumsum = np.cumsum(self.returns)
        x = np.arange(n)
        slope, intercept = np.polyfit(x, cumsum, 1)
        y_fit = slope * x + intercept
        std_err = np.sqrt(np.sum((cumsum - y_fit) ** 2) / (n - 2))
        if std_err == 0:
            return 0
        return slope / (std_err * np.sqrt(n))
        
    def _calculate_expectancy(self) -> float:
        """Calcule l'espérance mathématique"""
        win_rate = self._calculate_win_rate()
        wins = self.returns[self.returns > 0]
        losses = self.returns[self.returns < 0]
        avg_win = np.mean(wins) if len(wins) > 0 else 0
        avg_loss = np.mean(losses) if len(losses) > 0 else 0
        return win_rate * avg_win + (1 - win_rate) * avg_loss
        
    def _calculate_r_squared(self) -> float:
        """Calcule le R²"""
        n = len(self.returns)
        if n < 2:
            return 0
        x = np.arange(n)
        cumsum = np.cumsum(self.returns)
        correlation = np.corrcoef(x, cumsum)[0, 1]
        return correlation ** 2
        
    def _calculate_beta(self, market_returns: Optional[np.ndarray] = None) -> float:
        """Calcule le beta"""
        if market_returns is None:
            # Utiliser une approximation ou des données de marché par défaut
            return 1.0
        covariance = np.cov(self.returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        if market_variance == 0:
            return 0
        return covariance / market_variance
        
    def _calculate_alpha(self, risk_free_rate: float = 0, market_returns: Optional[np.ndarray] = None) -> float:
        """Calcule l'alpha"""
        if market_returns is None:
            return np.mean(self.returns) - risk_free_rate
        beta = self._calculate_beta(market_returns)
        return np.mean(self.returns) - risk_free_rate - beta * (np.mean(market_returns) - risk_free_rate)
        
    def _get_drawdown_series(self) -> np.ndarray:
        """Obtient la série des drawdowns"""
        cumulative = np.cumprod(1 + self.returns)
        peak = np.maximum.accumulate(cumulative)
        drawdown = (peak - cumulative) / peak
        return drawdown
        
    def _calculate_average_drawdown(self) -> float:
        """Calcule le drawdown moyen"""
        drawdowns = self._get_drawdown_series()
        return np.mean(drawdowns)
        
    def _calculate_ulcer_index(self) -> float:
        """Calcule l'Ulcer Index"""
        drawdowns = self._get_drawdown_series()
        return np.sqrt(np.mean(drawdowns ** 2))
        
    def optimize_position_size(self, method: str = 'kelly', max_position: float = 0.25) -> float:
        """Optimise la taille de position selon la méthode choisie"""
        methods = {
            'kelly': self._calculate_kelly_criterion,
            'optimal_f': self._calculate_optimal_f,
            'fixed_fractional': lambda: 0.02,
            'volatility_targeting': self._calculate_volatility_target,
            'risk_parity': self._calculate_risk_parity
        }
        
        if method in methods:
            position = methods[method]()
            return min(position, max_position)
        return 0.02
        
    def _calculate_optimal_f(self) -> float:
        """Calcule l'Optimal F de Ralph Vince"""
        if len(self.returns) == 0:
            return 0
            
        max_loss = min(self.returns)
        if max_loss >= 0:
            return 0
            
        def twr(f):
            product = 1
            for ret in self.returns:
                product *= (1 + f * ret / abs(max_loss))
            return -product
            
        result = minimize_scalar(twr, bounds=(0.01, 0.99), method='bounded')
        return result.x
        
    def _calculate_volatility_target(self, target_vol: float = 0.15, periods_per_year: int = 252) -> float:
        """Calcule la position pour cibler une volatilité donnée"""
        current_vol = self._calculate_volatility(periods_per_year)
        if current_vol == 0:
            return 0
        return min(target_vol / current_vol, 1.0)
        
    def _calculate_risk_parity(self) -> float:
        """Calcule la position selon le principe de parité des risques"""
        vol = np.std(self.returns)
        if vol == 0:
            return 0
        return 1 / (vol * 10)  # Ajuster le facteur selon le besoin
        
    def get_summary(self) -> Dict:
        """Retourne un résumé complet des métriques"""
        return {
            'name': self.name,
            'metrics': self.metrics,
            'parameters': self.parameters,
            'num_periods': len(self.returns) if self.returns is not None else 0
        }