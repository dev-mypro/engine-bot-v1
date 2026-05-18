from utils.mt5_utils import get_account_summary, get_available_symbols

last_backtest_result = None

def set_last_backtest_result(result):
    global last_backtest_result
    last_backtest_result = result

def cetak_menu(config: dict) -> None:
    global last_backtest_result
    current = config["current"]
    options = config["options"]
    
    def status(value):
        return "ON" if value else "OFF"

    def format_line(num, text, current_val, hint=""):
        text = text.replace("Toggle ", "").replace("Set ", "")
        line = f"{num:>2}) {text:<25}"
        current_str = f"(current: {current_val})"
        line = f"{line}{current_str:<25}"
        if hint:
            line += f" {hint}"
        print(line)

    print("\\n" + "="*90)

    if last_backtest_result:
        print(last_backtest_result)
        last_backtest_result = None
    else:
        summary = get_account_summary()
        if summary:
            pl_sign = "+" if summary['today_net'] >= 0 else "-"
            print(f"💰 Balance: ${summary['balance']:.2f} | Equity: ${summary['equity']:.2f} | Today's P/L: {pl_sign}${abs(summary['today_net']):.2f} | Open: {summary['open_positions']}")

    print("="*90)
    print("Menu:")
    print(" 1) Analyze now")
    format_line(2, "Change SYMBOL", current['symbol'], f"available: {', '.join(get_available_symbols()[:5])}...")
    format_line(3, "Change TIMEFRAME", current['timeframe'], f"options: {', '.join(options['timeframes'])}")
    format_line(4, "Change CANDLES", current['candles'], "e.g. 50 / 100 / 200")
    format_line(5, "Switch ACCOUNT", current['account'], f"options: {', '.join(options['accounts'])}")
    format_line(6, "Change TRADE MODE", current['trade_mode'], f"options: {', '.join(options['trade_modes'])}")
    print(" 7) Launch external TRAINER window (every 10s, bars=800)")
    format_line(8, "Toggle AUTO-TRADE", status(current['auto_trade']))
    format_line(9, "Set AUTO lot", current['lot'])
    format_line(10, "Set AUTO slippage (dev)", current['slippage'])
    format_line(11, "Toggle AUTO-CLOSE profit", status(current['auto_close_profit']))
    format_line(12, "Set AUTO-CLOSE target USD", current['auto_close_target'])
    format_line(13, "Toggle AUTO-ANALYZE", status(current['auto_analyze']))
    format_line(14, "Set AUTO-ANALYZE interval minutes", current['auto_analyze_interval'])
    format_line(15, "Toggle BEP", status(current['bep']))
    format_line(16, "Set BEP min profit USD", current['bep_min_profit'])
    format_line(17, "Set BEP spread multiplier", current['bep_spread_multiplier'])
    format_line(18, "Toggle STEP TRAILING", status(current['stpp_trailing']))
    format_line(19, "Set STEP lock init USD", current['step_lock_init'])
    format_line(20, "Set STEP step USD", current['step_step'])
    print(" 0) Quit")

    print("\\n-- Price Trigger --")
    print("21) Set ONE-SHOT price trigger (symbol, side, price, lot, SL, TP, int-match)")
    print("22) Cancel price trigger")
    format_line(23, "Set ENTRY match decimals", current.get('entry_decimals'), "e.g. None/0/1/2")

    print("\\n-- Backtest --")
    print("24) Backtest (custom range) -> CSV")
    print("25) Backtest 1 minggu (last 7d)")
    print("26) Backtest 2 minggu (last 14d)")
    print("27) Backtest 1 bulan (last 30d)")
    print("28) Backtest 2 bulan (last 60d)")

    print("\\n-- General --")
    format_line(29, "Toggle TRADE ALWAYS ON", status(current.get('trade_always_on', False)))
    print("30) Change mode (SCALPING/AGGRESSIVE/MODERATE/CONSERVATIVE)")
    print("31) Multi-position setup (RAPID FIRE mode)")
    
    print("\\n-- Controls --")
    print("99) START TRADING")
    print("-" * 90)

def pilih_menu() -> int:
    pilihan = input("Select: ").strip()
    if not pilihan:
        print("❌ Silakan masukkan pilihan menu!")
        return -1
        
    try:
        nilai = int(pilihan)
        valid_options = list(range(0, 32)) + [99]
        if nilai not in valid_options:
            print(f"❌ Pilihan {nilai} tidak tersedia dalam menu!")
            return -1
        return nilai
    except ValueError:
        print(f"❌ '{pilihan}' bukan pilihan yang valid! Masukkan nomor menu (0-31 atau 99)")
        return -1
