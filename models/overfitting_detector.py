"""
Détecteur d'Overfitting pour les Formules de Trading
Module spécialisé pour détecter si une formule d'allocation est overfittée aux données historiques
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from scipy import stats
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class OverfittingDetector:
    """Détecteur d'overfitting pour les formules de trading"""

    def __init__(self):
        self.results = {}
        self.metrics_history = []

    def analyze_formula_overfitting(self, strategy_data: Dict, formula: str,
                                  current_allocations: Dict) -> Dict[str, Any]:
        """
        Analyse principale pour détecter l'overfitting d'une formule

        Args:
            strategy_data: Données des stratégies {name: {metrics, returns, dates}}
            formula: Formule d'allocation à tester
            current_allocations: Allocations actuelles calculées par la formule

        Returns:
            Dict avec les résultats d'analyse d'overfitting
        """
        results = {
            'overfitting_score': 0.0,
            'risk_level': 'FAIBLE',
            'warnings': [],
            'recommendations': [],
            'detailed_analysis': {},
            'time_stability': {},
            'cross_validation': {},
            'robustness_test': {},
            'correlation_analysis': {}
        }

        if len(strategy_data) < 2:
            results['warnings'].append("Pas assez de stratégies pour une analyse robuste")
            return results

        try:
            # 1. Analyse de stabilité temporelle
            stability_score = self._analyze_time_stability(strategy_data, formula)
            results['time_stability'] = stability_score

            # 2. Validation croisée temporelle
            cv_score = self._cross_validation_analysis(strategy_data, formula)
            results['cross_validation'] = cv_score

            # 3. Test de robustesse aux perturbations
            robustness_score = self._robustness_test(strategy_data, formula)
            results['robustness_test'] = robustness_score

            # 4. Analyse des corrélations excessives
            correlation_score = self._correlation_analysis(strategy_data, current_allocations)
            results['correlation_analysis'] = correlation_score

            # 5. Détection des allocations extrêmes
            extreme_allocation_score = self._detect_extreme_allocations(current_allocations)

            # 6. Score global d'overfitting (0-100)
            overfitting_score = self._calculate_overfitting_score(
                stability_score, cv_score, robustness_score,
                correlation_score, extreme_allocation_score
            )

            results['overfitting_score'] = overfitting_score
            results['risk_level'] = self._determine_risk_level(overfitting_score)
            results['warnings'] = self._generate_warnings(overfitting_score, results)

            # Analyse détaillée
            results['detailed_analysis'] = {
                'stability_score': stability_score.get('score', 0),
                'cv_score': cv_score.get('score', 0),
                'robustness_score': robustness_score.get('score', 0),
                'correlation_score': correlation_score.get('score', 0),
                'extreme_allocation_score': extreme_allocation_score,
                'formula_complexity': self._analyze_formula_complexity(formula)
            }

        except Exception as e:
            results['warnings'].append(f"Erreur d'analyse: {str(e)}")

        return results

    def _analyze_time_stability(self, strategy_data: Dict, formula: str) -> Dict:
        """Analyse la stabilité de la formule dans le temps"""
        try:
            # Diviser les données en périodes
            periods = 3
            all_allocations = []
            period_scores = []

            for name, data in strategy_data.items():
                if 'returns' not in data or data['returns'] is None:
                    continue

                returns = np.array(data['returns'])
                if len(returns) < periods * 10:  # Au moins 10 points par période
                    continue

                period_size = len(returns) // periods
                period_allocations = []

                for i in range(periods):
                    start_idx = i * period_size
                    end_idx = start_idx + period_size if i < periods - 1 else len(returns)
                    period_returns = returns[start_idx:end_idx]

                    # Calculer les métriques pour cette période
                    period_metrics = self._calculate_period_metrics(period_returns)
                    allocation = self._evaluate_formula(formula, period_metrics)
                    period_allocations.append(allocation)

                if len(period_allocations) == periods:
                    all_allocations.append(period_allocations)

            if not all_allocations:
                return {'score': 0, 'stability': 'INSUFFISANT', 'details': 'Pas assez de données'}

            # Calculer la variabilité des allocations dans le temps
            allocation_matrix = np.array(all_allocations)
            stability_scores = []

            for strategy_allocations in allocation_matrix:
                cv = np.std(strategy_allocations) / (np.mean(strategy_allocations) + 1e-6)
                stability_score = max(0, 100 - cv * 100)  # Plus le CV est élevé, plus le score est faible
                stability_scores.append(stability_score)

            overall_stability = np.mean(stability_scores)

            return {
                'score': overall_stability,
                'stability': 'STABLE' if overall_stability > 70 else 'INSTABLE' if overall_stability < 30 else 'MODERE',
                'coefficient_variation': np.mean([np.std(allocs) / (np.mean(allocs) + 1e-6) for allocs in all_allocations]),
                'details': f"Stabilité moyenne: {overall_stability:.1f}/100"
            }

        except Exception as e:
            return {'score': 0, 'stability': 'ERREUR', 'details': str(e)}

    def _cross_validation_analysis(self, strategy_data: Dict, formula: str) -> Dict:
        """Validation croisée temporelle pour tester la généralisation"""
        try:
            cv_scores = []
            n_splits = 3

            for name, data in strategy_data.items():
                if 'returns' not in data or data['returns'] is None:
                    continue

                returns = np.array(data['returns'])
                if len(returns) < n_splits * 20:  # Au moins 20 points par fold
                    continue

                # TimeSeriesSplit pour données temporelles
                tscv = TimeSeriesSplit(n_splits=n_splits)
                split_scores = []

                for train_idx, test_idx in tscv.split(returns):
                    train_returns = returns[train_idx]
                    test_returns = returns[test_idx]

                    # Entraîner sur train, tester sur test
                    train_metrics = self._calculate_period_metrics(train_returns)
                    test_metrics = self._calculate_period_metrics(test_returns)

                    train_allocation = self._evaluate_formula(formula, train_metrics)
                    test_allocation = self._evaluate_formula(formula, test_metrics)

                    # Score basé sur la différence d'allocation
                    diff = abs(train_allocation - test_allocation)
                    score = max(0, 100 - diff * 2)  # Pénalité pour forte différence
                    split_scores.append(score)

                if split_scores:
                    cv_scores.append(np.mean(split_scores))

            if not cv_scores:
                return {'score': 0, 'generalization': 'INSUFFISANT', 'details': 'Pas assez de données'}

            overall_cv_score = np.mean(cv_scores)

            return {
                'score': overall_cv_score,
                'generalization': 'BONNE' if overall_cv_score > 70 else 'MAUVAISE' if overall_cv_score < 30 else 'MODEREE',
                'cv_variance': np.var(cv_scores),
                'details': f"Score de généralisation: {overall_cv_score:.1f}/100"
            }

        except Exception as e:
            return {'score': 0, 'generalization': 'ERREUR', 'details': str(e)}

    def _robustness_test(self, strategy_data: Dict, formula: str) -> Dict:
        """Test de robustesse avec perturbations des métriques"""
        try:
            robustness_scores = []
            noise_levels = [0.05, 0.1, 0.2]  # 5%, 10%, 20% de bruit

            for name, data in strategy_data.items():
                if 'returns' not in data or data['returns'] is None:
                    continue

                returns = np.array(data['returns'])
                original_metrics = self._calculate_period_metrics(returns)
                original_allocation = self._evaluate_formula(formula, original_metrics)

                strategy_robustness = []

                for noise_level in noise_levels:
                    noisy_allocations = []

                    # Tester avec 10 perturbations différentes
                    for _ in range(10):
                        noisy_metrics = {}
                        for key, value in original_metrics.items():
                            noise = np.random.normal(0, abs(value) * noise_level)
                            noisy_metrics[key] = value + noise

                        noisy_allocation = self._evaluate_formula(formula, noisy_metrics)
                        noisy_allocations.append(noisy_allocation)

                    # Calculer la variance des allocations avec bruit
                    allocation_variance = np.var(noisy_allocations)
                    robustness = max(0, 100 - allocation_variance)
                    strategy_robustness.append(robustness)

                if strategy_robustness:
                    robustness_scores.append(np.mean(strategy_robustness))

            if not robustness_scores:
                return {'score': 0, 'robustness': 'INSUFFISANT', 'details': 'Pas assez de données'}

            overall_robustness = np.mean(robustness_scores)

            return {
                'score': overall_robustness,
                'robustness': 'ROBUSTE' if overall_robustness > 70 else 'FRAGILE' if overall_robustness < 30 else 'MODEREE',
                'sensitivity': 100 - overall_robustness,
                'details': f"Robustesse aux perturbations: {overall_robustness:.1f}/100"
            }

        except Exception as e:
            return {'score': 0, 'robustness': 'ERREUR', 'details': str(e)}

    def _correlation_analysis(self, strategy_data: Dict, current_allocations: Dict) -> Dict:
        """Analyse des corrélations pour détecter l'overfitting"""
        try:
            # Vérifier si les allocations sont trop corrélées aux performances passées
            allocations = []
            past_performances = []

            for name in strategy_data.keys():
                if name in current_allocations:
                    allocations.append(current_allocations[name])

                    # Performance passée
                    if 'returns' in strategy_data[name] and strategy_data[name]['returns'] is not None:
                        returns = strategy_data[name]['returns']
                        total_return = np.sum(returns) * 100  # En pourcentage
                        past_performances.append(total_return)
                    else:
                        past_performances.append(0)

            if len(allocations) < 2:
                return {'score': 50, 'correlation': 'INSUFFISANT', 'details': 'Pas assez de données'}

            # Calculer la corrélation entre allocations et performances passées
            correlation = np.corrcoef(allocations, past_performances)[0, 1]

            if np.isnan(correlation):
                correlation = 0

            # Score : corrélation trop élevée = overfitting probable
            correlation_score = max(0, 100 - abs(correlation) * 100)

            # Analyser aussi la distribution des allocations
            allocation_std = np.std(allocations)
            allocation_range = np.max(allocations) - np.min(allocations)

            return {
                'score': correlation_score,
                'correlation': abs(correlation),
                'correlation_level': 'FAIBLE' if abs(correlation) < 0.3 else 'ELEVEE' if abs(correlation) > 0.7 else 'MODEREE',
                'allocation_std': allocation_std,
                'allocation_range': allocation_range,
                'details': f"Corrélation allocation/performance: {correlation:.3f}"
            }

        except Exception as e:
            return {'score': 50, 'correlation': 'ERREUR', 'details': str(e)}

    def _detect_extreme_allocations(self, current_allocations: Dict) -> float:
        """Détecte les allocations extrêmes qui peuvent indiquer un overfitting"""
        if not current_allocations:
            return 50

        allocations = list(current_allocations.values())

        # Détecter les valeurs extrêmes
        extreme_count = 0
        total_count = len(allocations)

        for alloc in allocations:
            if alloc > 50 or alloc < 0:  # Allocation > 50% ou négative
                extreme_count += 1

        extreme_ratio = extreme_count / total_count if total_count > 0 else 0

        # Score : plus d'extrêmes = plus d'overfitting probable
        score = max(0, 100 - extreme_ratio * 150)

        return score

    def _calculate_overfitting_score(self, stability: Dict, cv: Dict, robustness: Dict,
                                   correlation: Dict, extreme: float) -> float:
        """Calcule le score global d'overfitting"""
        scores = [
            stability.get('score', 0) * 0.25,  # 25% pour la stabilité
            cv.get('score', 0) * 0.25,         # 25% pour la validation croisée
            robustness.get('score', 0) * 0.20, # 20% pour la robustesse
            correlation.get('score', 0) * 0.20, # 20% pour les corrélations
            extreme * 0.10                      # 10% pour les allocations extrêmes
        ]

        # Score final (0-100) : plus haut = moins d'overfitting
        final_score = sum(scores)

        # Inverser pour avoir un score d'overfitting (plus haut = plus d'overfitting)
        overfitting_score = 100 - final_score

        return max(0, min(100, overfitting_score))

    def _determine_risk_level(self, overfitting_score: float) -> str:
        """Détermine le niveau de risque d'overfitting"""
        if overfitting_score < 30:
            return 'FAIBLE'
        elif overfitting_score < 60:
            return 'MODERE'
        else:
            return 'ELEVE'

    def _generate_warnings(self, overfitting_score: float, results: Dict) -> List[str]:
        """Génère les avertissements basés sur l'analyse"""
        warnings = []

        if overfitting_score > 70:
            warnings.append("⚠️ RISQUE ÉLEVÉ D'OVERFITTING détecté!")

        stability = results.get('time_stability', {})
        if stability.get('score', 100) < 30:
            warnings.append("📈 Formule INSTABLE dans le temps")

        cv = results.get('cross_validation', {})
        if cv.get('score', 100) < 30:
            warnings.append("🎯 Mauvaise GÉNÉRALISATION sur nouvelles données")

        robustness = results.get('robustness_test', {})
        if robustness.get('score', 100) < 30:
            warnings.append("🔧 Formule FRAGILE aux perturbations")

        correlation = results.get('correlation_analysis', {})
        if correlation.get('correlation', 0) > 0.8:
            warnings.append("📊 Corrélation EXCESSIVE avec performances passées")

        return warnings

    # Méthode _generate_recommendations supprimée (inutile)

    def _calculate_period_metrics(self, returns: np.ndarray) -> Dict[str, float]:
        """Calcule les métriques pour une période donnée"""
        if len(returns) == 0:
            return {'sharpe': 0, 'volatility': 0.15, 'win_rate': 0.5}

        mean_return = np.mean(returns)
        std_return = np.std(returns)

        metrics = {
            'sharpe': mean_return / (std_return + 1e-6) * np.sqrt(252),
            'volatility': std_return * np.sqrt(252),
            'win_rate': np.sum(returns > 0) / len(returns),
            'total_return': np.sum(returns),
            'omega': 1.5,  # Valeur par défaut
            'drawdown': abs(np.min(np.minimum.accumulate(returns - np.maximum.accumulate(returns)))),
            'profit_factor': max(1, np.sum(returns[returns > 0]) / abs(np.sum(returns[returns < 0]) + 1e-6)),
            'calmar': mean_return * 252 / (abs(np.min(np.minimum.accumulate(returns - np.maximum.accumulate(returns)))) + 1e-6),
            'sortino': mean_return / (np.std(returns[returns < 0]) + 1e-6) * np.sqrt(252)
        }

        return metrics

    def _evaluate_formula(self, formula: str, metrics: Dict[str, float]) -> float:
        """Évalue une formule avec des métriques données"""
        try:
            # Sécuriser l'évaluation
            safe_dict = {
                '__builtins__': {},
                'sqrt': np.sqrt,
                'max': max,
                'min': min,
                'abs': abs
            }
            safe_dict.update(metrics)

            result = eval(formula, safe_dict)
            return min(50, max(0, float(result)))  # Cap entre 0 et 50%

        except Exception:
            return 10.0  # Valeur par défaut si erreur

    def _analyze_formula_complexity(self, formula: str) -> Dict[str, Any]:
        """Analyse la complexité de la formule"""
        operators = ['+', '-', '*', '/', '**', '(', ')']
        functions = ['sqrt', 'max', 'min', 'abs']

        complexity_score = 0
        complexity_score += len([op for op in operators if op in formula]) * 1
        complexity_score += len([func for func in functions if func in formula]) * 2
        complexity_score += formula.count('/') * 3  # Division plus complexe
        complexity_score += formula.count('**') * 4  # Puissance très complexe

        return {
            'complexity_score': complexity_score,
            'complexity_level': 'SIMPLE' if complexity_score < 5 else 'COMPLEXE' if complexity_score > 15 else 'MODEREE',
            'operator_count': len([op for op in operators if op in formula]),
            'function_count': len([func for func in functions if func in formula])
        }

    def quick_overfitting_check(self, allocations: Dict[str, float]) -> str:
        """Check rapide d'overfitting basé sur les allocations"""
        if not allocations:
            return "Aucune allocation à analyser"

        values = list(allocations.values())

        # Vérifications rapides
        issues = []

        # Allocations extrêmes
        extreme_count = sum(1 for v in values if v > 40 or v < 0)
        if extreme_count > 0:
            issues.append(f"⚠️ {extreme_count} allocation(s) extrême(s)")

        # Concentration excessive
        max_allocation = max(values) if values else 0
        if max_allocation > 50:
            issues.append(f"🎯 Allocation max trop élevée: {max_allocation:.1f}%")

        # Variabilité suspecte
        if len(values) > 1:
            std_dev = np.std(values)
            if std_dev > 20:
                issues.append(f"📊 Forte variabilité: {std_dev:.1f}%")

        if not issues:
            return "✅ Allocations semblent raisonnables"
        else:
            return " | ".join(issues)