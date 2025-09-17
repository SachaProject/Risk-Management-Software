"""
Vue Graphiques AVANCÉE - Version PROFESSIONNELLE
Tous les graphiques de corrélation, performance et analyse avec les VRAIES données
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QGroupBox, QLabel, QTabWidget, QSplitter,
                            QGridLayout, QScrollArea, QFrame, QToolTip)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from .styles import AppStyles

# Import matplotlib pour les graphiques
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
    
    # Seaborn optionnel pour les heatmaps
    try:
        import seaborn as sns
        SEABORN_AVAILABLE = True
    except ImportError:
        SEABORN_AVAILABLE = False
        
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    SEABORN_AVAILABLE = False

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy import stats


class ProChartWidget(QWidget):
    """Widget de graphique professionnel avec thème dark"""
    
    def __init__(self, figure_size=(10, 6), dpi=100):
        super().__init__()
        self.figure = Figure(figsize=figure_size, dpi=dpi, facecolor='#1a1f2e')
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Configuration du style dark professionnel
        self.setup_dark_theme()
        
    def setup_dark_theme(self):
        """Configure le thème dark professionnel"""
        plt.style.use('dark_background')
        self.figure.patch.set_facecolor('#1a1f2e')
        
        # Palette de couleurs professionnelles
        self.colors = {
            'primary': '#00d9ff',
            'success': '#00ff88',
            'warning': '#ffa500',
            'danger': '#ff4444',
            'info': '#667eea',
            'grid': '#2d3748',
            'text': '#e2e8f0',
            'bg': '#1a1f2e'
        }
        
    def clear(self):
        """Efface le graphique"""
        self.figure.clear()
        self.canvas.draw()


class AdvancedChartsView(QWidget):
    """Vue avancée pour les graphiques professionnels avec vraies données"""
    
    def __init__(self):
        super().__init__()
        self.strategy_data = {}
        self.correlation_matrix = None
        self.is_visible = False
        self.init_ui()
        
        # Timer pour mise à jour automatique
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all_charts)
        self.update_timer.start(60000)  # Update toutes les minutes
        
    def showEvent(self, event):
        """Appelé quand l'onglet devient visible"""
        super().showEvent(event)
        if not self.is_visible:
            self.is_visible = True
            # Forcer une mise à jour immédiate quand l'onglet devient visible
            QTimer.singleShot(1000, self.update_all_charts)
        
    def init_ui(self):
        """Initialise l'interface avec tous les graphiques pro"""
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
                color: #00d9ff;
            }
            QTabWidget::pane {
                border: 1px solid #2d3748;
                background-color: #1a1f2e;
            }
            QTabBar::tab {
                background-color: #2d3748;
                color: #cbd5e0;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1a1f2e;
                color: #00d9ff;
                border-bottom: 2px solid #00d9ff;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Header avec titre et actions
        header = self.create_header()
        layout.addWidget(header)
        
        # Onglets techniques uniquement
        self.tab_widget = QTabWidget()
        
        # 1. Impact de la formule (principal)
        self.formula_tab = self.create_formula_analysis_tab()
        self.tab_widget.addTab(self.formula_tab, "🧮 Impact Formule")
        
        # 2. Corrélations
        self.correlation_tab = self.create_correlation_tab()
        self.tab_widget.addTab(self.correlation_tab, "🔗 Corrélations")
        
        # 3. Métriques de qualité
        self.quality_tab = self.create_quality_metrics_tab()
        self.tab_widget.addTab(self.quality_tab, "📊 Qualité Strategies")
        
        layout.addWidget(self.tab_widget)
        
        # Chargement initial après un court délai
        QTimer.singleShot(500, self.update_all_charts)
        
    def create_header(self):
        """Crée le header minimaliste"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1a1f2e;
                border-bottom: 2px solid #2d3748;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # Titre
        title = QLabel("🎯 ANALYSE TECHNIQUE DES FORMULES")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #00d9ff;")
        
        # Status seul
        self.status_label = QLabel("⏳ Chargement...")
        self.status_label.setStyleSheet("color: #cbd5e0;")
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.status_label)
        
        return header
        
        
    def create_correlation_tab(self):
        """Onglet des corrélations avec heatmap et scatter plots"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # Heatmap de corrélation principale
        heatmap_group = QGroupBox("🔥 Matrice de Corrélation")
        heatmap_group.setToolTip("Montre les corrélations entre les rendements des différentes stratégies. "
                                "Rouge = corrélation forte positive, Bleu = corrélation négative, "
                                "Blanc = pas de corrélation. Idéal: diversification avec corrélations faibles.")
        heatmap_layout = QVBoxLayout(heatmap_group)
        self.correlation_heatmap = ProChartWidget((10, 8))
        heatmap_layout.addWidget(self.correlation_heatmap)
        layout.addWidget(heatmap_group, 0, 0, 2, 2)
        
        # Scatter plot métriques
        scatter_group = QGroupBox("📊 Relations entre Métriques")
        scatter_group.setToolTip("Visualise les relations entre différentes métriques de performance. "
                                "Chaque point = une stratégie. Permet d'identifier les stratégies outliers "
                                "et les patterns dans les performances. Utile pour valider les corrélations.")
        scatter_layout = QVBoxLayout(scatter_group)
        self.metrics_scatter = ProChartWidget((8, 6))
        scatter_layout.addWidget(self.metrics_scatter)
        layout.addWidget(scatter_group, 0, 2, 1, 1)
        
        # Corrélation rolling
        rolling_group = QGroupBox("📈 Corrélation Glissante")
        rolling_group.setToolTip("Evolution de la corrélation entre stratégies au fil du temps. "
                                "Permet de détecter les périodes où les stratégies deviennent plus/moins corrélées. "
                                "Important pour le risk management: corrélations élevées = risque concentré.")
        rolling_layout = QVBoxLayout(rolling_group)
        self.rolling_correlation = ProChartWidget((8, 4))
        rolling_layout.addWidget(self.rolling_correlation)
        layout.addWidget(rolling_group, 1, 2, 1, 1)
        
        return widget
        
    def create_performance_tab(self):
        """Onglet performance détaillée"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # Courbes d'équité
        equity_group = QGroupBox("💰 Courbes d'Équité Normalisées")
        equity_group.setToolTip("Evolution du capital normalisé (base 100) pour chaque stratégie. "
                                "Permet de comparer visuellement les performances relatives et la régularité. "
                                "Pente = rendement, lissage = faible volatilité, chutes = drawdowns.")
        equity_layout = QVBoxLayout(equity_group)
        self.equity_curves_chart = ProChartWidget((14, 6))
        equity_layout.addWidget(self.equity_curves_chart)
        layout.addWidget(equity_group, 0, 0, 1, 2)
        
        # Drawdown
        dd_group = QGroupBox("📉 Drawdown Comparatif")
        dd_group.setToolTip("Magnitude et durée des pertes maximales pour chaque stratégie. "
                           "Plus le drawdown est faible et court, plus la stratégie est stable. "
                           "Crucial pour évaluer le risque psychologique et de capital.")
        dd_layout = QVBoxLayout(dd_group)
        self.drawdown_chart = ProChartWidget((14, 4))
        dd_layout.addWidget(self.drawdown_chart)
        layout.addWidget(dd_group, 1, 0, 1, 2)
        
        # Performance mensuelle
        monthly_group = QGroupBox("📅 Performance Mensuelle")
        monthly_group.setToolTip("Rendements agrégés par mois pour identifier les patterns saisonniers. "
                                "Permet de détecter les mois historiquement forts/faibles. "
                                "Vert = mois profitable, Rouge = mois perdant.")
        monthly_layout = QVBoxLayout(monthly_group)
        self.monthly_returns_chart = ProChartWidget((7, 5))
        monthly_layout.addWidget(self.monthly_returns_chart)
        layout.addWidget(monthly_group, 2, 0, 1, 1)
        
        # Ratio rendement/risque
        ratio_group = QGroupBox("⚖️ Ratio Rendement/Risque")
        ratio_group.setToolTip("Positionnement de chaque stratégie sur l'axe Rendement vs Risque. "
                              "Idéal = coin supérieur gauche (haut rendement, faible risque). "
                              "La ligne d'efficience montre la frontière optimale.")
        ratio_layout = QVBoxLayout(ratio_group)
        self.risk_return_chart = ProChartWidget((7, 5))
        ratio_layout.addWidget(self.risk_return_chart)
        layout.addWidget(ratio_group, 2, 1, 1, 1)
        
        return widget
        
    def create_risk_tab(self):
        """Onglet analyse des risques"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # VaR et CVaR
        var_group = QGroupBox("💀 VaR et CVaR (95%)")
        var_layout = QVBoxLayout(var_group)
        self.var_chart = ProChartWidget((10, 5))
        var_layout.addWidget(self.var_chart)
        layout.addWidget(var_group, 0, 0, 1, 2)
        
        # Distribution des pertes
        loss_group = QGroupBox("📊 Distribution des Pertes")
        loss_layout = QVBoxLayout(loss_group)
        self.loss_distribution_chart = ProChartWidget((7, 5))
        loss_layout.addWidget(self.loss_distribution_chart)
        layout.addWidget(loss_group, 1, 0, 1, 1)
        
        # Stress test visuel
        stress_group = QGroupBox("🔥 Stress Test Scénarios")
        stress_layout = QVBoxLayout(stress_group)
        self.stress_test_chart = ProChartWidget((7, 5))
        stress_layout.addWidget(self.stress_test_chart)
        layout.addWidget(stress_group, 1, 1, 1, 1)
        
        return widget
        
    def create_formula_analysis_tab(self):
        """Onglet d'analyse technique de la formule"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # Allocation par stratégie (principal)
        allocation_group = QGroupBox("⚖️ Allocations Calculées par la Formule")
        allocation_layout = QVBoxLayout(allocation_group)
        self.formula_allocation_chart = ProChartWidget((14, 6))
        allocation_layout.addWidget(self.formula_allocation_chart)
        layout.addWidget(allocation_group, 0, 0, 1, 2)
        
        # Performance simulée avec allocations
        simulated_group = QGroupBox("📈 Performance Simulée (Allocations Appliquées)")
        simulated_layout = QVBoxLayout(simulated_group)
        self.simulated_performance_chart = ProChartWidget((7, 5))
        simulated_layout.addWidget(self.simulated_performance_chart)
        layout.addWidget(simulated_group, 1, 0, 1, 1)
        
        # Comparaison de formules
        comparison_group = QGroupBox("⚖️ Comparaison de Formules")
        comparison_layout = QVBoxLayout(comparison_group)
        self.formula_comparison_chart = ProChartWidget((7, 5))
        comparison_layout.addWidget(self.formula_comparison_chart)
        layout.addWidget(comparison_group, 1, 1, 1, 1)
        
        # Analyse de sensibilité
        sensitivity_group = QGroupBox("📊 Sensibilité aux Métriques")
        sensitivity_layout = QVBoxLayout(sensitivity_group)
        self.sensitivity_chart = ProChartWidget((14, 4))
        sensitivity_layout.addWidget(self.sensitivity_chart)
        layout.addWidget(sensitivity_group, 2, 0, 1, 2)
        
        return widget
        
    def create_quality_metrics_tab(self):
        """Onglet des métriques de qualité des stratégies"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # Radar des métriques
        radar_group = QGroupBox("🎯 Radar des Métriques de Qualité")
        radar_layout = QVBoxLayout(radar_group)
        self.metrics_radar_chart = ProChartWidget((8, 6))
        radar_layout.addWidget(self.metrics_radar_chart)
        layout.addWidget(radar_group, 0, 0, 1, 1)
        
        # Scatter Sharpe vs Win Rate
        scatter_group = QGroupBox("📊 Sharpe vs Win Rate")
        scatter_layout = QVBoxLayout(scatter_group)
        self.metrics_scatter = ProChartWidget((8, 6))
        scatter_layout.addWidget(self.metrics_scatter)
        layout.addWidget(scatter_group, 0, 1, 1, 1)
        
        # Distribution des rendements
        dist_group = QGroupBox("📈 Distribution des Rendements")
        dist_layout = QVBoxLayout(dist_group)
        self.returns_distribution_chart = ProChartWidget((8, 5))
        dist_layout.addWidget(self.returns_distribution_chart)
        layout.addWidget(dist_group, 1, 0, 1, 1)
        
        # Drawdown analysis
        dd_group = QGroupBox("📉 Analyse des Drawdowns")
        dd_layout = QVBoxLayout(dd_group)
        self.drawdown_analysis_chart = ProChartWidget((8, 5))
        dd_layout.addWidget(self.drawdown_analysis_chart)
        layout.addWidget(dd_group, 1, 1, 1, 1)
        
        return widget
        
    def get_real_strategy_data(self):
        """Récupère les VRAIES données des stratégies (pas de génération!)"""
        try:
            # Accéder au contrôleur principal
            widget = self
            main_window = None
            
            # Chercher la MainWindow dans la hiérarchie
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
                print("❌ Pas de MainWindow ou controller trouvé")
                return None
                
            controller = main_window.controller
            data_controller = controller.data_controller
            
            print(f"🔍 Debug info:")
            print(f"   - Main window: {main_window is not None}")
            print(f"   - Controller: {controller is not None}")
            print(f"   - Data controller: {data_controller is not None}")
            
            # Récupérer les modèles de trades (vraies données!)
            trade_models = data_controller.trade_models if data_controller else None
            strategy_models = data_controller.strategy_models if data_controller else None
            portfolio = controller.portfolio_controller.portfolio if controller else None
            
            print(f"📊 Trade models trouvés: {len(trade_models) if trade_models else 0}")
            print(f"🎯 Strategy models trouvés: {len(strategy_models) if strategy_models else 0}")
            
            # Si pas de trade models, essayer de charger automatiquement
            if not trade_models or len(trade_models) == 0:
                print("⚠️ Aucun trade model - tentative de chargement automatique...")
                csv_files = data_controller.scan_directory() if data_controller else []
                print(f"   CSV trouvés: {len(csv_files)}")
                
                if csv_files and data_controller:
                    loaded = data_controller.load_multiple_csv(csv_files)
                    print(f"   CSV chargés: {loaded}")
                    trade_models = data_controller.trade_models
                    strategy_models = data_controller.strategy_models
                    
            if not trade_models:
                print("❌ Aucun trade model trouvé après tentative de chargement")
                return None
                
            # Extraire les VRAIES données CSV
            real_data = {}
            
            for name, trade_model in trade_models.items():
                print(f"   Traitement: {name}")
                
                if trade_model.df is None or trade_model.df.empty:
                    print(f"      ❌ DataFrame vide ou None")
                    continue
                    
                df = trade_model.df.copy()
                
                # Calculer les vraies métriques depuis les trades
                stats = trade_model.get_statistics()
                returns = trade_model.get_returns()
                daily_returns = trade_model.get_daily_returns()
                
                print(f"      ✅ Stats: Sharpe={stats.get('sharpe_ratio', 0):.2f}, WR={stats.get('win_rate', 0):.2%}")
                
                # Récupérer l'allocation du portfolio
                allocation = 0
                if portfolio and hasattr(portfolio, 'allocations') and name in portfolio.allocations:
                    allocation = portfolio.allocations[name] * 100
                
                # Construire les données réelles
                real_data[name] = {
                    'df': df,  # DataFrame original des trades
                    'returns': returns,  # Rendements par trade
                    'daily_returns': daily_returns,  # Rendements quotidiens
                    'statistics': stats,  # Statistiques calculées
                    'allocation': allocation,
                    'dates': pd.to_datetime(df['Date Closed']) if 'Date Closed' in df else None,
                    'pl': df['P/L'].values if 'P/L' in df else None
                }
                
            print(f"✅ Données récupérées pour {len(real_data)} stratégies")
            return real_data
            
        except Exception as e:
            print(f"❌ Erreur dans get_real_strategy_data: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    def update_all_charts(self):
        """Met à jour TOUS les graphiques avec les VRAIES données"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        self.status_label.setText("⏳ Mise à jour...")
        
        # Récupérer les VRAIES données
        real_data = self.get_real_strategy_data()
        
        if not real_data:
            self.status_label.setText("⚠️ Aucune donnée CSV")
            return
            
        self.strategy_data = real_data
        
        # Mettre à jour tous les graphiques techniques
        self.update_formula_analysis(real_data)
        self.update_correlations(real_data)
        self.update_quality_metrics(real_data)
        
        self.status_label.setText(f"✅ {len(real_data)} stratégies - {datetime.now().strftime('%H:%M:%S')}")
        
        
    def get_current_formula_allocation(self, data):
        """Récupère l'allocation moyenne calculée par la formule actuelle"""
        try:
            # Accéder à la formule actuelle depuis le portfolio
            widget = self
            main_window = None
            
            for _ in range(10):
                widget = widget.parent() if widget else None
                if widget and widget.__class__.__name__ == 'MainWindow':
                    main_window = widget
                    break
                    
            if main_window and hasattr(main_window, 'portfolio_view'):
                current_formula = main_window.portfolio_view.formula_input.text().strip()
                if current_formula:
                    # Calculer l'allocation pour chaque stratégie
                    allocations = []
                    for strat_data in data.values():
                        stats = strat_data['statistics']
                        # Normaliser les métriques
                        metrics = {
                            'sharpe': stats.get('sharpe_ratio', 1.0),
                            'omega': 1.5,  # Valeur par défaut
                            'volatility': stats.get('volatility', 0.15),
                            'drawdown': abs(stats.get('max_drawdown', 0.1)),
                            'win_rate': stats.get('win_rate', 0.6),
                            'profit_factor': stats.get('profit_factor', 1.2),
                            'total_return': 0.1,  # Normalisé
                            'calmar': stats.get('calmar_ratio', 1.0),
                            'sortino': stats.get('sortino_ratio', 1.0)
                        }
                        
                        try:
                            result = eval(current_formula, {'__builtins__': {}}, metrics)
                            allocations.append(min(50, max(0, float(result))))  # Cap à 50%
                        except:
                            allocations.append(10)  # Valeur par défaut
                    
                    return np.mean(allocations) if allocations else 10
            
            return 10  # Valeur par défaut
            
        except Exception as e:
            return 10
            
    def update_formula_allocation_impact(self, data):
        """Met à jour le graphique d'impact de la formule"""
        self.formula_allocation_chart.clear()
        ax = self.formula_allocation_chart.figure.add_subplot(111)
        
        # Calculer les allocations pour chaque stratégie avec la formule
        names = []
        allocations = []
        sharpe_ratios = []
        
        for name, strat_data in data.items():
            stats = strat_data['statistics']
            allocation = self.calculate_strategy_allocation(stats)
            
            names.append(name)
            allocations.append(allocation)
            sharpe_ratios.append(stats.get('sharpe_ratio', 0))
        
        # Graphique en barres avec couleur selon le Sharpe
        colors = ['#00ff88' if s > 1 else '#00d9ff' if s > 0.5 else '#ffa500' if s > 0 else '#ff4444' for s in sharpe_ratios]
        
        bars = ax.bar(range(len(names)), allocations, color=colors, alpha=0.8, edgecolor='white')
        
        # Ajouter une ligne de référence à 10%
        ax.axhline(y=10, color='red', linestyle='--', alpha=0.5, label='Allocation Recommandée (10%)')
        
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha='right', color='white')
        ax.set_title('Allocation Calculée par la Formule (par Stratégie)', color='white', fontsize=14)
        ax.set_ylabel('Allocation (%)', color='white')
        ax.legend()
        ax.grid(True, alpha=0.2, axis='y')
        ax.set_facecolor('#1a1f2e')
        ax.tick_params(colors='white')
        
        # Ajouter les valeurs sur les barres
        for bar, allocation, sharpe in zip(bars, allocations, sharpe_ratios):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{allocation:.1f}%\n(S:{sharpe:.2f})', ha='center', va='bottom', 
                   color='white', fontsize=9, fontweight='bold')
        
        self.formula_allocation_chart.canvas.draw()
        
    def calculate_strategy_allocation(self, stats):
        """Calcule l'allocation d'une stratégie avec la formule actuelle"""
        try:
            # Accéder à la formule
            widget = self
            main_window = None
            
            for _ in range(10):
                widget = widget.parent() if widget else None
                if widget and widget.__class__.__name__ == 'MainWindow':
                    main_window = widget
                    break
                    
            if main_window and hasattr(main_window, 'portfolio_view'):
                current_formula = main_window.portfolio_view.formula_input.text().strip()
                if current_formula:
                    metrics = {
                        'sharpe': stats.get('sharpe_ratio', 1.0),
                        'omega': 1.5,
                        'volatility': stats.get('volatility', 0.15),
                        'drawdown': abs(stats.get('max_drawdown', 0.1)),
                        'win_rate': stats.get('win_rate', 0.6),
                        'profit_factor': stats.get('profit_factor', 1.2),
                        'total_return': 0.1,
                        'calmar': stats.get('calmar_ratio', 1.0),
                        'sortino': stats.get('sortino_ratio', 1.0)
                    }
                    
                    result = eval(current_formula, {'__builtins__': {}}, metrics)
                    return min(50, max(0, float(result)))
                    
        except Exception as e:
            pass
            
        # Formule par défaut simple
        sharpe = stats.get('sharpe_ratio', 1.0)
        return min(20, max(2, sharpe * 10))
        
    def update_simulated_performance(self, data):
        """Met à jour la performance simulée avec les allocations de la formule"""
        self.simulated_performance_chart.clear()
        ax = self.simulated_performance_chart.figure.add_subplot(111)
        
        colors = ['#00d9ff', '#00ff88', '#ffa500', '#ff4444', '#667eea', '#f368e0']
        
        # Simuler la performance avec les allocations calculées
        for i, (name, strat_data) in enumerate(data.items()):
            stats = strat_data['statistics']
            allocation_pct = self.calculate_strategy_allocation(stats) / 100
            
            # Prendre les rendements réels et les multiplier par l'allocation
            if 'returns' in strat_data and strat_data['returns'] is not None:
                returns = np.array(strat_data['returns']) * allocation_pct
                equity_curve = np.cumprod(1 + returns)
                
                ax.plot(range(len(equity_curve)), equity_curve, label=f"{name} ({allocation_pct*100:.1f}%)",
                       color=colors[i % len(colors)], linewidth=2, alpha=0.9)
        
        ax.set_title('Performance Simulée avec Allocations Formule', color='white', fontsize=14)
        ax.set_xlabel('Nombre de Trades', color='white')
        ax.set_ylabel('Équité (Base 1)', color='white')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.2)
        ax.set_facecolor('#1a1f2e')
        ax.tick_params(colors='white')
        
        self.simulated_performance_chart.canvas.draw()
        
    def update_returns_distribution(self, data):
        """Met à jour la distribution des rendements"""
        self.returns_distribution_chart.clear()
        ax = self.returns_distribution_chart.figure.add_subplot(111)
        
        # Combiner tous les rendements
        all_returns = []
        for strat_data in data.values():
            if strat_data['returns'] is not None:
                all_returns.extend(strat_data['returns'])
        
        if all_returns:
            # Histogramme avec courbe de distribution
            n, bins, patches = ax.hist(all_returns, bins=50, alpha=0.7, 
                                      color='#00d9ff', edgecolor='#667eea')
            
            # Ajouter une courbe de distribution normale
            mu, std = np.mean(all_returns), np.std(all_returns)
            xmin, xmax = ax.get_xlim()
            x = np.linspace(xmin, xmax, 100)
            p = stats.norm.pdf(x, mu, std) * len(all_returns) * (bins[1] - bins[0])
            ax.plot(x, p, 'r-', linewidth=2, label=f'Normal (μ={mu:.2f}, σ={std:.2f})')
            
            ax.set_title('Distribution Réelle des Rendements', color='white')
            ax.set_xlabel('Rendement (%)', color='white')
            ax.set_ylabel('Fréquence', color='white')
            ax.legend()
            ax.grid(True, alpha=0.2)
            ax.set_facecolor('#1a1f2e')
            ax.tick_params(colors='white')
        
        self.returns_distribution_chart.canvas.draw()
        
        
    def update_metrics_radar(self, data):
        """Met à jour le radar des métriques"""
        self.metrics_radar_chart.clear()
        ax = self.metrics_radar_chart.figure.add_subplot(111, projection='polar')
        
        # Métriques à afficher
        metrics = ['Sharpe', 'Win Rate', 'Profit Factor', 'Sortino', 'Calmar']
        
        # Calculer les moyennes
        avg_values = []
        for metric in ['sharpe_ratio', 'win_rate', 'profit_factor', 'sortino_ratio', 'calmar_ratio']:
            values = [d['statistics'].get(metric, 0) for d in data.values()]
            avg_values.append(np.mean(values) if values else 0)
        
        # Normaliser les valeurs (0-100)
        normalized_values = [
            min(100, max(0, avg_values[0] * 33)),  # Sharpe (0-3 -> 0-100)
            avg_values[1],  # Win rate déjà en %
            min(100, max(0, avg_values[2] * 33)),  # Profit factor (0-3 -> 0-100)
            min(100, max(0, avg_values[3] * 33)),  # Sortino (0-3 -> 0-100)
            min(100, max(0, avg_values[4] * 33))   # Calmar (0-3 -> 0-100)
        ]
        
        # Angles pour le radar
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False)
        normalized_values += [normalized_values[0]]  # Fermer le polygone
        angles = np.concatenate((angles, [angles[0]]))
        
        # Tracer le radar
        ax.plot(angles, normalized_values, 'o-', linewidth=2, color='#00d9ff')
        ax.fill(angles, normalized_values, alpha=0.25, color='#00d9ff')
        ax.set_thetagrids(angles[:-1] * 180/np.pi, metrics, color='white')
        ax.set_ylim(0, 100)
        ax.set_title('Radar des Métriques Moyennes', color='white', y=1.08)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#1a1f2e')
        
        self.metrics_radar_chart.canvas.draw()
        
    def update_correlations(self, data):
        """Met à jour les graphiques de corrélation"""
        if len(data) < 2:
            return
            
        # Créer la matrice de corrélation
        returns_dict = {}
        for name, strat_data in data.items():
            if strat_data['daily_returns'] is not None and len(strat_data['daily_returns']) > 0:
                returns_dict[name] = pd.Series(strat_data['daily_returns'])
        
        if len(returns_dict) < 2:
            return
            
        returns_df = pd.DataFrame(returns_dict)
        self.correlation_matrix = returns_df.corr()
        
        # Heatmap de corrélation
        self.correlation_heatmap.clear()
        ax = self.correlation_heatmap.figure.add_subplot(111)
        
        if SEABORN_AVAILABLE:
            # Utiliser seaborn si disponible (plus joli)
            sns.heatmap(self.correlation_matrix, annot=True, fmt='.2f', 
                       cmap='coolwarm', center=0, square=True,
                       cbar_kws={'label': 'Corrélation'}, ax=ax,
                       vmin=-1, vmax=1)
        else:
            # Heatmap manuelle avec matplotlib
            im = ax.imshow(self.correlation_matrix.values, cmap='coolwarm', 
                          aspect='auto', vmin=-1, vmax=1)
            
            # Ajouter les valeurs dans les cellules
            for i in range(len(self.correlation_matrix)):
                for j in range(len(self.correlation_matrix.columns)):
                    text = ax.text(j, i, f'{self.correlation_matrix.iloc[i, j]:.2f}',
                                 ha="center", va="center", color="white" if abs(self.correlation_matrix.iloc[i, j]) > 0.5 else "black")
            
            # Configurer les axes
            ax.set_xticks(range(len(self.correlation_matrix.columns)))
            ax.set_yticks(range(len(self.correlation_matrix)))
            ax.set_xticklabels(self.correlation_matrix.columns, rotation=45, ha='right')
            ax.set_yticklabels(self.correlation_matrix.index)
            
            # Ajouter la colorbar
            plt.colorbar(im, ax=ax, label='Corrélation')
        
        ax.set_title('Matrice de Corrélation des Stratégies', color='white', fontsize=14)
        ax.tick_params(colors='white')
        
        self.correlation_heatmap.canvas.draw()
        
        # Scatter plot des métriques
        self.update_metrics_scatter(data)
        
        # Corrélation rolling
        self.update_rolling_correlation(data)
        
        # Afficher la corrélation moyenne dans le status
        avg_corr = self.correlation_matrix.values[np.triu_indices_from(self.correlation_matrix.values, k=1)].mean()
        
    def update_metrics_scatter(self, data):
        """Met à jour le scatter plot des métriques"""
        self.metrics_scatter.clear()
        ax = self.metrics_scatter.figure.add_subplot(111)
        
        # Extraire Sharpe et rendements totaux
        sharpes = []
        returns = []
        names = []
        
        for name, strat_data in data.items():
            sharpes.append(strat_data['statistics'].get('sharpe_ratio', 0))
            returns.append(strat_data['statistics'].get('total_pl', 0))
            names.append(name)
        
        colors = ['#00ff88' if r > 0 else '#ff4444' for r in returns]
        sizes = [abs(r)/100 for r in returns]  # Taille proportionnelle au P/L
        
        scatter = ax.scatter(sharpes, returns, c=colors, s=sizes, alpha=0.6, edgecolors='white')
        
        # Ajouter les noms
        for i, name in enumerate(names):
            ax.annotate(name, (sharpes[i], returns[i]), 
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, color='white', alpha=0.7)
        
        ax.set_xlabel('Sharpe Ratio', color='white')
        ax.set_ylabel('P/L Total (€)', color='white')
        ax.set_title('Relation Sharpe vs Rendement', color='white')
        ax.grid(True, alpha=0.2)
        ax.set_facecolor('#1a1f2e')
        ax.tick_params(colors='white')
        
        # Ajouter une ligne de tendance
        if len(sharpes) > 1:
            z = np.polyfit(sharpes, returns, 1)
            p = np.poly1d(z)
            ax.plot(sorted(sharpes), p(sorted(sharpes)), "r--", alpha=0.5, label='Tendance')
            ax.legend()
        
        self.metrics_scatter.canvas.draw()
        
    def update_rolling_correlation(self, data):
        """Met à jour la corrélation glissante"""
        self.rolling_correlation.clear()
        ax = self.rolling_correlation.figure.add_subplot(111)
        
        # Prendre les 2 premières stratégies pour la corrélation rolling
        if len(data) >= 2:
            names = list(data.keys())[:2]
            returns1 = data[names[0]]['daily_returns']
            returns2 = data[names[1]]['daily_returns']
            
            if returns1 is not None and returns2 is not None:
                # Calculer la corrélation rolling sur 30 jours
                window = 30
                if len(returns1) > window and len(returns2) > window:
                    min_len = min(len(returns1), len(returns2))
                    r1 = pd.Series(returns1[:min_len])
                    r2 = pd.Series(returns2[:min_len])
                    
                    rolling_corr = r1.rolling(window).corr(r2)
                    
                    ax.plot(rolling_corr, color='#00d9ff', linewidth=2)
                    ax.axhline(y=0, color='white', linestyle='--', alpha=0.3)
                    ax.fill_between(range(len(rolling_corr)), rolling_corr, 0, 
                                   where=(rolling_corr >= 0), color='#00ff88', alpha=0.3)
                    ax.fill_between(range(len(rolling_corr)), rolling_corr, 0,
                                   where=(rolling_corr < 0), color='#ff4444', alpha=0.3)
                    
                    ax.set_title(f'Corrélation Glissante (30j) : {names[0]} vs {names[1]}', color='white')
                    ax.set_xlabel('Jours', color='white')
                    ax.set_ylabel('Corrélation', color='white')
                    ax.set_ylim(-1, 1)
                    ax.grid(True, alpha=0.2)
                    ax.set_facecolor('#1a1f2e')
                    ax.tick_params(colors='white')
        
        self.rolling_correlation.canvas.draw()
        
    def update_performance(self, data):
        """Met à jour les graphiques de performance"""
        # Courbes d'équité normalisées
        self.equity_curves_chart.clear()
        ax = self.equity_curves_chart.figure.add_subplot(111)
        
        colors = ['#00d9ff', '#00ff88', '#ffa500', '#ff4444', '#667eea', '#f368e0']
        
        for i, (name, strat_data) in enumerate(data.items()):
            if strat_data['pl'] is not None:
                # Normaliser en base 100
                cumsum = np.cumsum(strat_data['pl'])
                if cumsum[0] != 0:
                    normalized = (cumsum / abs(cumsum[0])) * 100
                else:
                    normalized = cumsum
                
                ax.plot(range(len(normalized)), normalized, label=name,
                       color=colors[i % len(colors)], linewidth=2, alpha=0.9)
        
        ax.set_title('Courbes d\'Équité Normalisées (Base 100)', color='white', fontsize=14)
        ax.set_xlabel('Nombre de Trades', color='white')
        ax.set_ylabel('Performance (%)', color='white')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.2)
        ax.set_facecolor('#1a1f2e')
        ax.tick_params(colors='white')
        
        self.equity_curves_chart.canvas.draw()
        
        # Drawdown
        self.update_drawdown(data)
        
        # Performance mensuelle
        self.update_monthly_returns(data)
        
        # Risk/Return
        self.update_risk_return(data)
        
    def update_drawdown(self, data):
        """Met à jour le graphique de drawdown"""
        self.drawdown_chart.clear()
        ax = self.drawdown_chart.figure.add_subplot(111)
        
        colors = ['#ff4444', '#ffa500', '#ff6b6b', '#ff9999', '#ffcccc']
        
        for i, (name, strat_data) in enumerate(data.items()):
            if strat_data['pl'] is not None:
                cumsum = np.cumsum(strat_data['pl'])
                peak = np.maximum.accumulate(cumsum)
                drawdown = (cumsum - peak) / np.maximum(peak, 1) * 100
                
                ax.fill_between(range(len(drawdown)), drawdown, 0,
                               color=colors[i % len(colors)], alpha=0.6, label=name)
        
        ax.set_title('Drawdown Comparatif (%)', color='white')
        ax.set_xlabel('Nombre de Trades', color='white')
        ax.set_ylabel('Drawdown (%)', color='white')
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.2)
        ax.set_facecolor('#1a1f2e')
        ax.tick_params(colors='white')
        
        self.drawdown_chart.canvas.draw()
        
    def update_monthly_returns(self, data):
        """Met à jour les rendements mensuels"""
        self.monthly_returns_chart.clear()
        ax = self.monthly_returns_chart.figure.add_subplot(111)
        
        # Pour simplifier, on prend la première stratégie
        if data:
            first_strat = list(data.values())[0]
            if first_strat['df'] is not None and 'Date Closed' in first_strat['df']:
                df = first_strat['df'].copy()
                df['Date Closed'] = pd.to_datetime(df['Date Closed'])
                df['Month'] = df['Date Closed'].dt.to_period('M')
                
                monthly = df.groupby('Month')['P/L'].sum()
                
                colors = ['#00ff88' if v > 0 else '#ff4444' for v in monthly.values]
                bars = ax.bar(range(len(monthly)), monthly.values, color=colors, alpha=0.8)
                
                ax.set_title(f'Rendements Mensuels - {list(data.keys())[0]}', color='white')
                ax.set_xlabel('Mois', color='white')
                ax.set_ylabel('P/L (€)', color='white')
                ax.grid(True, alpha=0.2, axis='y')
                ax.set_facecolor('#1a1f2e')
                ax.tick_params(colors='white')
                
                # Rotation des labels
                if len(monthly) > 0:
                    ax.set_xticks(range(len(monthly)))
                    ax.set_xticklabels([str(m) for m in monthly.index], rotation=45, ha='right')
        
        self.monthly_returns_chart.canvas.draw()
        
    def update_risk_return(self, data):
        """Met à jour le graphique risk/return"""
        self.risk_return_chart.clear()
        ax = self.risk_return_chart.figure.add_subplot(111)
        
        # Extraire volatilité et rendements
        vols = []
        returns = []
        names = []
        
        for name, strat_data in data.items():
            vols.append(strat_data['statistics'].get('volatility', 0) * 100)
            returns.append(strat_data['statistics'].get('annualized_return', 0) * 100)
            names.append(name)
        
        colors = ['#00ff88' if r > 0 else '#ff4444' for r in returns]
        
        ax.scatter(vols, returns, c=colors, s=100, alpha=0.6, edgecolors='white')
        
        # Ajouter les noms
        for i, name in enumerate(names):
            ax.annotate(name, (vols[i], returns[i]),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, color='white')
        
        # Ajouter la frontière efficiente (simplifiée)
        if len(vols) > 2:
            ax.plot([0, max(vols)], [0, max(vols) * 0.5], 'r--', alpha=0.3, label='Ratio 0.5')
            ax.plot([0, max(vols)], [0, max(vols) * 1.0], 'y--', alpha=0.3, label='Ratio 1.0')
        
        ax.set_xlabel('Volatilité (%)', color='white')
        ax.set_ylabel('Rendement Annualisé (%)', color='white')
        ax.set_title('Profil Rendement/Risque', color='white')
        ax.legend()
        ax.grid(True, alpha=0.2)
        ax.set_facecolor('#1a1f2e')
        ax.tick_params(colors='white')
        
        self.risk_return_chart.canvas.draw()
        
    def update_risk_analysis(self, data):
        """Met à jour l'analyse des risques"""
        # VaR et CVaR
        self.update_var_analysis(data)
        
        # Distribution des pertes
        self.update_loss_distribution(data)
        
        # Stress test
        self.update_stress_test(data)
        
    def update_var_analysis(self, data):
        """Met à jour l'analyse VaR/CVaR"""
        self.var_chart.clear()
        ax = self.var_chart.figure.add_subplot(111)
        
        names = []
        vars_95 = []
        cvars_95 = []
        
        for name, strat_data in data.items():
            if strat_data['returns'] is not None and len(strat_data['returns']) > 0:
                returns = strat_data['returns']
                var_95 = np.percentile(returns, 5)
                cvar_95 = np.mean([r for r in returns if r <= var_95])
                
                names.append(name)
                vars_95.append(var_95)
                cvars_95.append(cvar_95)
        
        if names:
            x = np.arange(len(names))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, vars_95, width, label='VaR 95%', color='#ffa500', alpha=0.8)
            bars2 = ax.bar(x + width/2, cvars_95, width, label='CVaR 95%', color='#ff4444', alpha=0.8)
            
            ax.set_xlabel('Stratégies', color='white')
            ax.set_ylabel('Perte Potentielle (%)', color='white')
            ax.set_title('Value at Risk (VaR) et Conditional VaR à 95%', color='white')
            ax.set_xticks(x)
            ax.set_xticklabels(names, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.2, axis='y')
            ax.set_facecolor('#1a1f2e')
            ax.tick_params(colors='white')
        
        self.var_chart.canvas.draw()
        
    def update_loss_distribution(self, data):
        """Met à jour la distribution des pertes"""
        self.loss_distribution_chart.clear()
        ax = self.loss_distribution_chart.figure.add_subplot(111)
        
        # Collecter toutes les pertes
        all_losses = []
        for strat_data in data.values():
            if strat_data['pl'] is not None:
                losses = [p for p in strat_data['pl'] if p < 0]
                all_losses.extend(losses)
        
        if all_losses:
            ax.hist(all_losses, bins=30, color='#ff4444', alpha=0.7, edgecolor='#ff6666')
            
            # Ajouter des statistiques
            mean_loss = np.mean(all_losses)
            median_loss = np.median(all_losses)
            max_loss = min(all_losses)
            
            ax.axvline(mean_loss, color='yellow', linestyle='--', label=f'Moyenne: {mean_loss:.0f}€')
            ax.axvline(median_loss, color='orange', linestyle='--', label=f'Médiane: {median_loss:.0f}€')
            ax.axvline(max_loss, color='red', linestyle='--', label=f'Max: {max_loss:.0f}€')
            
            ax.set_title('Distribution des Pertes Réelles', color='white')
            ax.set_xlabel('Perte (€)', color='white')
            ax.set_ylabel('Fréquence', color='white')
            ax.legend()
            ax.grid(True, alpha=0.2)
            ax.set_facecolor('#1a1f2e')
            ax.tick_params(colors='white')
        
        self.loss_distribution_chart.canvas.draw()
        
    def update_stress_test(self, data):
        """Met à jour le stress test visuel"""
        self.stress_test_chart.clear()
        ax = self.stress_test_chart.figure.add_subplot(111)
        
        # Scénarios de stress
        scenarios = ['Normal', 'Correction -10%', 'Bear Market -20%', 'Krach -30%', 'Crise Majeure -40%']
        multipliers = [1.0, 0.9, 0.8, 0.7, 0.6]
        
        # Calculer l'impact pour chaque stratégie
        strategy_impacts = []
        
        for name, strat_data in data.items():
            if strat_data['statistics'].get('total_pl', 0) > 0:
                base_pl = strat_data['statistics']['total_pl']
                impacts = [base_pl * m for m in multipliers]
                strategy_impacts.append((name, impacts))
        
        if strategy_impacts:
            # Prendre les 3 meilleures stratégies
            top_strategies = strategy_impacts[:3]
            
            x = np.arange(len(scenarios))
            width = 0.25
            colors = ['#00d9ff', '#00ff88', '#ffa500']
            
            for i, (name, impacts) in enumerate(top_strategies):
                offset = (i - 1) * width
                ax.bar(x + offset, impacts, width, label=name, 
                      color=colors[i], alpha=0.8)
            
            ax.set_xlabel('Scénarios', color='white')
            ax.set_ylabel('P/L Estimé (€)', color='white')
            ax.set_title('Stress Test - Impact des Scénarios', color='white')
            ax.set_xticks(x)
            ax.set_xticklabels(scenarios, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.2, axis='y')
            ax.set_facecolor('#1a1f2e')
            ax.tick_params(colors='white')
        
        self.stress_test_chart.canvas.draw()
        
    def update_formula_analysis(self, data):
        """Met à jour l'analyse technique de la formule"""
        # Allocations calculées par la formule
        self.update_formula_allocation_impact(data)
        
        # Performance simulée avec allocations
        self.update_simulated_performance(data)
        
        # Comparaison de formules
        self.update_formula_comparison(data)
        
        # Sensibilité aux métriques
        self.update_sensitivity_analysis(data)
        
    def update_quality_metrics(self, data):
        """Met à jour les métriques de qualité"""
        # Radar des métriques
        self.update_metrics_radar(data)
        
        # Scatter Sharpe vs Win Rate
        self.update_metrics_scatter(data)
        
        # Distribution des rendements
        self.update_returns_distribution(data)
        
        # Analyse des drawdowns
        self.update_drawdown_analysis(data)
        
    def update_formula_comparison(self, data):
        """Compare différentes formules sur les mêmes données"""
        self.formula_comparison_chart.clear()
        ax = self.formula_comparison_chart.figure.add_subplot(111)
        
        # Tester différentes formules
        formulas = [
            ('Conservative', 'sharpe / (drawdown * 10)'),
            ('Balanced', 'sharpe * win_rate'),
            ('Aggressive', 'sharpe * 15'),
            ('Custom', self.get_current_formula() or 'sharpe * 10')
        ]
        
        formula_results = []
        
        for formula_name, formula in formulas:
            avg_allocation = self.calculate_formula_average(data, formula)
            formula_results.append((formula_name, avg_allocation))
        
        # Graphique en barres
        names = [f[0] for f in formula_results]
        values = [f[1] for f in formula_results]
        colors = ['#00ff88', '#00d9ff', '#ffa500', '#ff4444']
        
        bars = ax.bar(names, values, color=colors[:len(names)], alpha=0.8, edgecolor='white')
        
        # Ligne de référence à 10%
        ax.axhline(y=10, color='white', linestyle='--', alpha=0.5, label='Optimal (10%)')
        
        ax.set_ylabel('Allocation Moyenne (%)', color='white')
        ax.set_title('Comparaison de Formules d\'Allocation', color='white')
        ax.legend()
        ax.grid(True, alpha=0.2, axis='y')
        ax.set_facecolor('#1a1f2e')
        ax.tick_params(colors='white')
        
        # Valeurs sur les barres
        for bar, value in zip(bars, values):
            height = bar.get_height()
            color = '#00ff88' if 5 <= value <= 15 else '#ffa500' if value <= 25 else '#ff4444'
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}%', ha='center', va='bottom', 
                   color=color, fontsize=11, fontweight='bold')
        
        self.formula_comparison_chart.canvas.draw()
        
    def update_drawdown_analysis(self, data):
        """Analyse des drawdowns par stratégie"""
        self.drawdown_analysis_chart.clear()
        ax = self.drawdown_analysis_chart.figure.add_subplot(111)
        
        names = []
        max_dds = []
        avg_dds = []
        
        for name, strat_data in data.items():
            stats = strat_data['statistics']
            max_dd = abs(stats.get('max_drawdown', 0)) * 100
            
            # Calculer drawdown moyen (estimation)
            if 'returns' in strat_data and strat_data['returns'] is not None:
                returns = strat_data['returns']
                cumsum = np.cumsum(returns)
                peak = np.maximum.accumulate(cumsum)
                dd_series = (cumsum - peak) / np.maximum(peak, 1)
                avg_dd = abs(np.mean(dd_series[dd_series < 0])) * 100 if len(dd_series[dd_series < 0]) > 0 else 0
            else:
                avg_dd = max_dd * 0.3  # Estimation
            
            names.append(name)
            max_dds.append(max_dd)
            avg_dds.append(avg_dd)
        
        if names:
            x = np.arange(len(names))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, max_dds, width, label='Max Drawdown', 
                          color='#ff4444', alpha=0.8)
            bars2 = ax.bar(x + width/2, avg_dds, width, label='Drawdown Moyen', 
                          color='#ffa500', alpha=0.8)
            
            ax.set_xlabel('Stratégies', color='white')
            ax.set_ylabel('Drawdown (%)', color='white')
            ax.set_title('Analyse Comparative des Drawdowns', color='white')
            ax.set_xticks(x)
            ax.set_xticklabels(names, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.2, axis='y')
            ax.set_facecolor('#1a1f2e')
            ax.tick_params(colors='white')
            
            # Ajouter les valeurs
            for bar, value in zip(bars1, max_dds):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.1f}%', ha='center', va='bottom', 
                       color='white', fontsize=9)
        
        self.drawdown_analysis_chart.canvas.draw()
        
    def get_current_formula(self):
        """Récupère la formule actuelle"""
        try:
            widget = self
            main_window = None
            
            for _ in range(10):
                widget = widget.parent() if widget else None
                if widget and widget.__class__.__name__ == 'MainWindow':
                    main_window = widget
                    break
                    
            if main_window and hasattr(main_window, 'portfolio_view'):
                return main_window.portfolio_view.formula_input.text().strip()
        except:
            pass
        return None
        
    def calculate_formula_average(self, data, formula):
        """Calcule l'allocation moyenne d'une formule"""
        allocations = []
        
        for strat_data in data.values():
            stats = strat_data['statistics']
            
            # Métriques normalisées
            metrics = {
                'sharpe': stats.get('sharpe_ratio', 1.0),
                'omega': 1.5,
                'volatility': stats.get('volatility', 0.15),
                'drawdown': abs(stats.get('max_drawdown', 0.1)),
                'win_rate': stats.get('win_rate', 0.6),
                'profit_factor': stats.get('profit_factor', 1.2),
                'total_return': 0.1,
                'calmar': stats.get('calmar_ratio', 1.0),
                'sortino': stats.get('sortino_ratio', 1.0)
            }
            
            try:
                result = eval(formula, {'__builtins__': {}, 'sqrt': np.sqrt, 'max': max, 'min': min}, metrics)
                allocations.append(min(50, max(0, float(result))))
            except:
                allocations.append(10)  # Défaut
        
        return np.mean(allocations) if allocations else 10
        
    def update_formula_impact(self, data):
        """Met à jour l'impact de la formule"""
        self.formula_impact_chart.clear()
        ax = self.formula_impact_chart.figure.add_subplot(111)
        
        # Simuler différentes formules et leur impact
        formulas = [
            ('Conservatrice', 'sharpe/volatility'),
            ('Équilibrée', 'sharpe * omega'),
            ('Agressive', 'profit_factor * win_rate'),
            ('Complexe', '(sharpe * omega) / drawdown')
        ]
        
        # Pour chaque formule, calculer l'allocation moyenne
        formula_results = []
        
        for formula_name, formula in formulas:
            allocations = []
            for strat_data in data.values():
                stats = strat_data['statistics']
                # Simplification: utiliser des valeurs par défaut
                sharpe = stats.get('sharpe_ratio', 1.0)
                omega = 1.5  # Valeur par défaut
                volatility = stats.get('volatility', 0.15)
                profit_factor = stats.get('profit_factor', 1.2)
                win_rate = stats.get('win_rate', 0.6)
                drawdown = abs(stats.get('max_drawdown', 0.1))
                
                try:
                    # Évaluer la formule
                    result = eval(formula, {
                        'sharpe': sharpe,
                        'omega': omega,
                        'volatility': volatility,
                        'profit_factor': profit_factor,
                        'win_rate': win_rate,
                        'drawdown': drawdown
                    })
                    allocations.append(min(100, max(0, result * 10)))  # Normaliser
                except:
                    allocations.append(0)
            
            avg_allocation = np.mean(allocations) if allocations else 0
            formula_results.append((formula_name, avg_allocation))
        
        # Tracer les résultats
        names = [f[0] for f in formula_results]
        values = [f[1] for f in formula_results]
        colors = ['#00ff88', '#00d9ff', '#ffa500', '#667eea']
        
        bars = ax.bar(names, values, color=colors, alpha=0.8)
        
        # Ajouter les valeurs
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}%', ha='center', va='bottom', color='white')
        
        ax.set_ylabel('Allocation Moyenne (%)', color='white')
        ax.set_title('Impact de Différentes Formules sur l\'Allocation', color='white')
        ax.grid(True, alpha=0.2, axis='y')
        ax.set_facecolor('#1a1f2e')
        ax.tick_params(colors='white')
        
        # Ajouter une ligne de référence
        ax.axhline(y=10, color='red', linestyle='--', alpha=0.5, label='Allocation Recommandée (10%)')
        ax.legend()
        
        self.formula_impact_chart.canvas.draw()
        
    def update_sensitivity_analysis(self, data):
        """Met à jour l'analyse de sensibilité"""
        self.sensitivity_chart.clear()
        ax = self.sensitivity_chart.figure.add_subplot(111)
        
        # Analyser la sensibilité aux paramètres
        parameters = ['Sharpe', 'Volatilité', 'Win Rate', 'Drawdown']
        sensitivities = []
        
        # Pour chaque paramètre, voir comment il affecte le résultat
        for param in parameters:
            # Calculer la corrélation entre le paramètre et le P/L
            param_values = []
            pl_values = []
            
            for strat_data in data.values():
                stats = strat_data['statistics']
                if param == 'Sharpe':
                    param_values.append(stats.get('sharpe_ratio', 0))
                elif param == 'Volatilité':
                    param_values.append(stats.get('volatility', 0))
                elif param == 'Win Rate':
                    param_values.append(stats.get('win_rate', 0))
                elif param == 'Drawdown':
                    param_values.append(abs(stats.get('max_drawdown', 0)))
                
                pl_values.append(stats.get('total_pl', 0))
            
            if len(param_values) > 1 and len(pl_values) > 1:
                correlation = np.corrcoef(param_values, pl_values)[0, 1]
                sensitivities.append(correlation)
            else:
                sensitivities.append(0)
        
        # Créer le graphique en barres
        colors = ['#00ff88' if s > 0 else '#ff4444' for s in sensitivities]
        bars = ax.barh(parameters, sensitivities, color=colors, alpha=0.8)
        
        ax.set_xlabel('Corrélation avec P/L', color='white')
        ax.set_title('Sensibilité du P/L aux Différents Paramètres', color='white')
        ax.axvline(x=0, color='white', linestyle='-', alpha=0.3)
        ax.grid(True, alpha=0.2, axis='x')
        ax.set_facecolor('#1a1f2e')
        ax.tick_params(colors='white')
        
        # Ajouter les valeurs
        for bar, value in zip(bars, sensitivities):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{value:.2f}', ha='left' if value > 0 else 'right',
                   va='center', color='white', fontsize=10)
        
        self.sensitivity_chart.canvas.draw()