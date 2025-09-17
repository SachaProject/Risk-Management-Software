import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json


class Trade:
    """Représentation d'un trade individuel"""
    
    def __init__(self, trade_data: Dict):
        self.date_opened = pd.to_datetime(trade_data.get('Date Opened', ''))
        self.time_opened = trade_data.get('Time Opened', '')
        self.opening_price = float(trade_data.get('Opening Price', 0))
        self.legs = trade_data.get('Legs', '')
        self.premium = float(trade_data.get('Premium', 0))
        self.closing_price = float(trade_data.get('Closing Price', 0))
        self.date_closed = pd.to_datetime(trade_data.get('Date Closed', ''))
        self.time_closed = trade_data.get('Time Closed', '')
        self.avg_closing_cost = float(trade_data.get('Avg. Closing Cost', 0))
        self.reason_for_close = trade_data.get('Reason For Close', '')
        self.pl = float(trade_data.get('P/L', 0))
        self.num_contracts = int(trade_data.get('No. of Contracts', 0))
        self.funds_at_close = float(trade_data.get('Funds at Close', 0))
        self.margin_req = float(trade_data.get('Margin Req.', 0))
        self.strategy = trade_data.get('Strategy', '')
        self.opening_commissions = float(trade_data.get('Opening Commissions + Fees', 0))
        self.gap = float(trade_data.get('Gap', 0) if trade_data.get('Gap') else 0)
        self.movement = float(trade_data.get('Movement', 0) if trade_data.get('Movement') else 0)
        self.max_profit = float(trade_data.get('Max Profit', 0) if trade_data.get('Max Profit') else 0)
        self.max_loss = float(trade_data.get('Max Loss', 0) if trade_data.get('Max Loss') else 0)
        
    def get_return(self) -> float:
        """Calcule le rendement du trade"""
        if self.margin_req > 0:
            return self.pl / self.margin_req
        return 0
    
    def get_duration(self) -> timedelta:
        """Calcule la durée du trade"""
        if pd.notna(self.date_closed) and pd.notna(self.date_opened):
            return self.date_closed - self.date_opened
        return timedelta(0)
    
    def is_winner(self) -> bool:
        """Détermine si le trade est gagnant"""
        return self.pl > 0
    
    def to_dict(self) -> Dict:
        """Convertit le trade en dictionnaire"""
        return {
            'date_opened': self.date_opened.isoformat() if pd.notna(self.date_opened) else None,
            'opening_price': self.opening_price,
            'closing_price': self.closing_price,
            'pl': self.pl,
            'return': self.get_return(),
            'duration': str(self.get_duration()),
            'is_winner': self.is_winner(),
            'strategy': self.strategy,
            'num_contracts': self.num_contracts
        }


