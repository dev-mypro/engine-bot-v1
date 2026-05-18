import pandas as pd
from typing import Dict
from analyzers.indicators import calculate_atr_value

def detect_candlestick_patterns(df: pd.DataFrame) -> Dict:
    """Detect bullish/bearish candlestick patterns"""
    if len(df) < 3:
        return {'signal': 'WAIT', 'patterns': [], 'count': 0}
    
    patterns = []
    signal = 'WAIT'
    
    # Get last 3 candles
    c0 = df.iloc[-1]  # Current
    c1 = df.iloc[-2]  # Previous
    c2 = df.iloc[-3]  # Before previous
    
    # Bullish Patterns
    
    # 1. Bullish Engulfing
    if (c1['close'] < c1['open'] and  # Previous bearish
        c0['close'] > c0['open'] and  # Current bullish
        c0['open'] < c1['close'] and
        c0['close'] > c1['open']):
        patterns.append("Bullish Engulfing (Strong Buy)")
        signal = 'BUY'
    
    # 2. Hammer
    body = abs(c0['close'] - c0['open'])
    lower_shadow = min(c0['close'], c0['open']) - c0['low']
    upper_shadow = c0['high'] - max(c0['close'], c0['open'])
    
    if lower_shadow > body * 2 and upper_shadow < body * 0.3:
        patterns.append("Hammer (Buy)")
        if signal != 'SELL':
            signal = 'BUY'
    
    # 3. Morning Star (3 candles)
    if (c2['close'] < c2['open'] and  # First bearish
        abs(c1['close'] - c1['open']) < body * 0.3 and  # Small body
        c0['close'] > c0['open'] and  # Third bullish
        c0['close'] > (c2['open'] + c2['close']) / 2):
        patterns.append("Morning Star (Strong Buy)")
        signal = 'BUY'
    
    # Bearish Patterns
    
    # 4. Bearish Engulfing
    if (c1['close'] > c1['open'] and  # Previous bullish
        c0['close'] < c0['open'] and  # Current bearish
        c0['open'] > c1['close'] and
        c0['close'] < c1['open']):
        patterns.append("Bearish Engulfing (Strong Sell)")
        signal = 'SELL'
    
    # 5. Shooting Star
    if upper_shadow > body * 2 and lower_shadow < body * 0.3:
        patterns.append("Shooting Star (Sell)")
        if signal != 'BUY':
            signal = 'SELL'
    
    # 6. Evening Star
    if (c2['close'] > c2['open'] and  # First bullish
        abs(c1['close'] - c1['open']) < body * 0.3 and  # Small body
        c0['close'] < c0['open'] and  # Third bearish
        c0['close'] < (c2['open'] + c2['close']) / 2):
        patterns.append("Evening Star (Strong Sell)")
        signal = 'SELL'
    
    # 7. Three White Soldiers (Bullish)
    if (c2['close'] > c2['open'] and
        c1['close'] > c1['open'] and
        c0['close'] > c0['open'] and
        c1['close'] > c2['close'] and
        c0['close'] > c1['close']):
        patterns.append("Three White Soldiers (Strong Buy)")
        signal = 'BUY'
    
    # 8. Three Black Crows (Bearish)
    if (c2['close'] < c2['open'] and
        c1['close'] < c1['open'] and
        c0['close'] < c0['open'] and
        c1['close'] < c2['close'] and
        c0['close'] < c1['close']):
        patterns.append("Three Black Crows (Strong Sell)")
        signal = 'SELL'
    
    return {
        'signal': signal,
        'patterns': patterns,
        'count': len(patterns)
    }

def detect_breakouts(df: pd.DataFrame) -> Dict:
    """Detect support/resistance breakouts"""
    if len(df) < 20:
        return {'signal': 'WAIT', 'breakouts': [], 'count': 0}
    
    breakouts = []
    signal = 'WAIT'
    
    last_close = df['close'].iloc[-1]
    
    # Recent high/low (last 20 bars)
    recent_high = df['high'].iloc[-20:-1].max()
    recent_low = df['low'].iloc[-20:-1].min()
    
    # Breakout detection
    if last_close > recent_high:
        breakouts.append(f"Resistance Breakout at {recent_high:.5f}")
        signal = 'BUY'
    
    if last_close < recent_low:
        breakouts.append(f"Support Breakdown at {recent_low:.5f}")
        signal = 'SELL'
    
    # High volatility breakout
    atr = calculate_atr_value(df)
    price_range = df['high'].iloc[-1] - df['low'].iloc[-1]
    
    if price_range > atr * 1.5:
        breakouts.append("High Volatility Breakout")
        # Direction based on close position
        if df['close'].iloc[-1] > (df['high'].iloc[-1] + df['low'].iloc[-1]) / 2:
            if signal != 'SELL':
                signal = 'BUY'
        else:
            if signal != 'BUY':
                signal = 'SELL'
    
    return {
        'signal': signal,
        'breakouts': breakouts,
        'count': len(breakouts)
    }

def find_support_resistance(df: pd.DataFrame) -> Dict:
    """Find key support and resistance levels"""
    if len(df) < 50:
        return {'support': [], 'resistance': [], 'signal': 'WAIT'}
    
    # Find pivot points
    highs = df['high'].iloc[-50:]
    lows = df['low'].iloc[-50:]
    
    # Simple pivot calculation
    pivot = (df['high'].iloc[-1] + df['low'].iloc[-1] + df['close'].iloc[-1]) / 3
    
    resistance1 = 2 * pivot - lows.min()
    support1 = 2 * pivot - highs.max()
    
    resistance2 = pivot + (highs.max() - lows.min())
    support2 = pivot - (highs.max() - lows.min())
    
    current_price = df['close'].iloc[-1]
    
    signal = 'WAIT'
    
    # Signal based on proximity to S/R
    if abs(current_price - support1) / current_price < 0.002:  # Within 0.2%
        signal = 'BUY'
    elif abs(current_price - resistance1) / current_price < 0.002:
        signal = 'SELL'
    
    return {
        'support': [support2, support1],
        'resistance': [resistance1, resistance2],
        'pivot': pivot,
        'signal': signal,
        'current_price': current_price
    }
