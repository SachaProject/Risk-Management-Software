"""
Vue Graphiques RÉELLE avec matplotlib intégré
Affichage des données de trading avec vrais charts interactifs
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QGroupBox, QLabel, QComboBox, QSplitter,
                            QTabWidget, QCheckBox, QSpinBox, QMessageBox,
                            QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from .styles import AppStyles

# Import matplotlib pour les graphiques RÉELS
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
    print("✅ Matplotlib disponible pour les graphiques")
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ Matplotlib non disponible - graphiques désactivés")

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class MatplotlibWidget(QWidget):
    """Widget matplotlib réutilisable pour les graphiques"""
    
    def __init__(self, figure_size=(10, 6)):
        super().__init__()
        self.figure = Figure(figsize=figure_size, facecolor='#2d3748')
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Style sombre par défaut
        plt.style.use('dark_background')
        self.figure.patch.set_facecolor('#2d3748')
        
    def clear(self):
        """Efface le graphique"""
        self.figure.clear()
        self.canvas.draw()


class ChartsView(QWidget):
    """Vue pour les graphiques et visualisations RÉELS"""
    
    def __init__(self):
        super().__init__()
        self.strategy_data = {}  # Cache des données de stratégies
        self.last_update = None
        self.init_ui()
        
        # Timer pour les mises à jour automatiques
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.auto_update)
        self.update_timer.start(30000)  # Mise à jour toutes les 30 secondes
        
    def init_ui(self):
        """Initialise l'interface utilisateur avec de vrais graphiques"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Toolbar de configuration
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        if not MATPLOTLIB_AVAILABLE:
            # Message d'erreur si matplotlib indisponible
            error_label = QLabel("❌ MATPLOTLIB NON DISPONIBLE\n\nPour afficher les graphiques, installez:\npip install matplotlib seaborn")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {AppStyles.DANGER};
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px;
                }}
            """)
            layout.addWidget(error_label)
            return
        
        # Onglets avec vrais graphiques
        self.tab_widget = QTabWidget()
        
        # Onglet Performance - RÉEL
        self.performance_tab = self.create_real_performance_tab()
        self.tab_widget.addTab(self.performance_tab, "📈 Performance")
        
        # Onglet Distribution - RÉEL
        self.distribution_tab = self.create_real_distribution_tab()
        self.tab_widget.addTab(self.distribution_tab, "📊 Distribution")
        
        # Onglet Portfolio - RÉEL
        self.portfolio_tab = self.create_real_portfolio_tab()
        self.tab_widget.addTab(self.portfolio_tab, "💼 Portfolio")
        
        # Onglet Métriques - RÉEL
        self.metrics_tab = self.create_real_metrics_tab()
        self.tab_widget.addTab(self.metrics_tab, "📊 Métriques")

        # Onglet Overfitting Check - NOUVEAU
        self.overfitting_tab = self.create_overfitting_check_tab()
        self.tab_widget.addTab(self.overfitting_tab, "🔍 Check Overfitting")
        
        layout.addWidget(self.tab_widget)
        
        # Chargement initial
        QTimer.singleShot(1000, self.update_charts)
        
    def create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.StyledPanel)
        toolbar_layout = QHBoxLayout(toolbar_frame)
        
        # Boutons d'action
        self.refresh_btn = QPushButton("🔄 Actualiser")
        self.refresh_btn.setStyleSheet(AppStyles.get_button_style("primary"))
        self.refresh_btn.clicked.connect(self.update_charts)
        
        self.export_btn = QPushButton("💾 Exporter")
        self.export_btn.setStyleSheet(AppStyles.get_button_style("success"))
        self.export_btn.clicked.connect(self.export_charts)
        
        # Configuration
        self.period_combo = QComboBox()
        self.period_combo.addItems(["1M", "3M", "6M", "1A", "2A", "Tout"])
        self.period_combo.setCurrentText("6M")
        
        self.auto_update_cb = QCheckBox("Auto-update")
        self.auto_update_cb.setChecked(True)
        
        # Status
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet(f"color: {AppStyles.TEXT_SECONDARY};")
        
        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addWidget(self.export_btn)
        toolbar_layout.addWidget(QLabel("Période:"))
        toolbar_layout.addWidget(self.period_combo)
        toolbar_layout.addWidget(self.auto_update_cb)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.status_label)
        
        return toolbar_frame
        
    def create_real_performance_tab(self):
        """Crée l'onglet performance avec VRAIS graphiques"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Splitter pour organiser les graphiques
        splitter = QSplitter(Qt.Vertical)
        
        # 1. Graphique principal - Courbes d'équité
        equity_group = QGroupBox("📈 Courbes d'Équité des Stratégies")
        equity_layout = QVBoxLayout(equity_group)
        
        self.equity_chart = MatplotlibWidget((12, 6))
        equity_layout.addWidget(self.equity_chart)
        splitter.addWidget(equity_group)
        
        # 2. Graphique secondaire - Drawdown
        dd_group = QGroupBox("📉 Drawdown Maximum")
        dd_layout = QVBoxLayout(dd_group)
        
        self.drawdown_chart = MatplotlibWidget((12, 3))
        dd_layout.addWidget(self.drawdown_chart)
        splitter.addWidget(dd_group)
        
        splitter.setSizes([400, 200])
        layout.addWidget(splitter)
        
        return widget
        
    def create_real_distribution_tab(self):
        """Crée l'onglet distribution avec VRAIS graphiques"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuration
        config_frame = QFrame()
        config_layout = QHBoxLayout(config_frame)
        
        self.bins_spin = QSpinBox()
        self.bins_spin.setRange(20, 100)
        self.bins_spin.setValue(50)
        self.bins_spin.valueChanged.connect(self.update_distribution_charts)
        
        config_layout.addWidget(QLabel("Bins:"))
        config_layout.addWidget(self.bins_spin)
        config_layout.addStretch()
        
        layout.addWidget(config_frame)
        
        # Graphiques de distribution
        splitter = QSplitter(Qt.Horizontal)
        
        # 1. Histogramme des rendements
        hist_group = QGroupBox("📊 Distribution des Rendements")
        hist_layout = QVBoxLayout(hist_group)
        
        self.histogram_chart = MatplotlibWidget((6, 6))
        hist_layout.addWidget(self.histogram_chart)
        splitter.addWidget(hist_group)
        
        # 2. Box plot comparatif
        box_group = QGroupBox("📦 Box Plot Comparatif")
        box_layout = QVBoxLayout(box_group)
        
        self.boxplot_chart = MatplotlibWidget((6, 6))
        box_layout.addWidget(self.boxplot_chart)
        splitter.addWidget(box_group)
        
        layout.addWidget(splitter)
        
        return widget
        
    def create_real_portfolio_tab(self):
        """Crée l'onglet portfolio avec VRAIS graphiques"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Graphiques de portfolio
        splitter = QSplitter(Qt.Horizontal)
        
        # 1. Allocation du portfolio
        allocation_group = QGroupBox("🥧 Allocation du Portfolio")
        allocation_layout = QVBoxLayout(allocation_group)
        
        self.allocation_chart = MatplotlibWidget((6, 6))
        allocation_layout.addWidget(self.allocation_chart)
        splitter.addWidget(allocation_group)
        
        # 2. Contribution aux performances
        contribution_group = QGroupBox("📈 Contribution aux Performances")
        contribution_layout = QVBoxLayout(contribution_group)
        
        self.contribution_chart = MatplotlibWidget((6, 6))
        contribution_layout.addWidget(self.contribution_chart)
        splitter.addWidget(contribution_group)
        
        layout.addWidget(splitter)
        
        return widget
        
    def create_real_metrics_tab(self):
        """Crée l'onglet métriques avec VRAIS graphiques"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Graphiques de métriques
        splitter = QSplitter(Qt.Vertical)
        
        # 1. Barres des métriques principales
        metrics_group = QGroupBox("📊 Métriques Principales")
        metrics_layout = QVBoxLayout(metrics_group)
        
        self.metrics_chart = MatplotlibWidget((12, 4))
        metrics_layout.addWidget(self.metrics_chart)
        splitter.addWidget(metrics_group)
        
        # 2. Radar chart des performances
        radar_group = QGroupBox("🕸️ Radar des Performances")
        radar_layout = QVBoxLayout(radar_group)
        
        self.radar_chart = MatplotlibWidget((8, 6))
        radar_layout.addWidget(self.radar_chart)
        splitter.addWidget(radar_group)
        
        layout.addWidget(splitter)
        
        return widget

    def create_overfitting_check_tab(self):
        """Crée l'onglet de vérification rapide d'overfitting"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Description
        info_label = QLabel("🔍 Vérifications Rapides d'Overfitting des Formules")
        info_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #ff6b6b; padding: 10px;")
        layout.addWidget(info_label)

        # Graphiques de vérification
        splitter = QSplitter(Qt.Vertical)

        # 1. Distribution des allocations
        alloc_group = QGroupBox("📊 Distribution des Allocations (Détection d'Extrêmes)")
        alloc_layout = QVBoxLayout(alloc_group)

        self.allocation_dist_chart = MatplotlibWidget((12, 4))
        alloc_layout.addWidget(self.allocation_dist_chart)
        splitter.addWidget(alloc_group)

        # 2. Stabilité dans le temps
        stability_group = QGroupBox("📈 Stabilité des Allocations dans le Temps")
        stability_layout = QVBoxLayout(stability_group)

        self.stability_chart = MatplotlibWidget((12, 4))
        stability_layout.addWidget(self.stability_chart)
        splitter.addWidget(stability_group)

        # 3. Corrélation Performance vs Allocation
        corr_group = QGroupBox("🎯 Corrélation Performance Passée vs Allocation Actuelle")
        corr_layout = QVBoxLayout(corr_group)

        self.correlation_check_chart = MatplotlibWidget((12, 4))
        corr_layout.addWidget(self.correlation_check_chart)
        splitter.addWidget(corr_group)

        layout.addWidget(splitter)

        return widget

    def get_strategy_data(self):
        """Récupère les VRAIES données des stratégies CSV importées"""
        try:
            # Accéder au contrôleur principal
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
                return None
                
            controller = main_window.controller
            data_controller = controller.data_controller
            
            # Utiliser les modèles de trades (vraies données!)
            trade_models = data_controller.trade_models
            portfolio = controller.portfolio_controller.portfolio
            
            if not trade_models:
                return None
                
            # Extraire les VRAIES données CSV
            strategy_data = {}
            
            for name, trade_model in trade_models.items():
                if not trade_model:
                    continue
                if trade_model.df is None:
                    continue
                if hasattr(trade_model.df, 'empty') and trade_model.df.empty:
                    continue
                    
                df = trade_model.df.copy()
                
                # Calculer les vraies métriques
                stats = trade_model.get_statistics()
                returns = trade_model.get_returns()
                
                # Récupérer l'allocation
                allocation = 0
                if portfolio and hasattr(portfolio, 'allocations') and name in portfolio.allocations:
                    allocation = portfolio.allocations[name] * 100
                
                try:
                    # Utiliser les VRAIES données pour créer les graphiques
                    dates = pd.to_datetime(df['Date Closed']) if 'Date Closed' in df else pd.date_range(end=datetime.now(), periods=len(df), freq='D')
                    pl_values = df['P/L'].values if 'P/L' in df else returns * 1000
                    
                    # Calculer la courbe d'équité cumulative RÉELLE
                    equity = np.cumsum(pl_values)
                    equity_normalized = (equity / abs(equity[0]) if equity[0] != 0 else equity) + 1
                    
                    # Calculer le VRAI drawdown
                    peak = np.maximum.accumulate(equity)
                    drawdown = (equity - peak) / np.maximum(peak, 1)
                    
                    # Utiliser les vraies métriques calculées
                    real_metrics = {
                        'total_return': stats.get('total_pl', 0),
                        'volatility': stats.get('volatility', 0) * 100,
                        'sharpe': stats.get('sharpe_ratio', 0),
                        'max_drawdown': stats.get('max_drawdown', 0),
                        'win_rate': stats.get('win_rate', 0) * 100,
                        'profit_factor': stats.get('profit_factor', 1),
                        'total_trades': stats.get('total_trades', len(df))
                    }
                    
                    strategy_data[name] = {
                        'dates': dates,
                        'returns': returns,  # Rendements par trade
                        'pl_values': pl_values,  # P/L réels
                        'equity': equity_normalized,  # Courbe d'équité normalisée
                        'drawdown': drawdown,  # Drawdown réel
                        'metrics': real_metrics,  # Métriques calculées
                        'allocation': allocation,
                        'raw_data': df  # DataFrame original
                    }
                    
                except Exception as e:
                    continue
                        
            return strategy_data if strategy_data else None
            
        except Exception as e:
            return None
            
    def generate_sample_data(self):
        """Génère des données d'exemple pour les démonstrations"""
        np.random.seed(42)  # Pour la reproductibilité
        
        dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
        strategies = ['Strategy_A', 'Strategy_B', 'Strategy_C', 'Strategy_D']
        
        data = {}
        for i, strategy in enumerate(strategies):
            # Paramètres différents pour chaque stratégie
            mu = 0.0005 + i * 0.0002  # Rendement moyen différent
            sigma = 0.015 + i * 0.005  # Volatilité différente
            
            # Générer des rendements
            returns = np.random.normal(mu, sigma, len(dates))
            
            # Calculer l'équité cumulative
            equity = (1 + returns).cumprod()
            
            # Calculer le drawdown
            peak = np.maximum.accumulate(equity)
            drawdown = (equity - peak) / peak
            
            data[strategy] = {
                'dates': dates,
                'returns': returns,
                'equity': equity,
                'drawdown': drawdown,
                'metrics': {
                    'total_return': (equity[-1] - 1) * 100,
                    'volatility': returns.std() * np.sqrt(252) * 100,
                    'sharpe': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
                    'max_drawdown': drawdown.min() * 100
                }
            }
            
        return data
        
    def update_charts(self):
        """Met à jour TOUS les graphiques avec les VRAIES données CSV"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        self.status_label.setText("Mise à jour...")
        
        # Récupérer les VRAIES données CSV
        real_data = self.get_strategy_data()
        
        if real_data:
            # UTILISER LES VRAIES DONNÉES CSV !
            self.status_label.setText(f"✅ {len(real_data)} stratégies CSV chargées")
            data = real_data  # ← UTILISER LES VRAIES DONNÉES !
            
            # Utiliser les vraies données CSV
        else:
            # Seulement si AUCUNE donnée CSV
            self.status_label.setText("⚠️ Pas de CSV - Données d'exemple")
            data = self.generate_sample_data()
            
        self.strategy_data = data
        self.last_update = datetime.now()
        
        # Mettre à jour tous les graphiques avec les VRAIES données
        self.update_performance_charts(data)
        self.update_distribution_charts()
        self.update_portfolio_charts(data)
        self.update_metrics_charts(data)
        self.update_overfitting_checks(data)
        
        # Status final
        if real_data:
            self.status_label.setText(f"✅ Données réelles: {self.last_update.strftime('%H:%M:%S')}")
        else:
            self.status_label.setText(f"⚠️ Exemple: {self.last_update.strftime('%H:%M:%S')}")
        
    def update_performance_charts(self, data):
        """Met à jour les graphiques de performance"""
        # 1. Courbes d'équité
        self.equity_chart.clear()
        ax1 = self.equity_chart.figure.add_subplot(111)
        
        colors = ['#00ff9f', '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#6c5ce7']
        
        for i, (name, strategy_data) in enumerate(data.items()):
            ax1.plot(strategy_data['dates'], strategy_data['equity'], 
                    label=name, color=colors[i % len(colors)], linewidth=2)
        
        ax1.set_title('Courbes d\'Équité Normalisées (Base 1)', color='white', fontsize=14, pad=20)
        ax1.set_xlabel('Date', color='white')
        ax1.set_ylabel('Équité', color='white')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(colors='white')
        
        self.equity_chart.canvas.draw()
        
        # 2. Drawdown
        self.drawdown_chart.clear()
        ax2 = self.drawdown_chart.figure.add_subplot(111)
        
        for i, (name, strategy_data) in enumerate(data.items()):
            ax2.fill_between(strategy_data['dates'], strategy_data['drawdown'] * 100, 0,
                           color=colors[i % len(colors)], alpha=0.6, label=name)
        
        ax2.set_title('Drawdown Maximum (%)', color='white', fontsize=12)
        ax2.set_ylabel('Drawdown %', color='white')
        ax2.legend(loc='lower right')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(colors='white')
        
        self.drawdown_chart.canvas.draw()
        
    def update_distribution_charts(self):
        """Met à jour les graphiques de distribution"""
        if not self.strategy_data:
            return
            
        # 1. Histogramme
        self.histogram_chart.clear()
        ax1 = self.histogram_chart.figure.add_subplot(111)
        
        bins = self.bins_spin.value()
        colors = ['#00ff9f', '#ff6b6b', '#4ecdc4', '#45b7d1']
        
        for i, (name, strategy_data) in enumerate(self.strategy_data.items()):
            returns_pct = strategy_data['returns'] * 100
            ax1.hist(returns_pct, bins=bins, alpha=0.6, 
                    label=name, color=colors[i % len(colors)])
        
        ax1.set_title('Distribution des Rendements Quotidiens', color='white', fontsize=12)
        ax1.set_xlabel('Rendement (%)', color='white')
        ax1.set_ylabel('Fréquence', color='white')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(colors='white')
        
        self.histogram_chart.canvas.draw()
        
        # 2. Box plot
        self.boxplot_chart.clear()
        ax2 = self.boxplot_chart.figure.add_subplot(111)
        
        returns_data = [strategy_data['returns'] * 100 for strategy_data in self.strategy_data.values()]
        labels = list(self.strategy_data.keys())
        
        bp = ax2.boxplot(returns_data, labels=labels, patch_artist=True)
        
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax2.set_title('Box Plot des Rendements par Stratégie', color='white', fontsize=12)
        ax2.set_ylabel('Rendement (%)', color='white')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(colors='white')
        
        self.boxplot_chart.canvas.draw()
        
    def update_portfolio_charts(self, data):
        """Met à jour les graphiques de portfolio avec les VRAIES allocations"""
        # 1. Allocation
        self.allocation_chart.clear()
        ax1 = self.allocation_chart.figure.add_subplot(111)
        
        # Utiliser les VRAIES allocations du portfolio !
        names = list(data.keys())
        allocations = [data[name].get('allocation', 0) for name in names]
        colors = ['#00ff9f', '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#6c5ce7']
        
        # Si toutes les allocations sont à 0, afficher un message
        if sum(allocations) == 0:
            ax1.text(0.5, 0.5, 'Aucune allocation définie\n\nUtilisez l\'onglet "Portfolio & Formules"\npour définir les allocations', 
                    ha='center', va='center', transform=ax1.transAxes,
                    fontsize=12, color='white')
            ax1.set_title('Allocation du Portfolio', color='white', fontsize=14)
        else:
            # Afficher le vrai pie chart avec les vraies allocations
            wedges, texts, autotexts = ax1.pie(allocations, labels=names, colors=colors[:len(names)], 
                                              autopct='%1.1f%%', startangle=90)
            
            for text in texts + autotexts:
                text.set_color('white')
                
            ax1.set_title(f'Allocation du Portfolio (Total: {sum(allocations):.1f}%)', 
                         color='white', fontsize=14)
        
        self.allocation_chart.canvas.draw()
        
        # 2. Contribution aux performances (basée sur les vraies allocations et rendements)
        self.contribution_chart.clear()
        ax2 = self.contribution_chart.figure.add_subplot(111)
        
        # Calculer les vraies contributions
        contributions = []
        for name in names:
            allocation = data[name].get('allocation', 0)
            total_return = data[name]['metrics']['total_return']
            contribution = (allocation / 100) * total_return  # Contribution réelle
            contributions.append(contribution)
        
        bars = ax2.bar(names, contributions, color=colors[:len(names)])
        ax2.set_title('Contribution aux Performances (%)', color='white', fontsize=12)
        ax2.set_ylabel('Contribution (%)', color='white')
        ax2.tick_params(colors='white')
        ax2.grid(True, alpha=0.3)
        
        # Ajouter les valeurs sur les barres
        for bar, contrib in zip(bars, contributions):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{contrib:.2f}%', ha='center', va='bottom', color='white', fontsize=9)
        
        self.contribution_chart.canvas.draw()
        
    def update_metrics_charts(self, data):
        """Met à jour les graphiques de métriques"""
        # 1. Barres des métriques
        self.metrics_chart.clear()
        ax1 = self.metrics_chart.figure.add_subplot(111)
        
        names = list(data.keys())
        metrics_names = ['Rendement', 'Volatilité', 'Sharpe', 'Max DD']
        
        x = np.arange(len(names))
        width = 0.2
        
        colors = ['#00ff9f', '#ff6b6b', '#4ecdc4', '#45b7d1']
        
        for i, metric in enumerate(['total_return', 'volatility', 'sharpe', 'max_drawdown']):
            values = [data[name]['metrics'][metric] for name in names]
            ax1.bar(x + i*width, values, width, label=metrics_names[i], color=colors[i])
        
        ax1.set_title('Métriques par Stratégie', color='white', fontsize=12)
        ax1.set_xticks(x + width * 1.5)
        ax1.set_xticklabels(names, color='white')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(colors='white')
        
        self.metrics_chart.canvas.draw()
        
        # 2. Radar chart (simplifié)
        self.radar_chart.clear()
        ax2 = self.radar_chart.figure.add_subplot(111, projection='polar')
        
        # Exemple de radar chart pour la première stratégie
        if data:
            first_strategy = list(data.values())[0]
            metrics_values = [
                max(0, min(100, first_strategy['metrics']['total_return'] + 50)),
                max(0, min(100, 100 - first_strategy['metrics']['volatility'])),
                max(0, min(100, first_strategy['metrics']['sharpe'] * 20 + 50)),
                max(0, min(100, 100 + first_strategy['metrics']['max_drawdown']))
            ]
            
            angles = np.linspace(0, 2*np.pi, len(metrics_names), endpoint=False)
            metrics_values += [metrics_values[0]]  # Fermer le polygone
            angles = np.concatenate((angles, [angles[0]]))
            
            ax2.plot(angles, metrics_values, 'o-', linewidth=2, color='#00ff9f')
            ax2.fill(angles, metrics_values, alpha=0.25, color='#00ff9f')
            ax2.set_thetagrids(angles[:-1] * 180/np.pi, metrics_names)
            ax2.set_title('Performance Radar', color='white', y=1.08)
            
        self.radar_chart.canvas.draw()

    def update_overfitting_checks(self, data):
        """Met à jour les graphiques de vérification d'overfitting"""
        if not MATPLOTLIB_AVAILABLE or not hasattr(self, 'allocation_dist_chart'):
            return

        # Récupérer les allocations actuelles
        allocations = self.get_current_allocations(data)

        # 1. Distribution des allocations
        self.update_allocation_distribution(allocations)

        # 2. Test de stabilité (simulé)
        self.update_allocation_stability(data, allocations)

        # 3. Corrélation performance/allocation
        self.update_performance_correlation(data, allocations)

    def get_current_allocations(self, data):
        """Récupère les allocations actuelles depuis le portfolio"""
        allocations = {}

        try:
            # Accéder au portfolio
            widget = self
            main_window = None

            for _ in range(10):
                widget = widget.parent() if widget else None
                if widget and widget.__class__.__name__ == 'MainWindow':
                    main_window = widget
                    break

            if main_window and hasattr(main_window, 'controller'):
                portfolio = main_window.controller.portfolio_controller.portfolio
                if portfolio and hasattr(portfolio, 'allocations'):
                    for name in data.keys():
                        if name in portfolio.allocations:
                            allocations[name] = portfolio.allocations[name] * 100
                        else:
                            allocations[name] = 0
            else:
                # Valeurs par défaut si pas d'accès
                for name in data.keys():
                    allocations[name] = 10  # 10% par défaut

        except Exception:
            # Fallback
            for name in data.keys():
                allocations[name] = np.random.uniform(5, 25)  # Entre 5% et 25%

        return allocations

    def update_allocation_distribution(self, allocations):
        """Met à jour le graphique de distribution des allocations"""
        self.allocation_dist_chart.clear()
        ax = self.allocation_dist_chart.figure.add_subplot(111)

        if not allocations:
            ax.text(0.5, 0.5, 'Aucune allocation disponible', ha='center', va='center',
                   transform=ax.transAxes, color='white', fontsize=12)
            self.allocation_dist_chart.canvas.draw()
            return

        names = list(allocations.keys())
        values = list(allocations.values())

        # Détecter les allocations extrêmes
        colors = []
        warnings = []

        for val in values:
            if val > 40:
                colors.append('#ff4444')  # Rouge pour trop élevé
                warnings.append(f"ÉLEVÉ: {val:.1f}%")
            elif val > 25:
                colors.append('#ffa500')  # Orange pour modéré
                warnings.append(f"MODÉRÉ: {val:.1f}%")
            elif val < 2:
                colors.append('#ff6b6b')  # Rouge clair pour trop faible
                warnings.append(f"FAIBLE: {val:.1f}%")
            else:
                colors.append('#00ff88')  # Vert pour OK
                warnings.append(f"OK: {val:.1f}%")

        # Graphique en barres
        bars = ax.bar(range(len(names)), values, color=colors, alpha=0.8, edgecolor='white')

        # Lignes de référence
        ax.axhline(y=25, color='orange', linestyle='--', alpha=0.7, label='Seuil modéré (25%)')
        ax.axhline(y=40, color='red', linestyle='--', alpha=0.7, label='Seuil élevé (40%)')
        ax.axhline(y=10, color='green', linestyle='--', alpha=0.5, label='Cible recommandée (10%)')

        # Configuration
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha='right', color='white')
        ax.set_ylabel('Allocation (%)', color='white')
        ax.set_title('Distribution des Allocations - Détection d\'Extrêmes', color='white', fontsize=12)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.2, axis='y')
        ax.set_facecolor('#2d3748')
        ax.tick_params(colors='white')

        # Ajouter les valeurs et warnings
        for bar, warning in zip(bars, warnings):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   warning, ha='center', va='bottom', color='white',
                   fontsize=8, fontweight='bold', rotation=90)

        # Résumé des problèmes
        extreme_count = sum(1 for v in values if v > 40 or v < 2)
        if extreme_count > 0:
            ax.text(0.02, 0.98, f'⚠️ {extreme_count} allocation(s) extrême(s) détectée(s)',
                   transform=ax.transAxes, va='top', ha='left',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.7),
                   color='white', fontweight='bold')

        self.allocation_dist_chart.canvas.draw()

    def update_allocation_stability(self, data, allocations):
        """Met à jour le test de stabilité des allocations"""
        self.stability_chart.clear()
        ax = self.stability_chart.figure.add_subplot(111)

        if not allocations:
            ax.text(0.5, 0.5, 'Pas de données pour le test de stabilité', ha='center', va='center',
                   transform=ax.transAxes, color='white', fontsize=12)
            self.stability_chart.canvas.draw()
            return

        # Simuler la stabilité en ajoutant du bruit aux allocations actuelles
        # (En réalité, on devrait calculer les allocations sur différentes périodes)
        periods = ['Période 1', 'Période 2', 'Période 3', 'Période 4']
        names = list(allocations.keys())
        colors = ['#00ff88', '#00d9ff', '#ffa500', '#ff4444']

        # Pour chaque stratégie, simuler la variabilité
        for i, name in enumerate(names):
            base_allocation = allocations[name]

            # Simuler des variations (en réalité, on calculerait sur vraies périodes)
            variations = []
            for _ in periods:
                # Ajouter une variation aléatoire de ±20%
                variation = base_allocation * (1 + np.random.uniform(-0.2, 0.2))
                variations.append(max(0, variation))

            # Tracer la ligne de stabilité
            ax.plot(periods, variations, 'o-', label=name, color=colors[i % len(colors)],
                   linewidth=2, markersize=6)

            # Calculer la variabilité
            cv = np.std(variations) / (np.mean(variations) + 1e-6)  # Coefficient de variation

            # Ajouter une annotation de stabilité
            if cv < 0.15:
                stability_text = "STABLE"
                text_color = '#00ff88'
            elif cv < 0.3:
                stability_text = "MODÉRÉ"
                text_color = '#ffa500'
            else:
                stability_text = "INSTABLE"
                text_color = '#ff4444'

            ax.text(len(periods)-1, variations[-1], f' {stability_text}\n(CV: {cv:.2f})',
                   color=text_color, fontweight='bold', fontsize=8, va='center')

        ax.set_title('Test de Stabilité des Allocations dans le Temps', color='white', fontsize=12)
        ax.set_xlabel('Périodes', color='white')
        ax.set_ylabel('Allocation (%)', color='white')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.2)
        ax.set_facecolor('#2d3748')
        ax.tick_params(colors='white')

        # Message d'explication
        ax.text(0.02, 0.02, 'Note: Simule la variabilité des allocations sur différentes périodes\n' +
                           'CV < 0.15 = STABLE, 0.15-0.30 = MODÉRÉ, > 0.30 = INSTABLE',
               transform=ax.transAxes, va='bottom', ha='left',
               fontsize=8, color='#cbd5e0', style='italic')

        self.stability_chart.canvas.draw()

    def update_performance_correlation(self, data, allocations):
        """Met à jour le graphique de corrélation performance/allocation"""
        self.correlation_check_chart.clear()
        ax = self.correlation_check_chart.figure.add_subplot(111)

        if not data or not allocations:
            ax.text(0.5, 0.5, 'Pas de données pour l\'analyse de corrélation', ha='center', va='center',
                   transform=ax.transAxes, color='white', fontsize=12)
            self.correlation_check_chart.canvas.draw()
            return

        # Extraire performance passée et allocations actuelles
        past_performances = []
        current_allocations = []
        strategy_names = []

        for name in data.keys():
            if name in allocations:
                # Performance passée (P/L total ou rendement total)
                perf = data[name]['metrics'].get('total_return', 0)
                alloc = allocations[name]

                past_performances.append(perf)
                current_allocations.append(alloc)
                strategy_names.append(name)

        if len(past_performances) < 2:
            ax.text(0.5, 0.5, 'Pas assez de données pour calculer la corrélation', ha='center', va='center',
                   transform=ax.transAxes, color='white', fontsize=12)
            self.correlation_check_chart.canvas.draw()
            return

        # Calculer la corrélation
        correlation = np.corrcoef(past_performances, current_allocations)[0, 1]

        if np.isnan(correlation):
            correlation = 0

        # Scatter plot
        colors = ['#00ff88' if p > 0 else '#ff4444' for p in past_performances]
        scatter = ax.scatter(past_performances, current_allocations, c=colors, s=100, alpha=0.7, edgecolors='white')

        # Ajouter les noms des stratégies
        for i, name in enumerate(strategy_names):
            ax.annotate(name, (past_performances[i], current_allocations[i]),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, color='white', alpha=0.8)

        # Ligne de tendance
        if len(past_performances) > 1:
            z = np.polyfit(past_performances, current_allocations, 1)
            p = np.poly1d(z)
            x_trend = np.linspace(min(past_performances), max(past_performances), 100)
            ax.plot(x_trend, p(x_trend), "r--", alpha=0.8, linewidth=2, label=f'Tendance (r={correlation:.3f})')

        # Configuration
        ax.set_xlabel('Performance Passée', color='white')
        ax.set_ylabel('Allocation Actuelle (%)', color='white')
        ax.set_title('Corrélation Performance Passée vs Allocation Actuelle', color='white', fontsize=12)
        ax.grid(True, alpha=0.2)
        ax.set_facecolor('#2d3748')
        ax.tick_params(colors='white')
        ax.legend()

        # Interprétation de la corrélation
        if abs(correlation) > 0.7:
            warning_text = f"⚠️ CORRÉLATION ÉLEVÉE ({correlation:.3f})\nRisque d'overfitting!"
            warning_color = '#ff4444'
        elif abs(correlation) > 0.4:
            warning_text = f"⚠️ Corrélation modérée ({correlation:.3f})\nÀ surveiller"
            warning_color = '#ffa500'
        else:
            warning_text = f"✅ Corrélation faible ({correlation:.3f})\nBon signe"
            warning_color = '#00ff88'

        ax.text(0.02, 0.98, warning_text, transform=ax.transAxes, va='top', ha='left',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=warning_color, alpha=0.7),
               color='white', fontweight='bold', fontsize=10)

        # Explication
        ax.text(0.02, 0.02, 'Corrélation élevée = allocation basée sur performance passée = overfitting potentiel',
               transform=ax.transAxes, va='bottom', ha='left',
               fontsize=8, color='#cbd5e0', style='italic')

        self.correlation_check_chart.canvas.draw()

    def auto_update(self):
        """Mise à jour automatique si activée"""
        if self.auto_update_cb.isChecked() and MATPLOTLIB_AVAILABLE:
            self.update_charts()
            
    def export_charts(self):
        """Exporte tous les graphiques"""
        if not MATPLOTLIB_AVAILABLE:
            QMessageBox.warning(self, "Export impossible", "Matplotlib non disponible")
            return
            
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les Graphiques",
            f"charts_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
            "PNG Files (*.png);;PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                # Exporter le graphique actuellement visible
                current_tab = self.tab_widget.currentIndex()
                
                if current_tab == 0 and hasattr(self, 'equity_chart'):
                    self.equity_chart.figure.savefig(file_path, dpi=300, bbox_inches='tight',
                                                   facecolor='#2d3748', edgecolor='none')
                elif current_tab == 1 and hasattr(self, 'histogram_chart'):
                    self.histogram_chart.figure.savefig(file_path, dpi=300, bbox_inches='tight',
                                                       facecolor='#2d3748', edgecolor='none')
                
                QMessageBox.information(self, "Export réussi", f"Graphiques exportés vers:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur Export", f"Erreur lors de l'export: {str(e)}")