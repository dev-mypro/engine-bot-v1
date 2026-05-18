import MetaTrader5 as mt5
import pandas as pd

def get_market_data_for(symbol: str, timeframe: str, candles: int) -> pd.DataFrame:
    """Get market data for specific symbol/timeframe from MT5"""
    try:
        tf_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1
        }
        
        mt5_tf = tf_map.get(timeframe, mt5.TIMEFRAME_M5)
        rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, candles)
        
        if rates is None or len(rates) == 0:
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
        
    except Exception as e:
        print(f"Error fetching market data for {symbol}: {e}")
        return pd.DataFrame()
