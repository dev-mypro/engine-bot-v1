from utils.config_manager import save_config
from utils.mt5_utils import select_symbol
import MetaTrader5 as mt5

def menu_2_change_symbol(config: dict) -> dict:
    current_symbol = config["current"]["symbol"]
    symbol_info = mt5.symbol_info(current_symbol)
    
    print("\\nℹ️ Informasi Symbol Saat Ini:")
    if symbol_info:
        print(f"Symbol: {current_symbol}")
        print(f"Bid: {symbol_info.bid:.5f}")
        print(f"Ask: {symbol_info.ask:.5f}")
        print(f"Spread: {(symbol_info.ask - symbol_info.bid):.5f}")
        print(f"Digit: {symbol_info.digits}")
        print(f"Point: {symbol_info.point:.5f}")
    else:
        print(f"⚠️ Tidak dapat mengambil info untuk {current_symbol}")
    
    all_symbols = mt5.symbols_get()
    if all_symbols:
        common_symbols = ['XAU', 'GOLD', 'EUR', 'GBP', 'JPY']
        popular = [s.name for s in all_symbols if any(pair in s.name for pair in common_symbols)]
        if popular:
            print("\\nPopular symbols:")
            for sym in sorted(popular)[:5]:
                sym_info = mt5.symbol_info(sym)
                if sym_info:
                    print(f"- {sym} (Bid: {sym_info.bid:.5f} | Ask: {sym_info.ask:.5f})")
    
    new_symbol = input(f"\\nMasukkan symbol baru (e.g., EURUSD, XAUUSD, XAUUSDm): ").strip()
    
    if select_symbol(new_symbol):
        config["current"]["symbol"] = new_symbol
        save_config(config)
        new_info = mt5.symbol_info(new_symbol)
        if new_info:
            print(f"\\n✅ Symbol baru {new_symbol}:")
            print(f"Bid: {new_info.bid:.5f}")
            print(f"Ask: {new_info.ask:.5f}")
            print(f"Spread: {(new_info.ask - new_info.bid):.5f}")
            
    return config

def menu_3_change_timeframe(config: dict) -> dict:
    new_tf = input(f"\\nMasukkan timeframe baru (Opsi: {', '.join(config['options']['timeframes'])}): ").strip().upper()
    if new_tf in config["options"]["timeframes"]:
        config["current"]["timeframe"] = new_tf
        save_config(config)
        print(f"✅ Timeframe diubah menjadi: {new_tf}")
    else:
        print(f"❌ Timeframe {new_tf} tidak tersedia!")
    return config

def menu_4_change_candles(config: dict) -> dict:
    try:
        new_count = int(input("\\nMasukkan jumlah candle (contoh: 50, 100): "))
        if new_count > 0:
            config["current"]["candles"] = new_count
            save_config(config)
            print(f"✅ Jumlah candle diatur menjadi: {new_count}")
        else:
            print("❌ Jumlah candle harus positif!")
    except ValueError:
        print("❌ Input harus angka!")
    return config

def menu_5_switch_account(config: dict) -> dict:
    new_acc = input(f"\\nMasukkan tipe akun (Opsi: {', '.join(config['options']['accounts'])}): ").strip().upper()
    if new_acc in config["options"]["accounts"]:
        config["current"]["account"] = new_acc
        save_config(config)
        print(f"✅ Akun diubah menjadi: {new_acc}")
    else:
        print(f"❌ Akun {new_acc} tidak tersedia!")
    return config

def menu_6_change_trade_mode(config: dict) -> dict:
    new_mode = input(f"\\nMasukkan mode trading (Opsi: {', '.join(config['options']['trade_modes'])}): ").strip().upper()
    if new_mode in config["options"]["trade_modes"]:
        config["current"]["trade_mode"] = new_mode
        save_config(config)
        print(f"✅ Mode Trading diubah menjadi: {new_mode}")
    else:
        print(f"❌ Mode Trading {new_mode} tidak tersedia!")
    return config

def menu_8_toggle_auto_trade(config: dict) -> dict:
    config["current"]["auto_trade"] = not config["current"]["auto_trade"]
    save_config(config)
    print(f"✅ Auto Trade diubah menjadi: {'ON' if config['current']['auto_trade'] else 'OFF'}")
    return config

