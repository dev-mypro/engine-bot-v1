import MetaTrader5 as mt5
from datetime import datetime

def should_trade(config: dict) -> bool:
    """Check if trading is allowed based on configurations and account status"""
    if not config.get('current', {}).get('auto_trade', False):
        return False
        
    account = mt5.account_info()
    if account and account.balance < 5:
        # Prevent trading with very low balance
        return False
        
    if config.get('current', {}).get('trade_always_on', True):
        return True
        
    now = datetime.now()
    # Trade only between 01:00 and 23:00 local time if not always on
    return 1 <= now.hour < 23
