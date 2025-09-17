"""
Moteur de stress test RÉEL pour analyse de formules de trading
Tests avec des scénarios de crise historiques réels
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StressScenario:
    """Scénario de stress test"""
    name: str
    description: str
    period: str
    sharpe_impact: float
    omega_impact: float
    volatility_multiplier: float
    drawdown_multiplier: float
    win_rate_impact: float
    duration_months: int


@dataclass
class StressTestResults:
    """Résultats d'un stress test"""
    scenario_name: str
    formula: str
    original_allocation: float
    stressed_allocation: float
    allocation_change_pct: float
    expected_loss: float
    worst_case_loss: float
    probability_ruin: float
    recovery_months: int
    risk_score: str
    impact_analysis: Dict[str, float]


class StressTestEngine:
    """Moteur de stress test avec scénarios historiques réels"""
    
    def __init__(self):
        self.scenarios = self._create_historical_scenarios()
        
    def _create_historical_scenarios(self) -> List[StressScenario]:
        """Crée les scénarios basés sur des crises historiques réelles"""
        return [
            StressScenario(
                name="Black Monday 1987",
                description="Krach boursier du 19 octobre 1987",
                period="Oct 1987",
                sharpe_impact=-2.5,
                omega_impact=-0.6,
                volatility_multiplier=3.2,
                drawdown_multiplier=4.5,
                win_rate_impact=-0.35,
                duration_months=6
            ),
            StressScenario(
                name="Dot-com Crash 2000",
                description="Éclatement de la bulle internet",
                period="2000-2002",
                sharpe_impact=-1.8,
                omega_impact=-0.45,
                volatility_multiplier=2.1,
                drawdown_multiplier=2.8,
                win_rate_impact=-0.25,
                duration_months=24
            ),
            StressScenario(
                name="Lehman Crisis 2008",
                description="Crise financière mondiale",
                period="Sep 2008 - Mar 2009",
                sharpe_impact=-3.2,
                omega_impact=-0.8,
                volatility_multiplier=4.1,
                drawdown_multiplier=5.2,
                win_rate_impact=-0.42,
                duration_months=18
            ),
            StressScenario(
                name="Flash Crash 2010",
                description="Krach éclair du 6 mai 2010",
                period="May 2010",
                sharpe_impact=-3.8,
                omega_impact=-0.7,
                volatility_multiplier=6.2,
                drawdown_multiplier=4.5,
                win_rate_impact=-0.48,
                duration_months=1
            ),
            StressScenario(
                name="COVID-19 2020",
                description="Pandémie mondiale et confinements",
                period="Mar-Apr 2020",
                sharpe_impact=-2.1,
                omega_impact=-0.52,
                volatility_multiplier=5.3,
                drawdown_multiplier=3.8,
                win_rate_impact=-0.38,
                duration_months=3
            ),
            StressScenario(
                name="Taux Fed 2022",
                description="Hausse agressive des taux d'intérêt",
                period="2022-2023",
                sharpe_impact=-1.2,
                omega_impact=-0.28,
                volatility_multiplier=1.9,
                drawdown_multiplier=2.1,
                win_rate_impact=-0.18,
                duration_months=12
            ),
            StressScenario(
                name="Extrême Synthétique",
                description="Scénario catastrophe combiné",
                period="Hypothétique",
                sharpe_impact=-5.0,
                omega_impact=-1.2,
                volatility_multiplier=10.0,
                drawdown_multiplier=8.0,
                win_rate_impact=-0.70,
                duration_months=36
            )
        ]
    
    def run_stress_test(self, formula: str, scenario_name: str = None, base_metrics: Dict[str, float] = None) -> List[StressTestResults]:
        """
        Execute un stress test sur une formule avec scénarios historiques
        
        Args:
            formula: La formule d'allocation à tester
            scenario_name: Nom du scénario spécifique (None = tous)
        """
        if scenario_name:
            scenarios = [s for s in self.scenarios if s.name == scenario_name]
        else:
            scenarios = self.scenarios
            
        results = []
        
        # Calculer l'allocation de référence (conditions normales)
        baseline_metrics = self._get_baseline_metrics(base_metrics)
        baseline_allocation = self._calculate_allocation(formula, baseline_metrics)
        
        for scenario in scenarios:
            # Appliquer le stress aux métriques
            stressed_metrics = self._apply_stress(baseline_metrics, scenario)
            
            # Calculer la nouvelle allocation
            stressed_allocation = self._calculate_allocation(formula, stressed_metrics)
            
            # Calculer l'impact
            results.append(self._analyze_impact(
                scenario, formula, baseline_allocation, 
                stressed_allocation, baseline_metrics, stressed_metrics
            ))
            
        return results
    
    def _get_baseline_metrics(self, base_metrics: Dict[str, float] = None) -> Dict[str, float]:
        """Métriques de référence en conditions normales"""
        if base_metrics:
            # Utiliser les vraies métriques CSV si disponibles
            return base_metrics.copy()
        else:
            # Valeurs par défaut plus réalistes
            return {
                'sharpe': 0.4,      # Sharpe réaliste
                'omega': 1.05,      # Omega légèrement positif
                'volatility': 0.18, # 18% de volatilité réaliste
                'drawdown': 0.12,   # 12% de drawdown réaliste
                'win_rate': 0.52,   # 52% de trades gagnants
                'profit_factor': 1.15,
                'total_return': 0.08,
                'calmar': 0.6,
                'sortino': 0.5
            }
    
    def _apply_stress(self, baseline: Dict[str, float], scenario: StressScenario) -> Dict[str, float]:
        """Applique le stress d'un scénario aux métriques"""
        stressed = baseline.copy()
        
        # Appliquer les impacts du scénario
        stressed['sharpe'] = max(-3.0, baseline['sharpe'] + scenario.sharpe_impact)
        stressed['omega'] = max(0.1, baseline['omega'] + scenario.omega_impact)
        stressed['volatility'] = baseline['volatility'] * scenario.volatility_multiplier
        stressed['drawdown'] = min(0.95, baseline['drawdown'] * scenario.drawdown_multiplier)
        stressed['win_rate'] = max(0.05, baseline['win_rate'] + scenario.win_rate_impact)
        
        # Ajustements cohérents
        stressed['profit_factor'] = max(0.2, baseline['profit_factor'] * (1 + scenario.omega_impact))
        stressed['total_return'] = baseline['total_return'] * (1 + scenario.sharpe_impact * 0.3)
        stressed['calmar'] = max(0.1, baseline['calmar'] * (1 + scenario.sharpe_impact * 0.2))
        stressed['sortino'] = max(0.1, baseline['sortino'] + scenario.sharpe_impact * 0.8)
        
        return stressed
    
    def _calculate_allocation(self, formula: str, metrics: Dict[str, float]) -> float:
        """Calcule l'allocation basée sur la formule et les métriques"""
        safe_dict = {
            'sqrt': np.sqrt,
            'abs': abs,
            'max': max,
            'min': min,
            'log': np.log,
            'exp': np.exp
        }
        
        try:
            formula_lower = formula.lower()
            for key, value in metrics.items():
                formula_lower = formula_lower.replace(key, str(value))
            
            result = eval(formula_lower, {"__builtins__": {}}, safe_dict)
            return max(0, min(100, float(result)))
            
        except Exception:
            return 5.0  # Allocation par défaut conservative
    
    def _analyze_impact(self, scenario: StressScenario, formula: str, 
                       baseline_alloc: float, stressed_alloc: float,
                       baseline_metrics: Dict[str, float], 
                       stressed_metrics: Dict[str, float]) -> StressTestResults:
        """Analyse l'impact du stress test"""
        
        # Changement d'allocation
        alloc_change = ((stressed_alloc - baseline_alloc) / max(baseline_alloc, 0.01)) * 100
        
        # Estimation des pertes basée sur l'allocation et la sévérité du scénario
        severity = self._calculate_scenario_severity(scenario)
        allocation_ratio = stressed_alloc / 100
        
        # Perte espérée (plus réaliste)
        expected_loss = allocation_ratio * severity * 0.3
        
        # Pire cas (queue de distribution)
        worst_case_loss = allocation_ratio * severity * 0.8
        
        # Probabilité de ruine (basée sur allocation et durée)
        monthly_ruin_prob = (allocation_ratio ** 2) * 0.02  # 2% par mois pour 100% allocation
        prob_ruin = 1 - (1 - monthly_ruin_prob) ** scenario.duration_months
        prob_ruin = min(0.95, prob_ruin)
        
        # Temps de récupération estimé
        recovery_months = int(scenario.duration_months * (1 + allocation_ratio * 2))
        
        # Score de risque
        risk_score = self._calculate_risk_score(stressed_alloc, prob_ruin, worst_case_loss)
        
        # Analyse d'impact détaillée
        impact_analysis = {
            'sharpe_degradation': (stressed_metrics['sharpe'] - baseline_metrics['sharpe']),
            'volatility_increase': (stressed_metrics['volatility'] / baseline_metrics['volatility'] - 1) * 100,
            'drawdown_increase': (stressed_metrics['drawdown'] / baseline_metrics['drawdown'] - 1) * 100,
            'win_rate_drop': (stressed_metrics['win_rate'] - baseline_metrics['win_rate']) * 100
        }
        
        return StressTestResults(
            scenario_name=scenario.name,
            formula=formula,
            original_allocation=baseline_alloc,
            stressed_allocation=stressed_alloc,
            allocation_change_pct=alloc_change,
            expected_loss=expected_loss * 100,
            worst_case_loss=worst_case_loss * 100,
            probability_ruin=prob_ruin * 100,
            recovery_months=recovery_months,
            risk_score=risk_score,
            impact_analysis=impact_analysis
        )
    
    def _calculate_scenario_severity(self, scenario: StressScenario) -> float:
        """Calcule la sévérité d'un scénario (0-1)"""
        factors = [
            abs(scenario.sharpe_impact) / 5.0,
            abs(scenario.omega_impact) / 1.2,
            (scenario.volatility_multiplier - 1) / 9.0,
            (scenario.drawdown_multiplier - 1) / 7.0,
            abs(scenario.win_rate_impact) / 0.7
        ]
        
        return min(1.0, np.mean(factors))
    
    def _calculate_risk_score(self, allocation: float, prob_ruin: float, worst_case: float) -> str:
        """Calcule le score de risque global"""
        if allocation <= 2 and prob_ruin <= 5 and worst_case <= 10:
            return "🟢 TRÈS FAIBLE"
        elif allocation <= 5 and prob_ruin <= 15 and worst_case <= 25:
            return "🟡 FAIBLE"
        elif allocation <= 15 and prob_ruin <= 35 and worst_case <= 50:
            return "🟠 MODÉRÉ"
        elif allocation <= 30 and prob_ruin <= 60 and worst_case <= 75:
            return "🔴 ÉLEVÉ"
        else:
            return "💀 EXTRÊME"