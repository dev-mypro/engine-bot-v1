import time
from datetime import datetime
from typing import Dict, Optional
from bot.lot_estimator import calculate_dynamic_lot

def analyze_symbol_timeframe(symbol: str, timeframe: str, analyzer, config: Dict, market_data_func) -> Optional[Dict]:
    """Analyze a single symbol/timeframe combination"""
    try:
        df = market_data_func(symbol, timeframe)
        if df.empty:
            return None
        
        analysis = analyzer.analyze_market(df, symbol, config)
        signal = analysis['overall']['signal']
        strength = analysis['overall']['strength']
        
        if signal != 'WAIT':
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'signal': signal,
                'strength': strength,
                'analysis': analysis
            }
        return None
    except Exception:
        return None

def execute_signal(
    signal_data: Dict, 
    trader, 
    tracker, 
    config: Dict, 
    starting_balance: float, 
    dynamic_lot_sizing: bool, 
    risk_percent: float
) -> bool:
    """Execute a trading signal"""
    try:
        symbol = signal_data['symbol']
        action = signal_data['signal']
        strength = signal_data['strength']
        tf = signal_data['timeframe']
        
        print(f"\n{'='*60}")
        print(f"💰 EXECUTING {action} - {symbol} ({tf})")
        print(f"   Strength: {strength:.0%}")
        
        analysis = signal_data.get('analysis', {})
        if analysis.get('patterns', {}).get('count', 0) > 0:
            patterns = analysis['patterns']['patterns'][:2]
            print(f"   🔥 {', '.join(patterns)}")
            
        lot_size = calculate_dynamic_lot(
            symbol=symbol,
            starting_balance=starting_balance,
            risk_percent=risk_percent,
            default_lot=config['current']['lot'],
            dynamic_lot_sizing=dynamic_lot_sizing
        )
        
        result = trader.place_order({
            'symbol': symbol,
            'action': action,
            'strength': strength,
            'lot_size': lot_size
        })
        
        if result['success']:
            tracker.record_trade()
            
            print(f"✅ SUCCESS! Ticket: #{result.get('ticket')}")
            print(f"   Entry: {result.get('price'):.5f}")
            print(f"   SL: {result.get('sl'):.5f} | TP: {result.get('tp'):.5f}")
            print(f"   Lot: {lot_size}")
            print(f"   Trades: {tracker.trades_today}/{tracker.max_daily_trades}")
            print(f"{'='*60}")
            return True
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown')}")
            print(f"{'='*60}")
            return False
            
    except Exception as e:
        print(f"❌ Execute error: {e}")
        return False