def menu_9_set_auto_lot(config: dict) -> dict:
    try:
        new_lot = float(input("\\nMasukkan ukuran lot (contoh: 0.01, 0.1): "))
        if 0 < new_lot <= 10:
            config["current"]["lot"] = new_lot
            save_config(config)
            print(f"✅ Lot diatur menjadi: {new_lot}")
        else:
            print("❌ Lot harus antara 0.01 dan 10!")
    except ValueError:
        print("❌ Input harus angka!")
    return config

def menu_10_set_auto_slippage(config: dict) -> dict:
    try:
        new_slip = int(input("\\nMasukkan slippage (points): "))
        if new_slip >= 0:
            config["current"]["slippage"] = new_slip
            save_config(config)
            print(f"✅ Slippage diatur menjadi: {new_slip}")
        else:
            print("❌ Slippage tidak bisa negatif!")
    except ValueError:
        print("❌ Input harus angka!")
    return config

def menu_11_toggle_auto_close_profit(config: dict) -> dict:
    config["current"]["auto_close_profit"] = not config["current"]["auto_close_profit"]
    save_config(config)
    print(f"✅ Auto Close Profit diubah menjadi: {'ON' if config['current']['auto_close_profit'] else 'OFF'}")
    return config

def menu_12_set_auto_close_target(config: dict) -> dict:
    try:
        new_target = float(input("\\nMasukkan target USD (contoh: 5.0): "))
        if new_target > 0:
            config["current"]["auto_close_target"] = new_target
            save_config(config)
            print(f"✅ Target Auto Close diatur menjadi: ${new_target}")
        else:
            print("❌ Target harus positif!")
    except ValueError:
        print("❌ Input harus angka!")
    return config

def menu_13_toggle_auto_analyze(config: dict) -> dict:
    config["current"]["auto_analyze"] = not config["current"]["auto_analyze"]
    save_config(config)
    print(f"✅ Auto Analyze diubah menjadi: {'ON' if config['current']['auto_analyze'] else 'OFF'}")
    return config

def menu_14_set_auto_analyze_interval(config: dict) -> dict:
    try:
        new_int = int(input("\\nMasukkan interval (menit): "))
        if new_int > 0:
            config["current"]["auto_analyze_interval"] = new_int
            save_config(config)
            print(f"✅ Interval Auto Analyze diatur menjadi: {new_int} menit")
        else:
            print("❌ Interval harus positif!")
    except ValueError:
        print("❌ Input harus angka!")
    return config

def menu_15_toggle_bep(config: dict) -> dict:
    config["current"]["bep"] = not config["current"]["bep"]
    save_config(config)
    print(f"✅ BEP diubah menjadi: {'ON' if config['current']['bep'] else 'OFF'}")
    return config

def menu_16_set_bep_min_profit(config: dict) -> dict:
    try:
        new_profit = float(input("\\nMasukkan BEP min profit (USD): "))
        if new_profit > 0:
            config["current"]["bep_min_profit"] = new_profit
            save_config(config)
            print(f"✅ BEP Min Profit diatur menjadi: ${new_profit}")
        else:
            print("❌ Profit harus positif!")
    except ValueError:
        print("❌ Input harus angka!")
    return config

def menu_17_set_bep_spread_multiplier(config: dict) -> dict:
    try:
        new_multi = float(input("\\nMasukkan BEP spread multiplier (contoh: 1.0): "))
        if new_multi > 0:
            config["current"]["bep_spread_multiplier"] = new_multi
            save_config(config)
            print(f"✅ BEP Spread Multiplier diatur menjadi: {new_multi}")
        else:
            print("❌ Multiplier harus positif!")
    except ValueError:
        print("❌ Input harus angka!")
    return config

def menu_18_toggle_stpp_trailing(config: dict) -> dict:
    config["current"]["stpp_trailing"] = not config["current"]["stpp_trailing"]
    save_config(config)
    print(f"✅ STPP Trailing diubah menjadi: {'ON' if config['current']['stpp_trailing'] else 'OFF'}")
    return config

