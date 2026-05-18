# bot/bot_manager.py - ULTRA LEAN VERSION
from typing import Dict, List
import time
import MetaTrader5 as mt5
import pandas as pd

from bot.position_tracker import PositionTracker
from bot.market_data_provider import get_market_data_for
from bot.trading_rules import should_trade
from bot.cycle_runner import CycleRunner

class TradingBot:
    def __init__(self, config: Dict, analyzer, trader, gemini_client=None):
        self.config = config
        self.analyzer = analyzer
        self.trader = trader
        self.gemini_client = gemini_client
        self.running = False
        self.last_analysis_time = 0
        
        # Get account info for balance tracking
        account = mt5.account_info()
        if account:
            self.starting_balance = account.balance
            if config.get('current', {}).get('starting_balance', 0) == 0:
                config['current']['starting_balance'] = account.balance
        else:
            self.starting_balance = config.get('current', {}).get('starting_balance', 100)
            
        # Initialize sub-modules
        self.tracker = PositionTracker(config, self.starting_balance)
        self.runner = CycleRunner(self)
        
        # Multi-symbol/timeframe
        self.enable_multi_symbol = config.get('current', {}).get('enable_multi_symbol', False)
        self.enable_multi_timeframe = config.get('current', {}).get('enable_multi_timeframe', False)
        self.symbols_to_trade = config.get('current', {}).get('symbols_to_trade', [config['current']['symbol']])
        self.timeframes_to_check = config.get('current', {}).get('timeframes_to_check', ['M5'])
        
        # Rapid fire mode
        self.rapid_fire_mode = config.get('current', {}).get('rapid_fire_mode', False)
        
        # Dynamic lot sizing
        self.dynamic_lot_sizing = config.get('current', {}).get('dynamic_lot_sizing', False)
        self.risk_percent = config.get('current', {}).get('risk_percent_per_trade', 1.0)
        
        # Check interval
        self.check_interval = config.get('current', {}).get('auto_analyze_interval', 1) * 60
        
        if self.rapid_fire_mode:
            self.check_interval = 10  # Check every 10 seconds in rapid fire mode
        
        print(f"🤖 Bot initialized - RAPID FIRE MODE:")
        print(f"   Starting Balance: ${self.starting_balance:.2f}")
        print(f"   Max trades/day: {self.tracker.max_daily_trades}")
        print(f"   Max positions per symbol: {self.tracker.max_positions_per_symbol}")
        print(f"   Max total positions: {self.tracker.max_total_positions}")
        print(f"   Auto-close profit: ${config.get('current', {}).get('auto_close_target', 0.4):.2f}")
        print(f"   Check interval: {self.check_interval}s")
        print(f"   Multi-symbol: {'✅' if self.enable_multi_symbol else '❌'}")
        print(f"   Dynamic lot sizing: {'✅' if self.dynamic_lot_sizing else '❌'}")
        print(f"   Rapid fire: {'✅' if self.rapid_fire_mode else '❌'}")
        
    def start(self) -> None:
        """Start the trading bot"""
        self.running = True
        
        print(f"🚀 RAPID FIRE Bot Started!")
        print(f"⚡ Symbols: {', '.join(self.symbols_to_trade)}")
        print(f"⏱️ Checking every {self.check_interval}s")
        print(f"🛑 MAX {self.tracker.max_total_positions} POSITIONS - Will STOP when full!")
        print("Press Ctrl+C to stop\n")
        
        while self.running:
            try:
                # Reset daily counter if new day
                self.tracker.check_new_day()
                
                # ALWAYS manage positions first (for auto-close)
                self.trader.manage_open_positions()
                
                # Run trading cycle
                if self.rapid_fire_mode:
                    self.runner.run_rapid_fire_cycle()
                else:
                    self.runner.run_cycle()
                
                # Wait before next cycle
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️ Stopping bot...")
                self.stop()
                break
                
            except Exception as e:
                print(f"❌ Cycle error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(10)
    
    def stop(self) -> None:
        """Stop the trading bot"""
        self.running = False
        
        # Get final stats
        positions = self.tracker.get_current_positions()
        open_count = len(positions)
        
        total_profit = sum(p.profit for p in positions)
        
        account = mt5.account_info()
        if account:
            current_balance = account.balance
            profit_from_start = current_balance - self.starting_balance
        else:
            profit_from_start = 0
        
        print(f"\n🛑 Bot stopped")
        print(f"📊 Final stats:")
        print(f"   Starting balance: ${self.starting_balance:.2f}")
        print(f"   Current balance: ${account.balance:.2f}" if account else "")
        print(f"   Profit/Loss: ${profit_from_start:+.2f}")
        print(f"   Trades executed: {self.tracker.trades_today}/{self.tracker.max_daily_trades}")
        print(f"   Open positions: {open_count}")
        print(f"   Floating P/L: ${total_profit:+.2f}")
    
    def _should_trade(self) -> bool:
        return should_trade(self.config)
    
    def _get_market_data(self) -> pd.DataFrame:
        return self._get_market_data_for(
            self.config['current']['symbol'],
            self.config['current']['timeframe']
        )
    
    def _get_market_data_for(self, symbol: str, timeframe: str) -> pd.DataFrame:
        return get_market_data_for(
            symbol=symbol,
            timeframe=timeframe,
            candles=self.config['current']['candles']
        )
    
    def get_statistics(self) -> Dict:
        return self.tracker.get_statistics(self.running)