from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QTableWidget, QTableWidgetItem, QGroupBox,
                            QLabel, QLineEdit, QComboBox, QSlider, QSpinBox,
                            QHeaderView, QSplitter, QTextEdit, QProgressBar,
                            QDoubleSpinBox, QCheckBox, QFrame, QGridLayout,
                            QTabWidget, QPlainTextEdit, QListWidget,
                            QListWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
import pandas as pd
import numpy as np
from .styles import AppStyles


class PortfolioView(QWidget):
    """Vue pour la gestion du portfolio"""
    
    def __init__(self, portfolio_controller):
        super().__init__()
        self.portfolio_controller = portfolio_controller
        self.main_window = None  # Référence vers la fenêtre principale
        self.init_ui()
        self.connect_signals()
        
    def set_main_window(self, main_window):
        """Définit la référence vers la fenêtre principale"""
        self.main_window = main_window
        
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Splitter principal (plus de toolbar!)
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel gauche - Configuration et Formules
        left_panel = self.create_config_panel()
        
        # Panel central - Allocations seulement
        center_panel = self.create_allocations_panel()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.setSizes([400, 600])  # Plus d'espace pour les deux panels restants
        
        layout.addWidget(splitter)
        
    def create_config_panel(self):
        """Crée le panel de configuration et formules"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)  # Plus d'espace entre les sections
        
        # Configuration professionnelle
        config_group = QGroupBox("Configuration Portfolio")
        config_group.setStyleSheet("""
            QGroupBox {
                font-weight: 500;
                font-size: 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                margin: 12px 0;
                padding-top: 12px;
                background-color: #2d3748;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #ffffff;
                background-color: #2d3748;
            }
        """)
        config_layout = QVBoxLayout(config_group)
        config_layout.setSpacing(18)
        
        # Capital avec design professionnel
        self.capital_input = QDoubleSpinBox()
        self.capital_input.setRange(1000, 10000000)
        self.capital_input.setValue(100000)
        self.capital_input.setSuffix(" €")
        self.capital_input.setMinimumHeight(36)
        self.capital_input.setStyleSheet("""
            QDoubleSpinBox {
                font-size: 13px;
                font-weight: 500;
                padding: 8px 12px;
                border: 1px solid #4a5568;
                border-radius: 4px;
                background-color: #2d3748;
                color: #ffffff;
            }
            QDoubleSpinBox:focus {
                border-color: #3b82f6;
                outline: 2px solid rgba(59, 130, 246, 0.1);
                background-color: #1a202c;
            }
            QDoubleSpinBox:hover {
                border-color: #63b3ed;
                background-color: #1a202c;
            }
        """)
        config_layout.addWidget(self.capital_input)
        
        layout.addWidget(config_group)
        
        # Éditeur de formules professionnel
        formula_group = QGroupBox("Formules Risk Management")
        formula_group.setStyleSheet("""
            QGroupBox {
                font-weight: 500;
                font-size: 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                margin: 12px 0;
                padding-top: 12px;
                background-color: #2d3748;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #ffffff;
                background-color: #2d3748;
            }
        """)
        formula_layout = QVBoxLayout(formula_group)
        formula_layout.setSpacing(20)
        
        # Variables sous forme de boutons cliquables
        variables_container = QWidget()
        variables_layout = QGridLayout(variables_container)
        variables_layout.setSpacing(8)
        variables_layout.setContentsMargins(5, 5, 5, 5)
        
        # Créer les boutons de variables en grille
        variables_data = [
            ("sharpe", "Sharpe Ratio"), ("omega", "Omega Ratio"), ("volatility", "Volatilité"),
            ("drawdown", "Max Drawdown"), ("win_rate", "Taux victoire"), ("profit_factor", "Facteur profit"),
            ("total_return", "Rendement total"), ("calmar", "Calmar Ratio"), ("sortino", "Sortino Ratio")
        ]
        
        for i, (var, desc) in enumerate(variables_data):
            row = i // 3
            col = i % 3
            
            var_btn = QPushButton(var)
            var_btn.setToolTip(f"Cliquez pour insérer '{var}' - {desc}")
            var_btn.setCursor(Qt.PointingHandCursor)
            var_btn.setMinimumHeight(32)
            var_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #2d3748;
                    color: #ffffff;
                    font-family: 'Segoe UI', sans-serif;
                    font-weight: 500;
                    font-size: 11px;
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                    padding: 6px 8px;
                }}
                QPushButton:hover {{
                    background-color: #2d3748;
                    border-color: #9ca3af;
                    color: #1f2937;
                }}
                QPushButton:pressed {{
                    background-color: #3b82f6;
                    color: white;
                    border-color: #2563eb;
                }}
            """)
            
            # Connecter le clic pour insérer la variable
            var_btn.clicked.connect(lambda checked, variable=var: self.insert_variable(variable))
            variables_layout.addWidget(var_btn, row, col)
            
        formula_layout.addWidget(variables_container)
        
        # Éditeur avec design professionnel
        self.formula_editor = QPlainTextEdit()
        self.formula_editor.setMinimumHeight(90)
        self.formula_editor.setMaximumHeight(120)
        self.formula_editor.setPlaceholderText("Cliquez sur les variables pour les insérer automatiquement\n\nExemples:\n• (sharpe * 0.4 + omega * 0.6) / volatility\n• sqrt(omega * sharpe) / drawdown")
        self.formula_editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2d3748;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                font-weight: 400;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 12px;
                selection-background-color: #dbeafe;
                line-height: 1.5;
            }
            QPlainTextEdit:focus {
                border-color: #3b82f6;
                outline: 2px solid rgba(59, 130, 246, 0.1);
            }
        """)
        self.formula_editor.textChanged.connect(self.on_formula_changed)
        formula_layout.addWidget(self.formula_editor)
        
        # Bouton professionnel
        self.calculate_btn = QPushButton("Calculer les Allocations")
        self.calculate_btn.setMinimumHeight(40)
        self.calculate_btn.setCursor(Qt.PointingHandCursor)
        self.calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: 500;
                font-size: 13px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #e2e8f0;
            }
        """)
        self.calculate_btn.clicked.connect(self.calculate_custom_allocation)
        formula_layout.addWidget(self.calculate_btn)
        
        # Résultat avec style professionnel
        self.formula_result = QLabel("Prêt à calculer les allocations\nLe total peut dépasser 100% (plusieurs stratégies actives)")
        self.formula_result.setWordWrap(True)
        self.formula_result.setMinimumHeight(32)
        self.formula_result.setAlignment(Qt.AlignCenter)
        self.formula_result.setStyleSheet("""
            QLabel {
                color: #e2e8f0;
                font-size: 11px;
                font-weight: 400;
                padding: 8px 12px;
                border-radius: 4px;
                background-color: #2d3748;
                border: 1px solid #e5e7eb;
            }
        """)
        formula_layout.addWidget(self.formula_result)
        
        layout.addWidget(formula_group)
        
        layout.addStretch()
        return panel
        
    def create_allocations_panel(self):
        """Crée le panel d'allocations"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Titre et résumé
        title_layout = QHBoxLayout()
        title_label = QLabel("Allocations du Portfolio")
        title_label.setFont(QFont("", 14, QFont.Bold))
        title_layout.addWidget(title_label)
        
        self.total_label = QLabel("Total: 100%")
        self.total_label.setStyleSheet(f"color: {AppStyles.ACCENT}; font-weight: bold;")
        title_layout.addWidget(self.total_label)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # Table des allocations
        self.allocations_table = QTableWidget()
        self.allocations_table.setColumnCount(3)
        self.allocations_table.setHorizontalHeaderLabels([
            "Stratégie", "Allocation (%)", "Capital (€)"
        ])
        self.allocations_table.setStyleSheet(AppStyles.get_table_style())
        self.allocations_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.allocations_table)
        
        # Plus d'espace pour la table
        layout.addStretch()
        
        return panel
        
        
    def connect_signals(self):
        """Connecte les signaux du contrôleur"""
        self.portfolio_controller.portfolio_updated.connect(self.update_view)
        self.portfolio_controller.allocation_changed.connect(self.update_allocations)
        self.portfolio_controller.optimization_complete.connect(self.on_optimization_complete)
        
            
    def update_view(self):
        """Met à jour toute la vue"""
        self.update_allocations_table()
        
            
    def update_allocations_table(self):
        """Met à jour la table des allocations"""
        portfolio = self.portfolio_controller.portfolio
        allocations = portfolio.allocations
        
        self.allocations_table.setRowCount(len(allocations))
        total_allocation = 0
        
        for i, (strategy_name, allocation) in enumerate(allocations.items()):
            # Nom de la stratégie
            self.allocations_table.setItem(i, 0, QTableWidgetItem(strategy_name))
            
            # Allocation en pourcentage
            allocation_pct = allocation * 100
            allocation_item = QTableWidgetItem(f"{allocation_pct:.2f}%")
            self.allocations_table.setItem(i, 1, allocation_item)
            
            # Capital alloué
            capital = allocation * portfolio.current_capital
            capital_item = QTableWidgetItem(f"{capital:,.0f}€")
            self.allocations_table.setItem(i, 2, capital_item)
            
            total_allocation += allocation_pct
            
        # Mettre à jour le total (peut être différent de 100%)
        total_color = "#3b82f6" if total_allocation <= 100 else "#ef4444"  # Rouge si > 100%
        self.total_label.setText(f"Total: {total_allocation:.1f}%")
        self.total_label.setStyleSheet(f"color: {total_color}; font-weight: bold;")
            
    def update_allocations(self, allocations):
        """Met à jour les allocations affichées"""
        self.update_allocations_table()
        
        
    def on_optimization_complete(self, result):
        """Appelé quand l'optimisation est terminée"""
        method = result.get('method', 'unknown')
        new_allocations = result.get('new_allocations', {})
        
        # Mettre à jour l'affichage
        self.update_view()
        
        # Afficher un message de confirmation
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Optimisation Terminée",
            f"Optimisation {method} terminée avec succès!\n"
            f"Nouvelles allocations appliquées."
        )
        
    def update_allocations_from_formula(self, allocations):
        """Met à jour les allocations depuis la vue des formules"""
        try:
            # Convertir les allocations en dictionnaire pour le contrôleur
            self.portfolio_controller.update_allocations(allocations)
            self.update_view()
        except Exception as e:
            print(f"Erreur mise à jour allocations: {e}")
            
            
        
    def on_formula_changed(self):
        """Appelé quand la formule change"""
        formula = self.formula_editor.toPlainText()
        if formula:
            # Validation simple de la formule
            try:
                # Test avec des valeurs factices
                test_vars = {
                    'sharpe': 1.0, 'omega': 1.5, 'volatility': 0.15,
                    'drawdown': 0.1, 'win_rate': 0.6, 'profit_factor': 1.5,
                    'total_return': 0.2, 'calmar': 1.2, 'sortino': 1.8
                }
                self.evaluate_formula(formula, test_vars)
                self.formula_result.setText("✅ Formule valide")
                self.formula_result.setStyleSheet("color: #4CAF50; font-size: 10px;")
            except Exception as e:
                self.formula_result.setText(f"❌ Erreur: {str(e)}")
                self.formula_result.setStyleSheet("color: #f44336; font-size: 10px;")
                
    def evaluate_formula(self, formula, variables):
        """Évalue une formule avec les variables données"""
        import numpy as np
        
        # Contexte sécurisé pour l'évaluation
        safe_dict = {
            '__builtins__': {},
            'sqrt': np.sqrt,
            'log': np.log,
            'exp': np.exp,
            'abs': abs,
            'max': max,
            'min': min,
            **variables
        }
        
        # Évaluer la formule
        result = eval(formula, {"__builtins__": {}}, safe_dict)
        return float(result)
        
    def calculate_custom_allocation(self):
        """Calcule les allocations avec la formule personnalisée"""
        formula = self.formula_editor.toPlainText()
        if not formula:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une formule")
            return
            
        try:
            allocations = {}
            scores = {}
            
            # Calculer le score pour chaque stratégie
            for name, strategy in self.portfolio_controller.portfolio.strategies.items():
                if strategy and hasattr(strategy, 'metrics'):
                    variables = {
                        'sharpe': strategy.metrics.get('sharpe_ratio', 0),
                        'omega': strategy.metrics.get('omega_ratio', 0),
                        'volatility': strategy.metrics.get('volatility', 0.01),
                        'drawdown': abs(strategy.metrics.get('max_drawdown', 0)),
                        'win_rate': strategy.metrics.get('win_rate', 0),
                        'profit_factor': strategy.metrics.get('profit_factor', 1),
                        'total_return': strategy.metrics.get('total_return', 0),
                        'calmar': strategy.metrics.get('calmar_ratio', 0),
                        'sortino': strategy.metrics.get('sortino_ratio', 0)
                    }
                    
                    # Éviter les divisions par zéro
                    for key in ['volatility', 'drawdown']:
                        if variables[key] == 0:
                            variables[key] = 0.001
                            
                    score = self.evaluate_formula(formula, variables)
                    scores[name] = max(0, score)  # Score positif seulement
                    
            # Utiliser les scores directement comme pourcentages d'allocation
            if any(score > 0 for score in scores.values()):
                for name, score in scores.items():
                    # Score = pourcentage direct (7.09 = 7.09%), convertir en décimal pour le système
                    allocations[name] = score / 100.0  # 7.09 devient 0.0709
                    
                # Appliquer les allocations
                self.portfolio_controller.update_allocations(allocations)
                self.update_view()
                
                # Transmettre la formule à l'onglet Analyse
                if self.main_window:
                    self.main_window.analysis_view.set_current_formula(formula)
                
                # Message de succès
                QMessageBox.information(
                    self,
                    "Allocations Calculées",
                    f"Les allocations ont été calculées avec la formule:\n{formula}\n\n" +
                    "\n".join([f"{name}: {alloc:.1%}" for name, alloc in allocations.items()])
                )
            else:
                QMessageBox.warning(self, "Erreur", "Tous les scores sont zéro. Vérifiez votre formule.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du calcul: {str(e)}")
            
    def insert_variable(self, variable_name):
        """Insère une variable dans l'éditeur de formule à la position du curseur"""
        cursor = self.formula_editor.textCursor()
        cursor.insertText(variable_name)
        self.formula_editor.setFocus()  # Redonner le focus à l'éditeur
        
        # Feedback visuel professionnel
        self.formula_result.setText(f"Variable '{variable_name}' ajoutée")
        self.formula_result.setStyleSheet("""
            QLabel {
                color: #059669;
                font-size: 11px;
                font-weight: 500;
                padding: 8px 12px;
                border-radius: 4px;
                background-color: #2d3748;
                border: 1px solid #a7f3d0;
            }
        """)
        
        # Remettre le style normal après 2 secondes
        QTimer.singleShot(2000, self.reset_formula_result_style)
        
    def reset_formula_result_style(self):
        """Remet le style normal du résultat de formule"""
        self.formula_result.setText("Prêt à calculer les allocations\nLe total peut dépasser 100% (plusieurs stratégies actives)")
        self.formula_result.setStyleSheet("""
            QLabel {
                color: #e2e8f0;
                font-size: 11px;
                font-weight: 400;
                padding: 8px 12px;
                border-radius: 4px;
                background-color: #2d3748;
                border: 1px solid #e5e7eb;
            }
        """)