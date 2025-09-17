"""
Moteur Monte Carlo RÉEL pour analyse de formules de trading
Calculs professionnels sans bullshit
"""

import numpy as np
from typing import Dict, List, Tuple
import math
from dataclasses import dataclass


@dataclass
class MonteCarloResults:
    """Résultats réels d'une simulation Monte Carlo"""
    expected_return: float
    volatility: float
    sharpe_ratio: float
    var_95: float
    cvar_95: float
    max_drawdown: float
    best_case: float
    worst_case: float
    probability_profit: float
    probability_loss_50: float
    probability_ruin: float
    percentiles: Dict[int, float]
    distribution_stats: Dict[str, float]
    allocation_per_strategy: float
    total_simulations: int


class MonteCarloEngine:
    """Moteur de simulation Monte Carlo professionnel"""
    
    def __init__(self):
        self.risk_free_rate = 0.005  # 0.5% taux sans risque réaliste (2024-2025)
        
    def run_simulation(self, formula: str, n_simulations: int = 10000, 
                      horizon_days: int = 252, confidence: float = 0.95, 
                      base_metrics: Dict[str, float] = None) -> MonteCarloResults:
        """
        Execute une VRAIE simulation Monte Carlo
        
        Args:
            formula: La formule d'allocation (ex: "sharpe * omega / drawdown")
            n_simulations: Nombre de simulations
            horizon_days: Horizon temporel en jours
            confidence: Niveau de confiance pour VaR/CVaR
            base_metrics: Métriques réelles des stratégies CSV (optionnel)
        """
        
        # 1. Générer des distributions réalistes pour chaque métrique
        metrics_distributions = self._generate_realistic_distributions(n_simulations, base_metrics)
        
        # 2. Calculer les allocations pour chaque simulation
        allocations = self._calculate_allocations(formula, metrics_distributions)
        
        # 3. Simuler les rendements basés sur les allocations
        returns = self._simulate_returns(allocations, horizon_days, n_simulations)
        
        # 4. Calculer toutes les métriques
        results = self._calculate_metrics(returns, allocations, confidence)
        
        return results
    
    def _generate_realistic_distributions(self, n_sims: int, base_metrics: Dict[str, float] = None) -> Dict[str, np.ndarray]:
        """
        Génère des distributions RÉALISTES pour chaque métrique
        Si base_metrics fourni, utilise ces valeurs comme moyennes
        Sinon utilise des valeurs génériques
        """
        np.random.seed(None)  # Vraie randomisation
        
        # Si on a des métriques de base (vraies stratégies CSV), les utiliser comme moyennes
        if base_metrics:
                
            distributions = {
                # Utiliser les valeurs CSV comme moyennes avec de la variance autour
                'sharpe': np.random.normal(base_metrics.get('sharpe', 0.5), 0.3, n_sims),
                'omega': np.maximum(0.1, np.random.normal(base_metrics.get('omega', 1.1), 0.2, n_sims)),
                'volatility': np.maximum(0.01, np.random.normal(base_metrics.get('volatility', 0.15), 0.05, n_sims)),
                'drawdown': np.clip(np.random.normal(base_metrics.get('drawdown', 0.08), 0.03, n_sims), 0.001, 0.95),
                'win_rate': np.clip(np.random.normal(base_metrics.get('win_rate', 0.58), 0.1, n_sims), 0.1, 0.9),
                'profit_factor': np.maximum(0.1, np.random.normal(base_metrics.get('profit_factor', 1.4), 0.3, n_sims)),
                'total_return': np.random.normal(base_metrics.get('total_return', 0.12), 0.1, n_sims),
                'calmar': np.random.normal(base_metrics.get('calmar', 0.8), 0.3, n_sims),
                'sortino': np.random.normal(base_metrics.get('sortino', 0.7), 0.3, n_sims)
            }
        else:
            # Distributions génériques si pas de données CSV
            print("⚠️ Pas de métriques CSV - utilisation valeurs génériques")
            distributions = {
                # Sharpe: Moyenne 0.5, std 0.8, peut être négatif
                'sharpe': np.random.normal(0.5, 0.8, n_sims),
                
                # Omega: Log-normale, moyenne 1.1, toujours > 0
                'omega': np.random.lognormal(0.1, 0.5, n_sims),
                
                # Volatilité: Gamma distribution, toujours positive, moyenne ~15%
                'volatility': np.random.gamma(2, 0.075, n_sims),
                
                # Drawdown: Beta distribution, entre 0 et 1, moyenne ~12%
                'drawdown': np.random.beta(2, 8, n_sims) * 0.5 + 0.01,  # Min 1% pour éviter division par 0
                
                # Win rate: Beta, entre 0 et 1, moyenne ~55%
                'win_rate': np.random.beta(5.5, 4.5, n_sims),
                
                # Profit factor: Log-normale, moyenne 1.3
                'profit_factor': np.random.lognormal(0.25, 0.4, n_sims),
                
                # Total return: Normale, peut être négatif
                'total_return': np.random.normal(0.12, 0.25, n_sims),
                
                # Calmar: Normale, moyenne 0.8
                'calmar': np.random.normal(0.8, 0.6, n_sims),
                
                # Sortino: Similaire à Sharpe mais généralement plus élevé
                'sortino': np.random.normal(0.7, 0.9, n_sims)
            }
        
        return distributions
    
    def _calculate_allocations(self, formula: str, metrics: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Calcule les allocations pour chaque simulation basé sur la formule
        """
        n_sims = len(metrics['sharpe'])
        allocations = np.zeros(n_sims)
        
        # Préparer un environnement sécurisé pour eval
        safe_dict = {
            'sqrt': np.sqrt,
            'abs': np.abs,
            'max': np.maximum,
            'min': np.minimum,
            'log': np.log,
            'exp': np.exp
        }
        
        # Calculer l'allocation pour chaque simulation
        for i in range(n_sims):
            # Créer un dictionnaire avec les valeurs de cette simulation
            sim_values = {
                'sharpe': metrics['sharpe'][i],
                'omega': metrics['omega'][i],
                'volatility': metrics['volatility'][i],
                'drawdown': metrics['drawdown'][i],
                'win_rate': metrics['win_rate'][i],
                'profit_factor': metrics['profit_factor'][i],
                'total_return': metrics['total_return'][i],
                'calmar': metrics['calmar'][i],
                'sortino': metrics['sortino'][i]
            }
            
            try:
                # Évaluer la formule avec les vraies valeurs
                formula_lower = formula.lower()
                for key, value in sim_values.items():
                    formula_lower = formula_lower.replace(key, str(value))
                
                result = eval(formula_lower, {"__builtins__": {}}, safe_dict)
                
                # Convertir en pourcentage d'allocation
                # Les formules donnent généralement des valeurs entre 0 et 100
                allocation = float(result)
                
                # Limiter les allocations entre 0 et 100%
                allocation = max(0, min(100, allocation))
                
                allocations[i] = allocation
                
            except Exception as e:
                # Si erreur, allocation par défaut conservative
                allocations[i] = 5.0
        
        return allocations
    
    def _simulate_returns(self, allocations: np.ndarray, horizon: int, n_sims: int) -> np.ndarray:
        """
        Simule les rendements basés sur les allocations calculées
        
        Plus l'allocation est élevée, plus le risque ET le rendement potentiel sont élevés
        """
        returns = np.zeros(n_sims)
        
        for i in range(n_sims):
            allocation = allocations[i] / 100  # Convertir en décimal
            
            # Paramètres basés sur l'allocation
            # Plus d'allocation = plus de rendement espéré MAIS plus de risque
            daily_expected_return = allocation * 0.0008  # 0.08% par jour pour 100% allocation
            daily_volatility = allocation * 0.025  # 2.5% vol quotidienne pour 100% allocation
            
            # Ajouter le risque de ruine pour les grosses allocations
            if allocation > 0.5:  # Plus de 50% d'allocation
                ruin_probability = (allocation - 0.5) * 0.02  # 2% de chance de ruine par jour au-dessus de 50%
                if np.random.random() < ruin_probability * horizon:
                    # Ruine ! Perte massive
                    returns[i] = -allocation * np.random.uniform(0.7, 1.0)
                    continue
            
            # Simulation du chemin de prix avec GBM (Geometric Brownian Motion)
            daily_returns = np.random.normal(daily_expected_return, daily_volatility, horizon)
            
            # Ajouter des événements de queue (tail events)
            n_tail_events = np.random.poisson(0.1 * horizon / 252)  # ~10% de chance par an
            for _ in range(n_tail_events):
                day = np.random.randint(0, horizon)
                # Événement négatif plus probable avec allocation élevée
                if np.random.random() < 0.7 + allocation * 0.2:
                    daily_returns[day] -= allocation * np.random.uniform(0.05, 0.15)
                else:
                    daily_returns[day] += allocation * np.random.uniform(0.03, 0.08)
            
            # Calculer le rendement cumulé
            cumulative_return = np.prod(1 + daily_returns) - 1
            
            # Appliquer les limites réalistes
            # Une stratégie ne peut pas perdre plus de 100%
            cumulative_return = max(-1.0, cumulative_return)
            
            returns[i] = cumulative_return
        
        return returns
    
    def _calculate_metrics(self, returns: np.ndarray, allocations: np.ndarray, 
                          confidence: float) -> MonteCarloResults:
        """
        Calcule toutes les métriques à partir des rendements simulés
        """
        # Statistiques de base
        expected_return = np.mean(returns) * 100
        volatility = np.std(returns) * 100
        
        # Sharpe Ratio
        excess_returns = returns - self.risk_free_rate
        sharpe = np.mean(excess_returns) / (np.std(returns) + 1e-10)
        
        # VaR et CVaR
        var_percentile = (1 - confidence) * 100
        var_95 = np.percentile(returns, var_percentile) * 100
        cvar_95 = np.mean(returns[returns <= np.percentile(returns, var_percentile)]) * 100
        
        # Drawdown maximum - calcul corrigé
        cumulative_value = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative_value)
        drawdown = (cumulative_value - running_max) / running_max
        
        # Éviter les valeurs aberrantes
        drawdown = np.clip(drawdown, -0.99, 0)  # Max 99% de perte
        max_drawdown = np.min(drawdown) * 100
        
        # Best/Worst cases
        best_case = np.percentile(returns, 95) * 100
        worst_case = np.percentile(returns, 5) * 100
        
        # Probabilités
        prob_profit = np.mean(returns > 0) * 100
        prob_loss_50 = np.mean(returns < -0.5) * 100
        prob_ruin = np.mean(returns < -0.9) * 100
        
        # Percentiles
        percentiles = {
            5: np.percentile(returns, 5) * 100,
            10: np.percentile(returns, 10) * 100,
            25: np.percentile(returns, 25) * 100,
            50: np.percentile(returns, 50) * 100,
            75: np.percentile(returns, 75) * 100,
            90: np.percentile(returns, 90) * 100,
            95: np.percentile(returns, 95) * 100
        }
        
        # Distribution stats
        distribution_stats = {
            'mean': np.mean(returns) * 100,
            'median': np.median(returns) * 100,
            'std': np.std(returns) * 100,
            'skewness': self._calculate_skewness(returns),
            'kurtosis': self._calculate_kurtosis(returns)
        }
        
        # Allocation moyenne
        avg_allocation = np.mean(allocations)
        
        return MonteCarloResults(
            expected_return=expected_return,
            volatility=volatility,
            sharpe_ratio=sharpe,
            var_95=var_95,
            cvar_95=cvar_95,
            max_drawdown=max_drawdown,
            best_case=best_case,
            worst_case=worst_case,
            probability_profit=prob_profit,
            probability_loss_50=prob_loss_50,
            probability_ruin=prob_ruin,
            percentiles=percentiles,
            distribution_stats=distribution_stats,
            allocation_per_strategy=avg_allocation,
            total_simulations=len(returns)
        )
    
    def _calculate_skewness(self, returns: np.ndarray) -> float:
        """Calcule la skewness (asymétrie) de la distribution"""
        mean = np.mean(returns)
        std = np.std(returns)
        if std == 0:
            return 0
        return np.mean(((returns - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, returns: np.ndarray) -> float:
        """Calcule la kurtosis (aplatissement) de la distribution"""
        mean = np.mean(returns)
        std = np.std(returns)
        if std == 0:
            return 0
        return np.mean(((returns - mean) / std) ** 4) - 3