class TradeModel:
    """Modèle pour gérer les données de trading"""
    
    def __init__(self):
        self.trades: List[Trade] = []
        self.df: Optional[pd.DataFrame] = None
        self.file_path: Optional[str] = None
        
    def load_from_csv(self, file_path: str) -> bool:
        """Charge les trades depuis un fichier CSV"""
        try:
            self.df = pd.read_csv(file_path, encoding='utf-8-sig')
            self.file_path = file_path
            self.trades = []
            
            for _, row in self.df.iterrows():
                trade = Trade(row.to_dict())
                self.trades.append(trade)
                
            return True
        except Exception as e:
            print(f"Erreur lors du chargement du CSV: {e}")
            return False
    
    def load_multiple_csv(self, file_paths: List[str]) -> bool:
        """Charge plusieurs fichiers CSV et les combine"""
        all_dfs = []
        
        for path in file_paths:
            try:
                df = pd.read_csv(path, encoding='utf-8-sig')
                df['source_file'] = path
                all_dfs.append(df)
            except Exception as e:
                print(f"Erreur lors du chargement de {path}: {e}")
                
        if all_dfs:
            self.df = pd.concat(all_dfs, ignore_index=True)
            self.trades = []
            
            for _, row in self.df.iterrows():
                trade = Trade(row.to_dict())
                self.trades.append(trade)
                
            return True
        return False
    
    def get_returns(self) -> np.ndarray:
        """Retourne la série des rendements"""
        returns = [trade.get_return() for trade in self.trades]
        return np.array(returns)
    
    def get_daily_returns(self) -> pd.Series:
        """Agrège les trades par jour et calcule les rendements quotidiens"""
        if not self.trades:
            return pd.Series()
            
        daily_pl = {}
        daily_margin = {}
        
        for trade in self.trades:
            if pd.notna(trade.date_closed):
                date = trade.date_closed.date()
                if date not in daily_pl:
                    daily_pl[date] = 0
                    daily_margin[date] = 0
                daily_pl[date] += trade.pl
                daily_margin[date] += trade.margin_req
                
        daily_returns = {}
        for date in daily_pl:
            if daily_margin[date] > 0:
                daily_returns[date] = daily_pl[date] / daily_margin[date]
            else:
                daily_returns[date] = 0
                
        return pd.Series(daily_returns).sort_index()
    
    def get_statistics(self) -> Dict:
        """Calcule les statistiques des trades"""
        if not self.trades:
            return {}
            
        winners = [t for t in self.trades if t.is_winner()]
        losers = [t for t in self.trades if not t.is_winner()]
        
        stats = {
            'total_trades': len(self.trades),
            'winners': len(winners),
            'losers': len(losers),
            'win_rate': len(winners) / len(self.trades) if self.trades else 0,
            'total_pl': sum(t.pl for t in self.trades),
            'avg_win': np.mean([t.pl for t in winners]) if winners else 0,
            'avg_loss': np.mean([t.pl for t in losers]) if losers else 0,
            'profit_factor': abs(sum(t.pl for t in winners) / sum(t.pl for t in losers)) if losers and sum(t.pl for t in losers) != 0 else 0,
            'max_win': max([t.pl for t in winners]) if winners else 0,
            'max_loss': min([t.pl for t in losers]) if losers else 0,
            'avg_duration': np.mean([t.get_duration().total_seconds() / 3600 for t in self.trades]) if self.trades else 0
        }
        
        returns = self.get_returns()
        if len(returns) > 0:
            stats['avg_return'] = np.mean(returns)
            stats['std_return'] = np.std(returns)
            stats['sharpe_ratio'] = stats['avg_return'] / stats['std_return'] * np.sqrt(252) if stats['std_return'] > 0 else 0
            
        return stats
    
    def filter_by_date(self, start_date: datetime, end_date: datetime) -> List[Trade]:
        """Filtre les trades par période"""
        filtered = []
        for trade in self.trades:
            if pd.notna(trade.date_opened) and start_date <= trade.date_opened <= end_date:
                filtered.append(trade)
        return filtered
    
    def filter_by_strategy(self, strategy: str) -> List[Trade]:
        """Filtre les trades par stratégie"""
        return [t for t in self.trades if strategy in t.strategy]
    
    def get_equity_curve(self, initial_capital: float = 100000) -> pd.Series:
        """Calcule la courbe d'équité"""
        if not self.trades:
            return pd.Series([initial_capital])
            
        sorted_trades = sorted(self.trades, key=lambda x: x.date_closed if pd.notna(x.date_closed) else pd.Timestamp.min)
        
        equity = initial_capital
        equity_curve = {pd.Timestamp.now().date(): initial_capital}
        
        for trade in sorted_trades:
            if pd.notna(trade.date_closed):
                equity += trade.pl
                equity_curve[trade.date_closed.date()] = equity
                
        return pd.Series(equity_curve).sort_index()
    
    def calculate_drawdowns(self) -> Tuple[pd.Series, float]:
        """Calcule les drawdowns et le drawdown maximum"""
        equity_curve = self.get_equity_curve()
        
        if len(equity_curve) == 0:
            return pd.Series(), 0
            
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak * 100
        max_drawdown = drawdown.min()
        
        return drawdown, abs(max_drawdown)