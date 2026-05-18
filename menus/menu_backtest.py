import pandas as pd
import MetaTrader5 as mt5
from utils.mt5_utils import map_timeframe
from menus.menu_display import set_last_backtest_result

def backtest_umum(config: dict, hari: int) -> None:
    print(f"\\n🔄 Backtest {config['current']['symbol']} ({config['current']['timeframe']}) selama {hari} hari...")
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.Timedelta(days=hari)
    
    mt5_start = start_date.timetuple()
    mt5_end = end_date.timetuple()
    mt5_tf = map_timeframe(config["current"]["timeframe"])
    
    data = mt5.copy_rates_range(
        config["current"]["symbol"],
        mt5_tf,
        mt5_start,
        mt5_end
    )
    
    if data is None:
        result_msg = f"❌ Backtest gagal | Error: {mt5.last_error()}"
        print(result_msg)
        set_last_backtest_result(result_msg)
        return
    
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    print(f"✅ Data backtest loaded | Baris: {len(df)} | Tanggal: {df['time'].min()} to {df['time'].max()}")
    
    csv_name = f"backtest_{config['current']['symbol']}_{hari}d.csv"
    df.to_csv(csv_name, index=False)
    
    result_msg = f"✅ Backtest {hari} hari selesai. Disimpan ke {csv_name}"
    print(result_msg)
    set_last_backtest_result(result_msg)

def menu_24_backtest_custom(config: dict) -> None:
    print("\\n📅 Backtest Kustom: Masukkan tanggal (YYYY-MM-DD)")
    try:
        start_str = input("Tanggal Mulai: ")
        end_str = input("Tanggal Akhir: ")
        start_date = pd.Timestamp(start_str)
        end_date = pd.Timestamp(end_str)
        
        mt5_start = start_date.timetuple()
        mt5_end = end_date.timetuple()
        mt5_tf = map_timeframe(config["current"]["timeframe"])
        
        data = mt5.copy_rates_range(
            config["current"]["symbol"],
            mt5_tf,
            mt5_start,
            mt5_end
        )
        
        if data is None:
            print(f"❌ Backtest gagal | Error: {mt5.last_error()}")
            return
        
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        csv_name = f"backtest_{config['current']['symbol']}_kustom.csv"
        df.to_csv(csv_name, index=False)
        result_msg = f"✅ Backtest kustom disimpan ke: {csv_name}"
        print(result_msg)
        set_last_backtest_result(result_msg)
    except Exception as e:
        print(f"❌ Format tanggal salah | Error: {str(e)}")

def menu_25_backtest_7d(config: dict) -> None:
    backtest_umum(config, hari=7)

def menu_26_backtest_14d(config: dict) -> None:
    backtest_umum(config, hari=14)

def menu_27_backtest_30d(config: dict) -> None:
    backtest_umum(config, hari=30)

def menu_28_backtest_60d(config: dict) -> None:
    backtest_umum(config, hari=60)
