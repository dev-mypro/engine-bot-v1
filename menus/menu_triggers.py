import MetaTrader5 as mt5
from datetime import datetime
import time
import threading
from utils.mt5_utils import select_symbol

price_triggers = []


def monitor_price_triggers():
    while True:
        try:
            for trigger in price_triggers:
                if trigger["status"] != "PENDING":
                    continue

                tick = mt5.symbol_info_tick(trigger["symbol"])
                if not tick:
                    continue

                current_price = tick.bid if trigger["side"] == "SELL" else tick.ask

                triggered = False
                if (
                    trigger["side"] == "BUY"
                    and current_price <= trigger["trigger_price"]
                ):
                    triggered = True
                elif (
                    trigger["side"] == "SELL"
                    and current_price >= trigger["trigger_price"]
                ):
                    triggered = True

                if triggered:
                    print(
                        f"\\n🔔 TRIGGER HIT! {trigger['symbol']} {trigger['side']} @ {current_price:.5f}"
                    )

                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": trigger["symbol"],
                        "volume": trigger["lot"],
                        "type": mt5.ORDER_TYPE_BUY
                        if trigger["side"] == "BUY"
                        else mt5.ORDER_TYPE_SELL,
                        "price": current_price,
                        "deviation": 20,
                        "magic": 234000,
                        "comment": f"Trigger #{trigger['id']}",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }

                    if trigger["sl"]:
                        request["sl"] = trigger["sl"]
                    if trigger["tp"]:
                        request["tp"] = trigger["tp"]

                    result = mt5.order_send(request)

                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        trigger["status"] = "EXECUTED"
                        trigger["executed_price"] = current_price
                        trigger["executed_at"] = datetime.now()
                        trigger["ticket"] = result.order
                        print(f"✅ Order executed! Ticket: {result.order}")
                    else:
                        trigger["status"] = "FAILED"
                        print(f"❌ Order failed: {result.comment}")

            time.sleep(1)
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(5)


def menu_21_set_one_shot(config: dict) -> None:
    print("\\n🎯 SET PRICE TRIGGER ORDER")
    print("=" * 50)
    try:
        symbol = (
            input(f"Symbol [{config['current']['symbol']}]: ").strip()
            or config["current"]["symbol"]
        )
        if not select_symbol(symbol):
            print("❌ Invalid symbol")
            return

        side = input("Side (BUY/SELL): ").strip().upper()
        if side not in ["BUY", "SELL"]:
            print("❌ Side must be BUY or SELL")
            return

        trigger_price = float(input("Trigger Price: "))
        lot = float(
            input(f"Lot Size [{config['current']['lot']}]: ")
            or config["current"]["lot"]
        )

        tick = mt5.symbol_info_tick(symbol)
        if tick:
            print(f"\\n📊 Current Market: Bid: {tick.bid:.5f} | Ask: {tick.ask:.5f}")

        sl_input = input("Stop Loss (price or leave empty): ").strip()
        sl = float(sl_input) if sl_input else None

        tp_input = input("Take Profit (price or leave empty): ").strip()
        tp = float(tp_input) if tp_input else None

        trigger = {
            "id": len(price_triggers) + 1,
            "symbol": symbol,
            "side": side,
            "trigger_price": trigger_price,
            "lot": lot,
            "sl": sl,
            "tp": tp,
            "created_at": datetime.now(),
            "status": "PENDING",
            "triggered": False,
        }
        price_triggers.append(trigger)

        print("\\n✅ Price Trigger Created:")
        print(f"ID: {trigger['id']} | {symbol} {side} @ {trigger_price:.5f}")

        monitor_thread = threading.Thread(target=monitor_price_triggers, daemon=True)
        monitor_thread.start()
        print("\\n🔍 Price monitoring started...")

    except ValueError:
        print("❌ Invalid input format")
    except Exception as e:
        print(f"❌ Error: {e}")


def menu_22_cancel_price_trigger() -> None:
    global price_triggers
    if not price_triggers:
        print("\\n❌ No active price triggers")
        return

    print("\\n📋 ACTIVE PRICE TRIGGERS")
    print("=" * 50)
    for trigger in price_triggers:
        if trigger["status"] == "PENDING":
            print(
                f"ID: {trigger['id']} | {trigger['symbol']} | {trigger['side']} @ {trigger['trigger_price']:.5f}"
            )

    try:
        trigger_id = input("\\nEnter Trigger ID to cancel (or 'all'): ").strip()
        if trigger_id.lower() == "all":
            cancelled = sum(
                1
                for t in price_triggers
                if t["status"] == "PENDING"
                and (t.update({"status": "CANCELLED"}) or True)
            )
            print(f"✅ Cancelled {cancelled} triggers")
        else:
            trigger_id = int(trigger_id)
            for trigger in price_triggers:
                if trigger["id"] == trigger_id and trigger["status"] == "PENDING":
                    trigger["status"] = "CANCELLED"
                    print(f"✅ Trigger {trigger_id} cancelled")
                    return
            print(f"❌ Trigger {trigger_id} not found")
    except ValueError:
        print("❌ Invalid input")
