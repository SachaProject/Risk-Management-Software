from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QTableWidget, QTableWidgetItem, QGroupBox,
                            QLabel, QLineEdit, QComboBox, QFileDialog,
                            QHeaderView, QSplitter, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
import pandas as pd
from .styles import AppStyles


class DataView(QWidget):
    """Vue pour la gestion des données"""
    
    def __init__(self, data_controller):
        super().__init__()
        self.data_controller = data_controller
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # Boutons d'action
        self.load_btn = QPushButton("📁 Charger CSV")
        self.load_btn.setStyleSheet(AppStyles.get_button_style("primary"))
        self.load_btn.clicked.connect(self.load_csv_files)
        
        self.clear_btn = QPushButton("🗑️ Effacer Tout")
        self.clear_btn.setStyleSheet(AppStyles.get_button_style("danger"))
        self.clear_btn.clicked.connect(self.clear_all_data)
        
        toolbar_layout.addWidget(self.load_btn)
        toolbar_layout.addWidget(self.clear_btn)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel gauche - Liste des fichiers
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        files_group = QGroupBox("Fichiers Chargés")
        files_layout = QVBoxLayout(files_group)
        
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(3)
        self.files_table.setHorizontalHeaderLabels(["Fichier", "Trades", "Statut"])
        self.files_table.setStyleSheet(AppStyles.get_table_style())
        self.files_table.horizontalHeader().setStretchLastSection(True)
        self.files_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.files_table.itemSelectionChanged.connect(self.on_file_selected)
        
        files_layout.addWidget(self.files_table)
        left_layout.addWidget(files_group)
        
        # Panel central - Données et statistiques
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        
        # Filtre
        filter_group = QGroupBox("Filtres")
        filter_layout = QHBoxLayout(filter_group)
        
        self.filter_strategy = QComboBox()
        self.filter_strategy.addItem("Toutes les stratégies")
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Rechercher...")
        
        self.filter_btn = QPushButton("Appliquer")
        self.filter_btn.clicked.connect(self.apply_filters)
        
        filter_layout.addWidget(QLabel("Stratégie:"))
        filter_layout.addWidget(self.filter_strategy)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(self.filter_btn)
        
        center_layout.addWidget(filter_group)
        
        # Table des trades
        trades_group = QGroupBox("Trades")
        trades_layout = QVBoxLayout(trades_group)
        
        self.trades_table = QTableWidget()
        self.trades_table.setStyleSheet(AppStyles.get_table_style())
        self.trades_table.setSortingEnabled(True)
        self.trades_table.setAlternatingRowColors(True)
        
        trades_layout.addWidget(self.trades_table)
        center_layout.addWidget(trades_group)
        
        # Panel droit - Statistiques
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        stats_group = QGroupBox("Statistiques")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d30;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        
        stats_layout.addWidget(self.stats_text)
        right_layout.addWidget(stats_group)
        
        # Ajouter les panels au splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 600, 300])
        
        layout.addWidget(splitter)
        
    def connect_signals(self):
        """Connecte les signaux du contrôleur"""
        self.data_controller.data_loaded.connect(self.on_data_loaded)
        self.data_controller.data_error.connect(self.on_data_error)
        self.data_controller.progress_update.connect(self.on_progress_update)
        
    def load_csv_files(self):
        """Charge des fichiers CSV"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner des fichiers CSV",
            "",
            "Fichiers CSV (*.csv)"
        )
        
        if files:
            self.data_controller.load_multiple_csv(files)
            
    def clear_all_data(self):
        """Efface toutes les données"""
        self.data_controller.clear_all_data()
        self.files_table.setRowCount(0)
        self.trades_table.setRowCount(0)
        self.stats_text.clear()
        
    def on_data_loaded(self, file_name):
        """Appelé quand un fichier est chargé"""
        self.refresh_data()
        self.update_file_list()
        
    def on_data_error(self, error_message):
        """Affiche une erreur de données"""
        # Géré par le contrôleur principal
        pass
        
    def on_progress_update(self, progress):
        """Met à jour la progression"""
        # Implémentation future d'une barre de progression
        pass
        
    def on_file_selected(self):
        """Appelé quand un fichier est sélectionné dans la liste"""
        selected_items = self.files_table.selectedItems()
        if selected_items:
            file_name = self.files_table.item(selected_items[0].row(), 0).text()
            self.show_file_details(file_name)
            
    def show_file_details(self, file_name):
        """Affiche les détails d'un fichier"""
        trade_model = self.data_controller.get_trade_model(file_name)
        
        if trade_model and trade_model.df is not None:
            # Afficher les trades dans la table
            self.populate_trades_table(trade_model.df)
            
            # Afficher les statistiques
            stats = trade_model.get_statistics()
            self.display_statistics(stats)
            
    def populate_trades_table(self, df):
        """Remplit la table des trades"""
        self.trades_table.setRowCount(len(df))
        self.trades_table.setColumnCount(len(df.columns))
        self.trades_table.setHorizontalHeaderLabels(df.columns.tolist())
        
        for i, row in df.iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                
                # Coloration conditionnelle pour P/L
                if df.columns[j] == 'P/L':
                    try:
                        pl = float(value)
                        if pl > 0:
                            item.setForeground(QColor(76, 175, 80))  # Vert
                        elif pl < 0:
                            item.setForeground(QColor(244, 67, 54))  # Rouge
                    except:
                        pass
                        
                self.trades_table.setItem(i, j, item)
                
        self.trades_table.resizeColumnsToContents()
        
    def display_statistics(self, stats):
        """Affiche les statistiques"""
        stats_text = "=== STATISTIQUES ===\n\n"
        
        stats_text += f"Total Trades: {stats.get('total_trades', 0)}\n"
        stats_text += f"Trades Gagnants: {stats.get('winners', 0)}\n"
        stats_text += f"Trades Perdants: {stats.get('losers', 0)}\n"
        stats_text += f"Win Rate: {stats.get('win_rate', 0):.2%}\n\n"
        
        stats_text += f"P/L Total: {stats.get('total_pl', 0):,.2f}€\n"
        stats_text += f"Gain Moyen: {stats.get('avg_win', 0):,.2f}€\n"
        stats_text += f"Perte Moyenne: {stats.get('avg_loss', 0):,.2f}€\n"
        stats_text += f"Profit Factor: {stats.get('profit_factor', 0):.2f}\n\n"
        
        stats_text += f"Max Gain: {stats.get('max_win', 0):,.2f}€\n"
        stats_text += f"Max Perte: {stats.get('max_loss', 0):,.2f}€\n"
        stats_text += f"Sharpe Ratio: {stats.get('sharpe_ratio', 0):.2f}\n"
        stats_text += f"Durée Moyenne: {stats.get('avg_duration', 0):.1f}h\n"
        
        self.stats_text.setText(stats_text)
        
    def update_file_list(self):
        """Met à jour la liste des fichiers"""
        files = self.data_controller.get_loaded_files()
        self.files_table.setRowCount(len(files))
        
        for i, file_name in enumerate(files):
            # Nom du fichier
            self.files_table.setItem(i, 0, QTableWidgetItem(file_name))
            
            # Nombre de trades
            trade_model = self.data_controller.get_trade_model(file_name)
            if trade_model:
                num_trades = len(trade_model.trades)
                self.files_table.setItem(i, 1, QTableWidgetItem(str(num_trades)))
                
            # Statut
            status_item = QTableWidgetItem("✓ Chargé")
            status_item.setForeground(QColor(76, 175, 80))
            self.files_table.setItem(i, 2, status_item)
            
        # Mettre à jour la liste des stratégies dans le filtre
        self.filter_strategy.clear()
        self.filter_strategy.addItem("Toutes les stratégies")
        for file_name in files:
            self.filter_strategy.addItem(file_name)
            
    def apply_filters(self):
        """Applique les filtres aux données"""
        strategy = self.filter_strategy.currentText()
        search_text = self.filter_input.text()
        
        if strategy == "Toutes les stratégies":
            strategy = None
        
        # Filtrer les données
        filtered_df = self.data_controller.filter_trades(
            strategy_name=strategy
        )
        
        # Appliquer la recherche textuelle si nécessaire
        if search_text and not filtered_df.empty:
            mask = filtered_df.astype(str).apply(
                lambda x: x.str.contains(search_text, case=False).any(), 
                axis=1
            )
            filtered_df = filtered_df[mask]
            
        # Afficher les résultats filtrés
        self.populate_trades_table(filtered_df)
        
    def refresh_data(self):
        """Rafraîchit toutes les données affichées"""
        self.update_file_list()
        
        # Mettre à jour les statistiques globales
        stats_df = self.data_controller.get_statistics_summary()
        if not stats_df.empty:
            # Afficher un résumé global
            global_stats = {
                'total_trades': stats_df['total_trades'].sum(),
                'total_pl': stats_df['total_pl'].sum(),
                'avg_win_rate': stats_df['win_rate'].mean(),
                'avg_sharpe': stats_df['sharpe_ratio'].mean()
            }
            
            stats_text = "=== STATISTIQUES GLOBALES ===\n\n"
            stats_text += f"Total Trades (tous fichiers): {global_stats['total_trades']}\n"
            stats_text += f"P/L Total: {global_stats['total_pl']:,.2f}€\n"
            stats_text += f"Win Rate Moyen: {global_stats['avg_win_rate']:.2%}\n"
            stats_text += f"Sharpe Moyen: {global_stats['avg_sharpe']:.2f}\n"
            
            self.stats_text.setText(stats_text)