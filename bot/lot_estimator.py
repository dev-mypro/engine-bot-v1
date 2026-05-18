import MetaTrader5 as mt5

def calculate_dynamic_lot(
    symbol: str, 
    starting_balance: float, 
    risk_percent: float, 
    default_lot: float, 
    dynamic_lot_sizing: bool
) -> float:
    """Calculate dynamic lot size based on balance and risk settings"""
    if not dynamic_lot_sizing:
        return default_lot
        
    try:
        account = mt5.account_info()
        if not account:
            return default_lot
            
        # Use starting balance for consistency
        balance = starting_balance
        risk_amount = balance * (risk_percent / 100.0)
        
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return default_lot
            
        # Estimate SL distance in USD
        if 'XAU' in symbol or 'GOLD' in symbol:
            sl_distance_usd = 10.0  # Average $10 SL for gold
        elif 'BTC' in symbol:
            sl_distance_usd = 500.0  # Bitcoin
        else:
            sl_distance_usd = 20.0  # Approximate for forex
            
        calculated_lot = risk_amount / sl_distance_usd
        calculated_lot = round(calculated_lot, 2)
        
        min_lot = symbol_info.volume_min
        max_lot = min(symbol_info.volume_max, 0.1)  # Cap at 0.1 for safety
        
        calculated_lot = max(min_lot, min(calculated_lot, max_lot))
        return calculated_lot
        
    except Exception as e:
        print(f"Lot calculation error: {e}")
        return default_lot
