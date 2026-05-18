import pandas as pd
import numpy as np
import MetaTrader5 as mt5

def calculate_sl_tp(symbol: str, price: float, action: str, atr: float, point: float, digits: int, stops_level: int) -> tuple:
    if 'XAU' in symbol or 'GOLD' in symbol:
        sl_distance = max(atr * 1.5, 3.0)
        tp_distance = max(atr * 2.0, 5.0)
    else:
        sl_pips = max(int(atr / point * 1.5), 20)
        tp_pips = max(int(atr / point * 2.0), 40)
        sl_distance = sl_pips * point
        tp_distance = tp_pips * point
    
    min_distance = stops_level * point
    if min_distance > 0:
        sl_distance = max(sl_distance, min_distance * 2)
        tp_distance = max(tp_distance, min_distance * 2)
    
    if action == 'BUY':
        sl = round(price - sl_distance, digits)
        tp = round(price + tp_distance, digits)
    else:
        sl = round(price + sl_distance, digits)
        tp = round(price - tp_distance, digits)
        
    return sl, tp

def get_risk_atr(symbol: str, period: int = 14) -> float:
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, period + 1)
    
    if rates is None or len(rates) < period:
        if 'XAU' in symbol or 'GOLD' in symbol: return 8.0
        elif 'BTC' in symbol: return 500.0
        else: return 0.0010
    
    df = pd.DataFrame(rates)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean().iloc[-1]
    
    if pd.isna(atr) or atr == 0:
        if 'XAU' in symbol or 'GOLD' in symbol: return 8.0
        else: return 0.0010
    
    return atr
