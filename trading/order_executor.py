import MetaTrader5 as mt5
from typing import Optional

def get_filling_type(symbol_info) -> int:
    """Determine the correct filling type for the symbol"""
    filling_modes = symbol_info.filling_mode
    if filling_modes & 2:
        return mt5.ORDER_FILLING_FOK
    elif filling_modes & 1:
        return mt5.ORDER_FILLING_IOC
    else:
        return mt5.ORDER_FILLING_RETURN

def modify_position(ticket: int, new_sl: Optional[float] = None, new_tp: Optional[float] = None) -> bool:
    """Modify existing position's SL/TP"""
    try:
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return False
        
        pos = position[0]
        symbol_info = mt5.symbol_info(pos.symbol)
        
        sl = new_sl if new_sl is not None else pos.sl
        tp = new_tp if new_tp is not None else pos.tp
        
        if sl:
            sl = round(sl, symbol_info.digits)
        if tp:
            tp = round(tp, symbol_info.digits)
        
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "symbol": pos.symbol,
            "sl": sl,
            "tp": tp
        }
        
        result = mt5.order_send(request)
        return result.retcode == mt5.TRADE_RETCODE_DONE
        
    except Exception as e:
        print(f"Error modifying position: {e}")
        return False

def close_position(ticket: int, slippage: int = 20) -> bool:
    """Close specific position"""
    try:
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return False
        
        pos = position[0]
        symbol_info = mt5.symbol_info(pos.symbol)
        tick = mt5.symbol_info_tick(pos.symbol)
        
        if not tick:
            return False
        
        close_price = tick.bid if pos.type == 0 else tick.ask
        filling_type = get_filling_type(symbol_info)
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
            "price": close_price,
            "deviation": slippage,
            "magic": 234000,
            "comment": "Bot Close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_type,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"✅ Position {ticket} closed at {close_price}")
            return True
        else:
            print(f"❌ Close failed: {result.comment}")
            return False
            
    except Exception as e:
        print(f"Error closing position: {e}")
        return False