def menu_19_set_step_lock_init(config: dict) -> dict:
    try:
        new_init = float(input("\\nMasukkan STEP Lock Init (USD): "))
        if new_init > 0:
            config["current"]["step_lock_init"] = new_init
            save_config(config)
            print(f"✅ STEP Lock Init diatur menjadi: ${new_init}")
        else:
            print("❌ Nilai harus positif!")
    except ValueError:
        print("❌ Input harus angka!")
    return config

def menu_20_set_step_step(config: dict) -> dict:
    try:
        new_step = float(input("\\nMasukkan STEP Step (USD): "))
        if new_step > 0:
            config["current"]["step_step"] = new_step
            save_config(config)
            print(f"✅ STEP Step diatur menjadi: ${new_step}")
        else:
            print("❌ Nilai harus positif!")
    except ValueError:
        print("❌ Input harus angka!")
    return config

def menu_23_set_entry_decimals(config: dict) -> dict:
    try:
        new_dec = input("\\nMasukkan entry decimals (contoh: None/0/1/2): ").strip().lower()
        if new_dec == "none":
            config["current"]["entry_decimals"] = None
        else:
            new_dec = int(new_dec)
            if 0 <= new_dec <= 2:
                config["current"]["entry_decimals"] = new_dec
            else:
                print("❌ Decimals harus 0,1,2, atau 'None'!")
                return config
        save_config(config)
        print(f"✅ Entry Decimals diatur menjadi: {config['current']['entry_decimals']}")
    except ValueError:
        print("❌ Input harus 'None', 0, 1, atau 2!")
    return config

def menu_29_toggle_trade_always_on(config: dict) -> dict:
    config["current"]["trade_always_on"] = not config["current"].get("trade_always_on", False)
    save_config(config)
    print(f"✅ Trade Always On diubah menjadi: {'ON' if config['current']['trade_always_on'] else 'OFF'}")
    return config

def menu_30_change_mode_settings(config: dict) -> dict:
    print("\\n⚙️ TRADING MODE SETTINGS")
    print("="*60)
    print(f"Current Mode: {config['current']['trade_mode']}")
    print(f"Signal Threshold: {config['current'].get('min_signal_strength', 0.2):.0%}")
    print(f"Check Interval: {config['current']['auto_analyze_interval']} min")
    print("="*60)
    
    print("\\n📊 PRESET MODES:")
    print("1) 🔥 SCALPING     - Ultra fast (5% threshold, 1min check, 100 trades/day)")
    print("2) ⚡ AGGRESSIVE   - Fast signals (10% threshold, 2min check, 50 trades/day)")
    print("3) 📈 MODERATE     - Balanced (20% threshold, 5min check, 20 trades/day)")
    print("4) 🛡️  CONSERVATIVE - Safe (35% threshold, 15min check, 10 trades/day)")
    print("5) ⚙️  CUSTOM       - Set your own values")
    print("0) ← Back")
    
    choice = input("\\nSelect preset (0-5): ").strip()
    
    if choice == '0':
        return config
    
    presets = {
        '1': {'trade_mode': 'SCALPING', 'min_signal_strength': 0.05, 'auto_analyze_interval': 1, 'max_daily_trades': 100, 'enable_scalping': True, 'enable_pattern_trading': True, 'enable_breakout_trading': True, 'signal_threshold': 'LOW'},
        '2': {'trade_mode': 'AGGRESSIVE', 'min_signal_strength': 0.1, 'auto_analyze_interval': 2, 'max_daily_trades': 50, 'enable_scalping': True, 'enable_pattern_trading': True, 'enable_breakout_trading': True, 'signal_threshold': 'LOW'},
        '3': {'trade_mode': 'MODERATE', 'min_signal_strength': 0.2, 'auto_analyze_interval': 5, 'max_daily_trades': 20, 'enable_scalping': False, 'enable_pattern_trading': True, 'enable_breakout_trading': True, 'signal_threshold': 'MEDIUM'},
        '4': {'trade_mode': 'CONSERVATIVE', 'min_signal_strength': 0.35, 'auto_analyze_interval': 15, 'max_daily_trades': 10, 'enable_scalping': False, 'enable_pattern_trading': True, 'enable_breakout_trading': False, 'signal_threshold': 'HIGH'}
    }
    
    if choice in presets:
        for key, value in presets[choice].items():
            config['current'][key] = value
        save_config(config)
        print("\\n✅ Settings Applied:")
        print(f"Mode: {config['current']['trade_mode']}")
    elif choice == '5':
        print("\\n⚙️ CUSTOM SETTINGS:")
        try:
            threshold = float(input("Signal threshold (0.05-0.50): "))
            interval = int(input("Check interval in minutes (1-60): "))
            max_trades = int(input("Max daily trades (1-200): "))
            if 0.05 <= threshold <= 0.5 and 1 <= interval <= 60 and 1 <= max_trades <= 200:
                config['current']['min_signal_strength'] = threshold
                config['current']['auto_analyze_interval'] = interval
                config['current']['max_daily_trades'] = max_trades
                config['current']['enable_scalping'] = input("Enable scalping signals? (y/n): ").lower() == 'y'
                config['current']['enable_pattern_trading'] = input("Enable pattern trading? (y/n): ").lower() == 'y'
                config['current']['enable_breakout_trading'] = input("Enable breakout trading? (y/n): ").lower() == 'y'
                config['current']['trade_mode'] = 'CUSTOM'
                save_config(config)
                print("\\n✅ Custom settings saved!")
            else:
                print("❌ Invalid range!")
        except ValueError:
            print("❌ Invalid input!")
    else:
        print("❌ Invalid choice!")
    return config

