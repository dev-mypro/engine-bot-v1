import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from utils.config_manager import load_environment

env = load_environment()
mt5_terhubung = False

def is_connected() -> bool:
    return mt5_terhubung

def get_available_symbols() -> list:
    """Get list of available symbols with variations"""
    symbols = []
    if mt5_terhubung:
        # Get all symbols
        all_symbols = mt5.symbols_get()
        if all_symbols:
            for symbol_info in all_symbols:
                name = symbol_info.name
                # Check for common forex pairs and variations
                if any(pair in name for pair in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'XAUUSD', 'BTCUSD']):
                    symbols.append(name)
    return symbols

def init_mt5() -> bool:
    global mt5_terhubung
    
    # Shutdown existing connection if any
    if mt5.initialize():
        mt5.shutdown()
    
    # Try multiple MT5 installation paths
    mt5_paths = [
        "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
        "C:\\Program Files (x86)\\MetaTrader 5\\terminal64.exe",
        None  # Let MT5 find the path automatically
    ]
    
    for path in mt5_paths:
        try:
            if mt5.initialize(
                login=env["mt5_login"],
                password=env["mt5_password"],
                server=env["mt5_server"],
                path=path
            ):
                # Test connection by getting account info
                akun = mt5.account_info()
                if akun:
                    print(f"\\n✅ Terhubung ke MT5 | Akun: {akun.login} | Saldo: {akun.balance} {akun.currency}")
                    mt5_terhubung = True
                    
                    # Get and subscribe to available symbols
                    all_symbols = mt5.symbols_get()
                    if all_symbols:
                        common_prefixes = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "BTCUSD"]
                        found_symbols = []
                        
                        # Find available variants
                        for prefix in common_prefixes:
                            for sym in all_symbols:
                                if sym.name.upper().startswith(prefix):
                                    if mt5.symbol_select(sym.name, True):
                                        print(f"✅ Subscribe {sym.name}")
                                        found_symbols.append(sym.name)
                                    break  # Take first matching variant
                        
                        if found_symbols:
                            print(f"\\nℹ️ Subscribed to: {', '.join(found_symbols)}")
                        else:
                            print("\\n⚠️ No common symbols found. Please select symbols manually.")
                    
                    return True
        except Exception as e:
            print(f"⚠️ Error path {path}: {str(e)}")
            continue
    
    print(f"\\n❌ Gagal terhubung MT5 | Error: {mt5.last_error()}")
    mt5_terhubung = False
    return False

def map_timeframe(timeframe_str: str) -> int:
    mapping = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }
    return mapping.get(timeframe_str, mt5.TIMEFRAME_M30)

def select_symbol(symbol_baru: str) -> bool:
    """Select a symbol in MT5 with fallback variations"""
    all_symbols = mt5.symbols_get()
    available_symbols = []
    if all_symbols:
        for symbol_info in all_symbols:
            available_symbols.append(symbol_info.name)
    
    symbol_upper = symbol_baru.upper()
    
    for available in available_symbols:
        if available.upper() == symbol_upper:
            if mt5.symbol_select(available, True):
                print(f"✅ Symbol {available} selected")
                return True
    
    variations = [
        symbol_upper,
        f"{symbol_upper}m",
        f"{symbol_upper}-m",
        f"{symbol_upper}.a",
        f"{symbol_upper}-a",
        f"{symbol_upper}_m",
        symbol_upper.replace('XAU', 'GOLD'),
        symbol_upper.replace('GOLD', 'XAU')
    ]
    
    for variant in variations:
        for available in available_symbols:
            if available.upper() == variant:
                if mt5.symbol_select(available, True):
                    print(f"✅ Found matching symbol: {available}")
                    return True
    
    print(f"❌ Symbol {symbol_baru} not found")
    return False

def ambil_candle(symbol: str, timeframe: str, jumlah: int) -> pd.DataFrame:
    if not mt5_terhubung:
        print("❌ MT5 belum terhubung!")
        return pd.DataFrame()
    
    if not select_symbol(symbol):
        return pd.DataFrame()

    mt5_tf = map_timeframe(timeframe)
    data = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, jumlah)
    
    if data is None:
        from_date = pd.Timestamp.now() - pd.Timedelta(days=5)
        to_date = pd.Timestamp.now()
        data = mt5.copy_rates_range(symbol, mt5_tf, from_date.timetuple(), to_date.timetuple())
    
    if data is None:
        print(f"❌ Gagal mengambil candle | Error: {mt5.last_error()}")
        if init_mt5():
            print("✅ Berhasil reconnect MT5")
            data = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, jumlah)
    
    if data is None:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

def get_account_summary() -> dict:
    """Get account summary including today's P&L"""
    if not mt5_terhubung:
        return None
        
    account = mt5.account_info()
    if not account:
        return None
    
    from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    to_date = datetime.now()
    
    deals = mt5.history_deals_get(from_date, to_date)
    
    today_profit = 0
    today_loss = 0
    total_trades = 0
    
    if deals:
        for deal in deals:
            if deal.type in [0, 1]:  # Buy or Sell deals only
                if deal.profit != 0:  # Closing deals
                    total_trades += 1
                    if deal.profit > 0:
                        today_profit += deal.profit
                    else:
                        today_loss += abs(deal.profit)
    
    starting_balance = account.balance - (today_profit - today_loss)
    profit_percent = (today_profit / starting_balance * 100) if starting_balance > 0 else 0
    loss_percent = (today_loss / starting_balance * 100) if starting_balance > 0 else 0
    
    positions = mt5.positions_get()
    open_positions = len(positions) if positions else 0
    floating_pl = sum(pos.profit for pos in positions) if positions else 0
    
    return {
        'balance': account.balance,
        'equity': account.equity,
        'margin': account.margin,
        'free_margin': account.margin_free,
        'currency': account.currency,
        'leverage': account.leverage,
        'today_profit': today_profit,
        'today_loss': today_loss,
        'today_net': today_profit - today_loss,
        'profit_percent': profit_percent,
        'loss_percent': loss_percent,
        'total_trades': total_trades,
        'open_positions': open_positions,
        'floating_pl': floating_pl
    }
