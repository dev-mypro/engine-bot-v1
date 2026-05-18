import MetaTrader5 as mt5
from datetime import datetime
from typing import Dict, List


class PositionTracker:
    def __init__(self, config: Dict, starting_balance: float):
        self.config = config
        self.starting_balance = starting_balance
        self.trades_today = 0
        self.last_trade_date = datetime.now().date()

        self.max_daily_trades = config.get("current", {}).get("max_daily_trades", 100)
        self.max_positions_per_symbol = config.get("current", {}).get(
            "max_positions_per_symbol", 3
        )
        self.max_total_positions = config.get("current", {}).get(
            "max_total_positions", 10
        )

    def check_new_day(self) -> None:
        """Reset counter if new trading day"""
        current_date = datetime.now().date()
        if current_date > self.last_trade_date:
            print(f"\\n📅 New trading day")
            print(f"   Yesterday's trades: {self.trades_today}")
            self.trades_today = 0
            self.last_trade_date = current_date

    def record_trade(self) -> None:
        self.trades_today += 1

    def get_current_positions(self) -> List:
        """Get all current bot positions"""
        positions = mt5.positions_get()
        if not positions:
            return []
        # Filter only our bot's positions
        return [p for p in positions if p.magic == 234000]

    def get_statistics(self, is_running: bool) -> Dict:
        """Get bot statistics"""
        positions = self.get_current_positions()

        symbol_counts = {}
        for p in positions:
            symbol_counts[p.symbol] = symbol_counts.get(p.symbol, 0) + 1

        total_profit = sum(p.profit for p in positions)

        return {
            "trades_today": self.trades_today,
            "max_daily_trades": self.max_daily_trades,
            "remaining_trades": self.max_daily_trades - self.trades_today,
            "open_positions": len(positions),
            "max_total_positions": self.max_total_positions,
            "positions_by_symbol": symbol_counts,
            "floating_pl": total_profit,
            "is_running": is_running,
            "trade_date": self.last_trade_date.strftime("%Y-%m-%d"),
            "starting_balance": self.starting_balance,
        }