def menu_31_setup_multi_position(config: dict) -> dict:
    print("\\n⚙️ MULTI-POSITION SETUP")
    print("="*60)
    current = config['current']
    print(f"Current Settings:")
    print(f"  Max positions per symbol: {current.get('max_positions_per_symbol', 1)}")
    print(f"  Max total positions: {current.get('max_total_positions', 5)}")
    print(f"  Multi-symbol: {current.get('enable_multi_symbol', False)}")
    print(f"  Rapid fire mode: {current.get('rapid_fire_mode', False)}")
    
    print("\\n📋 PRESETS:")
    print("1) 🐌 CONSERVATIVE - 1 position per symbol, max 3 total")
    print("2) 📈 MODERATE      - 3 positions per symbol, max 10 total")
    print("3) ⚡ AGGRESSIVE    - 5 positions per symbol, max 20 total")
    print("4) 🔥 RAPID FIRE    - 10 positions per symbol, max 50 total, multi-symbol")
    print("5) ⚙️  CUSTOM        - Set your own")
    print("0) ← Back")
    
    choice = input("\\nSelect preset (0-5): ").strip()
    presets = {
        '1': {'max_positions_per_symbol': 1, 'max_total_positions': 3, 'enable_multi_symbol': False, 'rapid_fire_mode': False, 'max_daily_trades': 20},
        '2': {'max_positions_per_symbol': 3, 'max_total_positions': 10, 'enable_multi_symbol': False, 'rapid_fire_mode': False, 'max_daily_trades': 50},
        '3': {'max_positions_per_symbol': 5, 'max_total_positions': 20, 'enable_multi_symbol': True, 'rapid_fire_mode': False, 'max_daily_trades': 100},
        '4': {'max_positions_per_symbol': 10, 'max_total_positions': 50, 'enable_multi_symbol': True, 'rapid_fire_mode': True, 'enable_multi_timeframe': True, 'max_daily_trades': 200, 'auto_analyze_interval': 1, 'symbols_to_trade': ['XAUUSDm', 'EURUSDm', 'GBPUSDm'], 'timeframes_to_check': ['M1', 'M5', 'M15']}
    }
    
    if choice == '0':
        return config
    
    if choice in presets:
        for key, value in presets[choice].items():
            config['current'][key] = value
        save_config(config)
        print("\\n✅ Settings Applied!")
    elif choice == '5':
        try:
            config['current']['max_positions_per_symbol'] = int(input("Max positions per symbol (1-20): "))
            config['current']['max_total_positions'] = int(input("Max total positions (1-100): "))
            config['current']['enable_multi_symbol'] = input("Enable multi-symbol? (y/n): ").lower() == 'y'
            config['current']['rapid_fire_mode'] = input("Enable rapid fire mode? (y/n): ").lower() == 'y'
            save_config(config)
            print("\\n✅ Custom settings saved!")
        except:
            print("❌ Invalid input")
    return config
