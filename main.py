import time
import MetaTrader5 as mt5

from utils.config_manager import load_config
from utils.mt5_utils import init_mt5
from utils.api_utils import init_gemini
from menus.menu_display import cetak_menu, pilih_menu
from menus.menu_trading import menu_1_analyze_now, menu_7_launch_trainer, menu_99_start_trading
from menus.menu_settings import (
    menu_2_change_symbol, menu_3_change_timeframe, menu_4_change_candles,
    menu_5_switch_account, menu_6_change_trade_mode, menu_8_toggle_auto_trade,
    menu_9_set_auto_lot, menu_10_set_auto_slippage, menu_11_toggle_auto_close_profit,
    menu_12_set_auto_close_target, menu_13_toggle_auto_analyze, menu_14_set_auto_analyze_interval,
    menu_15_toggle_bep, menu_16_set_bep_min_profit, menu_17_set_bep_spread_multiplier,
    menu_18_toggle_stpp_trailing, menu_19_set_step_lock_init, menu_20_set_step_step,
    menu_23_set_entry_decimals, menu_29_toggle_trade_always_on, menu_30_change_mode_settings,
    menu_31_setup_multi_position
)
from menus.menu_triggers import menu_21_set_one_shot, menu_22_cancel_price_trigger
from menus.menu_backtest import (
    menu_24_backtest_custom, menu_25_backtest_7d, menu_26_backtest_14d,
    menu_27_backtest_30d, menu_28_backtest_60d
)

def menu_0_quit() -> bool:
    mt5.shutdown()
    print("\n👋 Menutup MT5 dan keluar...")
    return False

def main():
    config = load_config()
    if not config:
        return
    
    init_mt5()
    from utils.config_manager import load_environment
    env = load_environment()
    gemini_client = init_gemini(env)
    
    mapping_menu = {
        1: lambda c: menu_1_analyze_now(c, gemini_client),
        2: menu_2_change_symbol,
        3: menu_3_change_timeframe,
        4: menu_4_change_candles,
        5: menu_5_switch_account,
        6: menu_6_change_trade_mode,
        7: menu_7_launch_trainer,
        8: menu_8_toggle_auto_trade,
        9: menu_9_set_auto_lot,
        10: menu_10_set_auto_slippage,
        11: menu_11_toggle_auto_close_profit,
        12: menu_12_set_auto_close_target,
        13: menu_13_toggle_auto_analyze,
        14: menu_14_set_auto_analyze_interval,
        15: menu_15_toggle_bep,
        16: menu_16_set_bep_min_profit,
        17: menu_17_set_bep_spread_multiplier,
        18: menu_18_toggle_stpp_trailing,
        19: menu_19_set_step_lock_init,
        20: menu_20_set_step_step,
        0: menu_0_quit,
        21: menu_21_set_one_shot,
        22: lambda c: menu_22_cancel_price_trigger(),
        23: menu_23_set_entry_decimals,
        24: menu_24_backtest_custom,
        25: menu_25_backtest_7d,
        26: menu_26_backtest_14d,
        27: menu_27_backtest_30d,
        28: menu_28_backtest_60d,
        29: menu_29_toggle_trade_always_on,
        30: menu_30_change_mode_settings,
        31: menu_31_setup_multi_position,
        99: lambda c: menu_99_start_trading(c, gemini_client)
    }
    
    running = True
    while running:
        cetak_menu(config)
        pilihan = pilih_menu()
        
        if pilihan in mapping_menu:
            if pilihan in [2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23, 29, 30, 31]:
                config = mapping_menu[pilihan](config)
            elif pilihan == 0:
                running = mapping_menu[pilihan]()
            else:
                mapping_menu[pilihan](config) 
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()