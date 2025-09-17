"""
Vue de Détection d'Overfitting des Formules
Interface pour analyser si une formule d'allocation est overfittée aux données
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QGroupBox, QLabel, QTextEdit, QProgressBar,
                            QTableWidget, QTableWidgetItem, QSplitter,
                            QFrame, QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
from .styles import AppStyles
import sys
import os

# Ajouter le répertoire parent pour l'import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.overfitting_detector import OverfittingDetector

# Import matplotlib pour les graphiques
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

import numpy as np
from datetime import datetime


class OverfittingChartWidget(QWidget):
    """Widget de graphique pour l'analyse d'overfitting"""

    def __init__(self, figure_size=(8, 6)):
        super().__init__()
        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=figure_size, facecolor='#1a1f2e')
            self.canvas = FigureCanvas(self.figure)

            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.canvas)
            self.setLayout(layout)

            # Style dark
            plt.style.use('dark_background')
            self.figure.patch.set_facecolor('#1a1f2e')
        else:
            # Fallback si matplotlib indisponible
            layout = QVBoxLayout()
            error_label = QLabel("Matplotlib requis pour les graphiques")
            error_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(error_label)
            self.setLayout(layout)

    def clear(self):
        """Efface le graphique"""
        if MATPLOTLIB_AVAILABLE:
            self.figure.clear()
            self.canvas.draw()


class OverfittingView(QWidget):
    """Vue principale pour la détection d'overfitting"""

    analysis_completed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.detector = OverfittingDetector()
        self.current_results = {}
        self.strategy_data = {}
        self.last_formula = ""  # Pour détecter les changements
        self.init_ui()

        # Pas de timer automatique - analyse immédiate seulement

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setStyleSheet("""
            QWidget {
                background-color: #0f1419;
                color: #e2e8f0;
            }
            QGroupBox {
                border: 1px solid #2d3748;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #ff6b6b;
            }
            QTableWidget {
                background-color: #1a1f2e;
                alternate-background-color: #2d3748;
                gridline-color: #4a5568;
            }
            QTextEdit {
                background-color: #1a1f2e;
                border: 1px solid #2d3748;
                border-radius: 4px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(self)

        # Header avec contrôles
        header = self.create_header()
        layout.addWidget(header)

        # Splitter principal
        main_splitter = QSplitter(Qt.Vertical)

        # Section résultats principaux
        results_widget = self.create_results_section()
        main_splitter.addWidget(results_widget)

        # Section détails et recommandations
        details_widget = self.create_details_section()
        main_splitter.addWidget(details_widget)

        main_splitter.setSizes([300, 400])
        layout.addWidget(main_splitter)

        # Première analyse au démarrage immédiate
        self.analyze_current_formula()

    def create_header(self):
        """Crée le header avec contrôles"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1a1f2e;
                border-bottom: 2px solid #2d3748;
                padding: 15px;
            }
        """)

        layout = QHBoxLayout(header)

        # Titre principal
        title = QLabel("🔍 DÉTECTION D'OVERFITTING DES FORMULES")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #ff6b6b;")

        # Pas de bouton - tout automatique

        # Plus de status d'analyse

        # Pas de barre de progression

        layout.addWidget(title)
        layout.addStretch()
        # Plus de barre de progression à ajouter
        # Plus de status label à ajouter

        return header

    def create_results_section(self):
        """Crée la section des résultats principaux"""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Score d'overfitting principal avec design amélioré
        score_group = QGroupBox("🎯 SCORE D'OVERFITTING")
        score_group.setStyleSheet("""
            QGroupBox {
                border: 3px solid #4a5568;
                border-radius: 15px;
                margin-top: 20px;
                padding-top: 20px;
                background-color: #1a202c;
                font-weight: bold;
                font-size: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 15px;
                color: #ff6b6b;
                background-color: #1a202c;
            }
        """)
        score_layout = QVBoxLayout(score_group)
        score_layout.setSpacing(15)

        self.overfitting_score_label = QLabel("--")
        self.overfitting_score_label.setAlignment(Qt.AlignCenter)
        self.overfitting_score_label.setFont(QFont("Arial", 48, QFont.Bold))
        self.overfitting_score_label.setStyleSheet("""
            color: #ff6b6b;
            background-color: #2d3748;
            border: 2px solid #4a5568;
            border-radius: 12px;
            padding: 15px;
            margin: 10px;
        """)
        self.overfitting_score_label.setToolTip(
            "🎯 SCORE D'OVERFITTING (0-100%)\n\n"
            "📊 CALCUL :\n"
            "• 25% Stabilité temporelle\n"
            "• 25% Validation croisée\n"
            "• 20% Robustesse\n"
            "• 20% Corrélations\n"
            "• 10% Allocations extrêmes\n\n"
            "📈 INTERPRÉTATION :\n"
            "• 0-15% = EXCELLENT (formule très fiable)\n"
            "• 15-30% = BON (formule correcte)\n"
            "• 30-60% = MOYEN (à améliorer)\n"
            "• 60-100% = DANGEREUX (overfitting)\n\n"
            "⚠️ Plus le score est BAS, mieux c'est !"
        )

        self.risk_level_label = QLabel("ANALYSE EN COURS")
        self.risk_level_label.setAlignment(Qt.AlignCenter)
        self.risk_level_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.risk_level_label.setStyleSheet("""
            color: #ffa500;
            background-color: rgba(255, 165, 0, 0.1);
            border: 1px solid #ffa500;
            border-radius: 8px;
            padding: 8px;
            margin: 5px;
        """)

        score_layout.addWidget(self.overfitting_score_label)
        score_layout.addWidget(self.risk_level_label)
        score_info = QLabel("Score 0-100 : Plus BAS = Mieux !\n0-15% = Excellent | 15-30% = Bon | 30%+ = À améliorer")
        score_info.setAlignment(Qt.AlignCenter)
        score_info.setStyleSheet("color: #cbd5e0; font-size: 10px; font-style: italic;")
        score_layout.addWidget(score_info)

        layout.addWidget(score_group)

        # Métriques détaillées
        metrics_group = QGroupBox("📊 MÉTRIQUES DÉTAILLÉES")
        metrics_layout = QVBoxLayout(metrics_group)

        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["Métrique", "Score"])
        self.metrics_table.horizontalHeader().setStretchLastSection(True)
        self.metrics_table.setMaximumHeight(200)

        # Activer les tooltips (automatiques avec setToolTip)

        metrics_layout.addWidget(self.metrics_table)
        layout.addWidget(metrics_group)

        # Analyse visuelle moderne
        if MATPLOTLIB_AVAILABLE:
            visual_group = QGroupBox("📊 ANALYSE VISUELLE")
            visual_group.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #4a5568;
                    border-radius: 12px;
                    margin-top: 15px;
                    padding-top: 15px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 10px;
                    color: #60a5fa;
                }
            """)
            visual_layout = QVBoxLayout(visual_group)

            self.summary_chart = OverfittingChartWidget((8, 5))
            visual_layout.addWidget(self.summary_chart)
            layout.addWidget(visual_group)

        return widget

    def create_details_section(self):
        """Crée la section des détails et recommandations"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Section Analyse détaillée uniquement (sans onglets)

        # Onglet Recommandations supprimé

        # Analyse détaillée
        details_group = QGroupBox("🔍 ANALYSE DÉTAILLÉE")
        details_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #4a5568;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #1a202c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #60a5fa;
                background-color: #1a202c;
            }
        """)
        details_layout = QVBoxLayout(details_group)

        self.details_text = QTextEdit()
        self.details_text.setStyleSheet("color: #cbd5e0;")
        self.details_text.setToolTip(
            "🔍 ANALYSE DÉTAILLÉE\n\n"
            "Informations techniques complètes :\n"
            "• Scores détaillés de chaque métrique\n"
            "• Statut de stabilité temporelle\n"
            "• Résultats de validation croisée\n"
            "• Niveau de robustesse\n"
            "• Analyse des corrélations\n"
            "• Timestamp de la dernière analyse\n\n"
            "Utile pour comprendre en détail\n"
            "pourquoi ta formule a ce score."
        )
        details_layout.addWidget(self.details_text)

        # Ajouter directement le groupe détails
        layout.addWidget(details_group)

        return widget

    def analyze_current_formula(self):
        """Lance l'analyse de la formule actuelle"""
        # Analyse immédiate sans indicateurs

        try:
            # Récupérer la formule et les données actuelles
            formula, allocations, strategy_data = self.get_current_formula_data()

            if not formula:
                # Aucune formule trouvée
                return

            if not strategy_data:
                # Aucune donnée de stratégie
                return

            # Progression supprimée

            # Lancer l'analyse d'overfitting
            results = self.detector.analyze_formula_overfitting(
                strategy_data, formula, allocations
            )

            # Progression supprimée

            # Sauvegarder et afficher les résultats
            self.current_results = results
            self.strategy_data = strategy_data
            self.update_display(results)

            # Progression supprimée

            # Plus de message de statut

            # Émettre le signal
            self.analysis_completed.emit(results)

        except Exception as e:
            # Erreur sans affichage
            pass

    def get_current_formula_data(self):
        """Récupère la formule et données actuelles depuis la main window"""
        try:
            # Accéder à la fenêtre principale
            widget = self
            main_window = None

            for _ in range(10):
                widget = widget.parent() if widget else None
                if widget and widget.__class__.__name__ == 'MainWindow':
                    main_window = widget
                    break

            if not main_window:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    for widget in app.topLevelWidgets():
                        if widget.__class__.__name__ == 'MainWindow':
                            main_window = widget
                            break

            if not main_window or not hasattr(main_window, 'controller'):
                return None, None, None

            controller = main_window.controller

            # Récupérer la formule actuelle
            formula = None
            if hasattr(main_window, 'portfolio_view') and hasattr(main_window.portfolio_view, 'formula_editor'):
                formula = main_window.portfolio_view.formula_editor.toPlainText().strip()

            # Récupérer les allocations actuelles
            portfolio = controller.portfolio_controller.portfolio
            allocations = {}
            if portfolio and hasattr(portfolio, 'allocations'):
                allocations = {name: alloc * 100 for name, alloc in portfolio.allocations.items()}

            # Récupérer les données de stratégies
            strategy_data = self.extract_strategy_data(controller)

            return formula, allocations, strategy_data

        except Exception as e:
            # Erreur silencieuse pour éviter le spam dans les logs
            return None, None, None

    def extract_strategy_data(self, controller):
        """Extrait les données nécessaires pour l'analyse"""
        try:
            data_controller = controller.data_controller
            trade_models = data_controller.trade_models if data_controller else {}

            strategy_data = {}

            for name, trade_model in trade_models.items():
                if not trade_model:
                    continue
                if trade_model.df is None:
                    continue
                if hasattr(trade_model.df, 'empty') and trade_model.df.empty:
                    continue

                # Extraire les rendements et métriques
                returns = trade_model.get_returns()
                stats = trade_model.get_statistics()

                if returns is not None and len(returns) > 5:  # Au moins 5 points
                    strategy_data[name] = {
                        'returns': returns,
                        'metrics': stats,
                        'dates': trade_model.df.get('Date Closed') if 'Date Closed' in trade_model.df else None
                    }

            return strategy_data

        except Exception as e:
            print(f"Erreur extract_strategy_data: {e}")
            return {}

    def update_display(self, results):
        """Met à jour l'affichage avec les résultats"""
        # Score principal
        score = results.get('overfitting_score', 0)
        risk_level = results.get('risk_level', 'INCONNU')

        self.overfitting_score_label.setText(f"{score:.0f}")
        self.risk_level_label.setText(f"RISQUE {risk_level}")

        # Couleur selon le risque (plus nuancée)
        if score < 15:
            # Excellent : Vert très vif
            self.risk_level_label.setStyleSheet("color: #00ff88; font-weight: bold;")
            self.overfitting_score_label.setStyleSheet("color: #00ff88; font-weight: bold;")
            self.risk_level_label.setText(f"EXCELLENT (< 15%)")
        elif score < 30:
            # Bon : Vert standard
            self.risk_level_label.setStyleSheet("color: #4ade80; font-weight: bold;")
            self.overfitting_score_label.setStyleSheet("color: #4ade80; font-weight: bold;")
            self.risk_level_label.setText(f"BON SCORE (< 30%)")
        elif risk_level == 'MODERE':
            # Modéré : Orange
            self.risk_level_label.setStyleSheet("color: #ffa500; font-weight: bold;")
            self.overfitting_score_label.setStyleSheet("color: #ffa500; font-weight: bold;")
        else:
            # Élevé : Rouge
            self.risk_level_label.setStyleSheet("color: #ff4444; font-weight: bold;")
            self.overfitting_score_label.setStyleSheet("color: #ff4444; font-weight: bold;")

        # Tableau des métriques
        self.update_metrics_table(results)

        # Mise à jour des détails uniquement
        self.update_details(results)

        # Graphique
        if MATPLOTLIB_AVAILABLE:
            self.update_summary_chart(results)

    def update_metrics_table(self, results):
        """Met à jour le tableau des métriques"""
        detailed = results.get('detailed_analysis', {})

        # Définir les métriques avec leurs descriptions
        self.metrics_data = {
            "Stabilité": {
                "score": detailed.get('stability_score', 0),
                "tooltip": (
                    "⏰ STABILITÉ TEMPORELLE\n\n"
                    "📊 CALCUL :\n"
                    "• Divise tes données en 3 périodes\n"
                    "• Calcule l'allocation pour chaque période\n"
                    "• Mesure la variabilité entre périodes\n"
                    "• Score = 100 - (variabilité × 100)\n\n"
                    "🎯 INTERPRÉTATION :\n"
                    "• 70+ = STABLE (formule constante)\n"
                    "• 30-70 = MODÉRÉE (quelques variations)\n"
                    "• <30 = INSTABLE (résultats imprévisibles)\n\n"
                    "💡 Plus ta formule donne des résultats similaires\n"
                    "dans le temps, plus ce score est élevé."
                )
            },
            "Validation": {
                "score": detailed.get('cv_score', 0),
                "tooltip": (
                    "🎯 VALIDATION CROISÉE\n\n"
                    "📊 CALCUL :\n"
                    "• Utilise TimeSeriesSplit (3 périodes)\n"
                    "• Entraîne la formule sur une période\n"
                    "• Teste sur la période suivante\n"
                    "• Compare les allocations train vs test\n"
                    "• Score = 100 - (différence moyenne × 2)\n\n"
                    "🎯 INTERPRÉTATION :\n"
                    "• 70+ = BONNE généralisation\n"
                    "• 30-70 = MODÉRÉE\n"
                    "• <30 = MAUVAISE (overfitting probable)\n\n"
                    "💡 Teste si ta formule fonctionne sur\n"
                    "des données qu'elle n'a jamais vues."
                )
            },
            "Robustesse": {
                "score": detailed.get('robustness_score', 0),
                "tooltip": (
                    "🔧 ROBUSTESSE\n\n"
                    "📊 CALCUL :\n"
                    "• Ajoute 5%, 10%, 20% de bruit aux métriques\n"
                    "• Recalcule les allocations avec le bruit\n"
                    "• Mesure la variance des résultats\n"
                    "• Score = 100 - variance_allocations\n\n"
                    "🎯 INTERPRÉTATION :\n"
                    "• 70+ = ROBUSTE (stable au bruit)\n"
                    "• 30-70 = MODÉRÉE\n"
                    "• <30 = FRAGILE (sensible aux petits changements)\n\n"
                    "💡 Une formule robuste donne des résultats\n"
                    "similaires même si les métriques changent un peu."
                )
            },
            "Corrélations": {
                "score": detailed.get('correlation_score', 0),
                "tooltip": (
                    "📊 CORRÉLATIONS\n\n"
                    "📊 CALCUL :\n"
                    "• Calcule la corrélation entre :\n"
                    "  - Performances passées des stratégies\n"
                    "  - Allocations actuelles de ta formule\n"
                    "• Score = 100 - |corrélation| × 100\n\n"
                    "🎯 INTERPRÉTATION :\n"
                    "• 70+ = FAIBLE corrélation (bon)\n"
                    "• 30-70 = MODÉRÉE\n"
                    "• <30 = FORTE corrélation (overfitting !)\n\n"
                    "⚠️ Si ta formule alloue plus aux stratégies\n"
                    "qui ont bien performé dans le passé,\n"
                    "c'est de l'overfitting !"
                )
            },
            "Extrêmes": {
                "score": detailed.get('extreme_allocation_score', 0),
                "tooltip": (
                    "⚖️ ALLOCATIONS EXTRÊMES\n\n"
                    "📊 CALCUL :\n"
                    "• Compte les allocations > 50% ou < 0%\n"
                    "• Ratio = nombre_extrêmes / total_stratégies\n"
                    "• Score = 100 - (ratio × 150)\n\n"
                    "🎯 INTERPRÉTATION :\n"
                    "• 70+ = Pas d'extrêmes (bon)\n"
                    "• 30-70 = Quelques extrêmes\n"
                    "• <30 = Beaucoup d'extrêmes (danger !)\n\n"
                    "⚠️ Des allocations > 50% ou négatives\n"
                    "sont souvent le signe d'overfitting\n"
                    "ou de formules mal contraintes."
                )
            }
        }

        # MÊME ORDRE que dans les barres du graphique
        metrics = [
            ("Stabilité", detailed.get('stability_score', 0)),
            ("Validation", detailed.get('cv_score', 0)),
            ("Robustesse", detailed.get('robustness_score', 0)),
            ("Corrélations", detailed.get('correlation_score', 0)),
            ("Extrêmes", detailed.get('extreme_allocation_score', 0))
        ]

        self.metrics_table.setRowCount(len(metrics))

        for i, (name, score) in enumerate(metrics):
            name_item = QTableWidgetItem(name)
            score_item = QTableWidgetItem(f"{score:.1f}/100")

            # Ajouter tooltip au nom de la métrique
            if name in self.metrics_data:
                name_item.setToolTip(self.metrics_data[name]["tooltip"])
                score_item.setToolTip(self.metrics_data[name]["tooltip"])

            # Couleur selon le score
            if score > 70:
                score_item.setBackground(QColor(0, 255, 136, 50))  # Vert
            elif score > 30:
                score_item.setBackground(QColor(255, 165, 0, 50))  # Orange
            else:
                score_item.setBackground(QColor(255, 68, 68, 50))  # Rouge

            self.metrics_table.setItem(i, 0, name_item)
            self.metrics_table.setItem(i, 1, score_item)

    # Méthode update_warnings supprimée - plus d'avertissements affichés

    # Méthode update_recommendations supprimée

    def update_details(self, results):
        """Met à jour l'analyse détaillée"""
        details_text = []

        # Informations générales
        details_text.append("=== ANALYSE DÉTAILLÉE ===\n")

        stability = results.get('time_stability', {})
        if stability:
            details_text.append(f"📈 STABILITÉ TEMPORELLE:")
            details_text.append(f"   Score: {stability.get('score', 0):.1f}/100")
            details_text.append(f"   Statut: {stability.get('stability', 'N/A')}")
            details_text.append(f"   Détails: {stability.get('details', 'N/A')}")
            details_text.append("")

        cv = results.get('cross_validation', {})
        if cv:
            details_text.append(f"🎯 VALIDATION CROISÉE:")
            details_text.append(f"   Score: {cv.get('score', 0):.1f}/100")
            details_text.append(f"   Généralisation: {cv.get('generalization', 'N/A')}")
            details_text.append(f"   Détails: {cv.get('details', 'N/A')}")
            details_text.append("")

        robustness = results.get('robustness_test', {})
        if robustness:
            details_text.append(f"🔧 ROBUSTESSE:")
            details_text.append(f"   Score: {robustness.get('score', 0):.1f}/100")
            details_text.append(f"   Robustesse: {robustness.get('robustness', 'N/A')}")
            details_text.append(f"   Sensibilité: {robustness.get('sensitivity', 0):.1f}%")
            details_text.append("")

        correlation = results.get('correlation_analysis', {})
        if correlation:
            details_text.append(f"📊 ANALYSE CORRÉLATION:")
            details_text.append(f"   Score: {correlation.get('score', 0):.1f}/100")
            details_text.append(f"   Corrélation: {correlation.get('correlation', 0):.3f}")
            details_text.append(f"   Niveau: {correlation.get('correlation_level', 'N/A')}")
            details_text.append("")

        # Timestamps
        details_text.append(f"⏰ Dernière analyse: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.details_text.setPlainText("\n".join(details_text))

    def update_summary_chart(self, results):
        """Met à jour le graphique de synthèse moderne"""
        self.summary_chart.clear()

        # Configuration globale moderne
        self.summary_chart.figure.patch.set_facecolor('#0f1419')

        # Créer un graphique circulaire moderne avec les scores
        detailed = results.get('detailed_analysis', {})
        overfitting_score = results.get('overfitting_score', 0)

        # Créer une grille simple 2x1
        gs = self.summary_chart.figure.add_gridspec(2, 1, hspace=0.3, height_ratios=[0.5, 1.5])

        # 1. Score principal (simple texte en haut)
        ax_main = self.summary_chart.figure.add_subplot(gs[0])
        self.create_circular_gauge(ax_main, overfitting_score)

        # 2. Barres des métriques détaillées (prend plus de place)
        ax_bars = self.summary_chart.figure.add_subplot(gs[1])
        self.create_modern_bars(ax_bars, detailed)

        self.summary_chart.canvas.draw()

    def create_circular_gauge(self, ax, score):
        """Zone simple - le score est déjà affiché à gauche"""
        # Couleurs selon le score
        if score < 15:
            level = 'EXCELLENT'
            color = '#10b981'
        elif score < 30:
            level = 'BON'
            color = '#06b6d4'
        elif score < 60:
            level = 'MOYEN'
            color = '#f59e0b'
        else:
            level = 'DANGEREUX'
            color = '#ef4444'

        # Juste un message simple au centre avec couleur
        ax.text(0.5, 0.5, f'Risque {level}', ha='center', va='center',
               fontsize=20, color=color, fontweight='bold', transform=ax.transAxes)

        # Configuration minimale
        ax.axis('off')
        ax.set_facecolor('#0f1419')

    def create_modern_bars(self, ax, detailed):
        """Crée des barres modernes pour les métriques détaillées"""
        # Ordre inversé pour correspondre visuellement au tableau (de haut en bas)
        categories = ['Extrêmes', 'Corrélations', 'Robustesse', 'Validation', 'Stabilité']
        scores = [
            detailed.get('extreme_allocation_score', 0),
            detailed.get('correlation_score', 0),
            detailed.get('robustness_score', 0),
            detailed.get('cv_score', 0),
            detailed.get('stability_score', 0)
        ]

        # Couleurs gradient modernes
        colors = []
        for score in scores:
            if score > 70:
                colors.append('#10b981')  # Vert
            elif score > 50:
                colors.append('#06b6d4')  # Cyan
            elif score > 30:
                colors.append('#f59e0b')  # Orange
            else:
                colors.append('#ef4444')  # Rouge

        # Créer les barres avec effet gradient
        y_pos = np.arange(len(categories))
        bars = ax.barh(y_pos, scores, color=colors, alpha=0.8, height=0.6)

        # Ajouter des effets visuels
        for i, (bar, score) in enumerate(zip(bars, scores)):
            # Bordure
            bar.set_edgecolor('white')
            bar.set_linewidth(0.5)

            # Texte avec le score
            ax.text(score + 2, i, f'{score:.0f}',
                   va='center', ha='left', fontweight='bold', color='white', fontsize=11)

        # Styling moderne
        ax.set_yticks(y_pos)
        ax.set_yticklabels(categories, color='white', fontsize=10)
        ax.set_xlim(0, 100)
        ax.set_xlabel('Score (0-100)', color='white', fontsize=11)

        # Grille subtile
        ax.grid(True, axis='x', alpha=0.2, color='white')
        ax.set_facecolor('#1a202c')

        # Zones de couleur en arrière-plan
        ax.axvspan(0, 30, alpha=0.1, color='red')
        ax.axvspan(30, 70, alpha=0.1, color='orange')
        ax.axvspan(70, 100, alpha=0.1, color='green')

        # Labels des zones
        ax.text(15, len(categories), 'FAIBLE', ha='center', va='bottom',
               color='#ef4444', fontsize=8, alpha=0.7)
        ax.text(50, len(categories), 'MOYEN', ha='center', va='bottom',
               color='#f59e0b', fontsize=8, alpha=0.7)
        ax.text(85, len(categories), 'BON', ha='center', va='bottom',
               color='#10b981', fontsize=8, alpha=0.7)

        ax.tick_params(colors='white', labelsize=9)
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # Méthode auto_analyze supprimée - plus d'analyse automatique

    def get_quick_status(self):
        """Retourne un status rapide pour la barre de statut"""
        if not self.current_results:
            return "Analyse d'overfitting non effectuée"

        score = self.current_results.get('overfitting_score', 0)
        risk = self.current_results.get('risk_level', 'INCONNU')

        if risk == 'FAIBLE':
            return f"✅ Overfitting: {score:.0f}% (Risque faible)"
        elif risk == 'MODERE':
            return f"⚠️ Overfitting: {score:.0f}% (Risque modéré)"
        else:
            return f"🚨 Overfitting: {score:.0f}% (Risque élevé)"