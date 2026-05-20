import os
import sys
import pandas as pd
import MetaTrader5 as mt5

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from utils.config_manager import load_config, load_environment
from utils.mt5_utils import init_mt5, ambil_candle
from analyzers.market_analyzer import MarketAnalyzer


def check_market():
    config = load_config()
    if not config:
        print("❌ Gagal load config.json")
        return

    print(f"Auto Trade Enabled: {config['current'].get('auto_trade')}")
    print(f"Trade Mode: {config['current'].get('trade_mode')}")
    print(f"Symbol: {config['current'].get('symbol')}")
    print(f"Timeframe: {config['current'].get('timeframe')}")
    print(f"Min Signal Strength: {config['current'].get('min_signal_strength')}")
    print(
        f"Ignore Economic Calendar: {config['current'].get('ignore_economic_calendar')}"
    )

    if not init_mt5():
        print("❌ Gagal terhubung ke MT5")
        return

    # Account info
    acc_info = mt5.account_info()
    if acc_info:
        print(f"\n💰 SALDO AKUN: {acc_info.balance} {acc_info.currency}")
        print(f"💰 EQUITY: {acc_info.equity}")
        print(f"💰 MARGIN FREE: {acc_info.margin_free}")
    else:
        print("❌ Gagal mengambil info akun")

    # Fetch candles
    symbol = config["current"]["symbol"]
    tf = config["current"]["timeframe"]
    candles_count = config["current"].get("candles", 100)

    print(f"\nMengambil {candles_count} candles untuk {symbol} ({tf})...")
    df = ambil_candle(symbol, tf, candles_count)
    if df.empty:
        print("❌ Gagal mengambil rates/candles")
        mt5.shutdown()
        return

    print(f"Terkumpul {len(df)} candles.")
    print(f"Close price terakhir: {df['close'].iloc[-1]}")

    # Analyze
    analyzer = MarketAnalyzer()

    # Run technical analysis
    tech = analyzer._analyze_technical(df)
    print("\n--- ANALISIS TEKNIKAL ---")
    print(f"Signal: {tech.get('signal')}")
    print(f"Bullish count: {tech.get('bullish')}")
    print(f"Bearish count: {tech.get('bearish')}")
    print(f"Signals list:")
    for sig in tech.get("signals", []):
        print(f" - {sig}")

    # Run scalping signals
    scalping = analyzer._scalping_signals(df)
    print("\n--- ANALISIS SCALPING ---")
    print(f"Signal: {scalping.get('signal')}")
    print(f"Confirmations: {scalping.get('confirmations')}/9")
    print(f"Signals list:")
    for sig in scalping.get("signals", []):
        print(f" - {sig}")

    # Run full combination in current mode
    analysis = analyzer.analyze_market(df, symbol, config)
    print("\n--- HASIL ANALISIS AKHIR (OVERALL - CURRENT MODE) ---")
    print(f"Final Signal: {analysis['overall'].get('signal')}")
    print(f"Final Strength: {analysis['overall'].get('strength')}")
    print(f"Reasons:")
    for r in analysis["overall"].get("reasons", []):
        print(f" - {r}")

    # Run full combination in NORMAL mode
    config_normal = config.copy()
    config_normal["current"] = config["current"].copy()
    config_normal["current"]["trade_mode"] = "NORMAL"
    analysis_normal = analyzer.analyze_market(df, symbol, config_normal)
    print("\n--- HASIL ANALISIS AKHIR (OVERALL - NORMAL MODE) ---")
    print(f"Final Signal: {analysis_normal['overall'].get('signal')}")
    print(f"Final Strength: {analysis_normal['overall'].get('strength')}")
    print(f"Reasons:")
    for r in analysis_normal["overall"].get("reasons", []):
        print(f" - {r}")

    mt5.shutdown()


if __name__ == "__main__":
    check_market()
