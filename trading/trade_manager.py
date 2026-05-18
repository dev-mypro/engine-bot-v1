from typing import Dict
import MetaTrader5 as mt5
from datetime import datetime
from trading.risk_manager import calculate_sl_tp, get_risk_atr
from trading.order_executor import get_filling_type, modify_position, close_position


class TradeManager:
    def __init__(self, config: Dict):
        self.config = config
        self.positions = {}

    def place_order(self, signal: Dict) -> Dict:
        """Place order with proper SL/TP calculation"""
        try:
            symbol = signal["symbol"]
            action = signal["action"]
            lot_size = signal.get("lot_size", self.config["current"]["lot"])

            if action not in ["BUY", "SELL"]:
                return {"success": False, "error": "Invalid action"}

            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                return {"success": False, "error": "Symbol info not available"}

            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                return {"success": False, "error": "Could not get price"}

            price = tick.ask if action == "BUY" else tick.bid
            point = symbol_info.point
            digits = symbol_info.digits
            stops_level = symbol_info.trade_stops_level

            atr = get_risk_atr(symbol)
            sl, tp = calculate_sl_tp(
                symbol, price, action, atr, point, digits, stops_level
            )

            if action == "BUY":
                if sl >= price or tp <= price:
                    return {
                        "success": False,
                        "error": f"Invalid SL/TP: Price={price}, SL={sl}, TP={tp}",
                    }
            else:
                if sl <= price or tp >= price:
                    return {
                        "success": False,
                        "error": f"Invalid SL/TP: Price={price}, SL={sl}, TP={tp}",
                    }

            if not symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL:
                return {
                    "success": False,
                    "error": "Trading not allowed for this symbol",
                }

            filling_type = get_filling_type(symbol_info)
            slippage = self.config["current"]["slippage"]

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": slippage,
                "magic": 234000,
                "comment": f"Bot {signal.get('strength', 0):.0%}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling_type,
            }

            print(f"\\n📋 Order Request:")
            print(f"   Symbol: {symbol}")
            print(f"   Action: {action}")
            print(f"   Price: {price:.{digits}f}")
            print(f"   SL: {sl:.{digits}f} (distance: {abs(price - sl):.{digits}f})")
            print(f"   TP: {tp:.{digits}f} (distance: {abs(tp - price):.{digits}f})")
            print(f"   Lot: {lot_size}")

            result = mt5.order_send(request)

            if result is None:
                return {"success": False, "error": "order_send returned None"}

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                min_distance = stops_level * point
                error_msg = f"Order failed: {result.comment} (code: {result.retcode})"
                if result.retcode == mt5.TRADE_RETCODE_INVALID_STOPS:
                    error_msg += f"\\n   Hint: SL/TP too close. Min distance: {min_distance:.{digits}f}"
                elif result.retcode == mt5.TRADE_RETCODE_NO_MONEY:
                    error_msg += (
                        f"\\n   Hint: Insufficient funds. Check margin requirements."
                    )
                elif result.retcode == mt5.TRADE_RETCODE_INVALID_PRICE:
                    error_msg += f"\\n   Hint: Price changed. Try again."
                return {"success": False, "error": error_msg}

            return {
                "success": True,
                "ticket": result.order,
                "price": price,
                "sl": sl,
                "tp": tp,
                "volume": lot_size,
            }

        except Exception as e:
            import traceback

            return {"success": False, "error": f"{str(e)}\\n{traceback.format_exc()}"}

    def manage_open_positions(self) -> None:
        """Manage all open positions - AUTO CLOSE, BEP, TRAILING"""
        try:
            positions = mt5.positions_get()
            if not positions:
                return

            for position in positions:
                if position.magic != 234000:
                    continue

                # 1. AUTO-CLOSE PROFIT
                if self.config["current"]["auto_close_profit"]:
                    target = self.config["current"]["auto_close_target"]
                    if position.profit >= target:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        print(f"\\n[{timestamp}] 💰 AUTO-CLOSE PROFIT TARGET HIT!")
                        print(f"   {position.symbol} Ticket #{position.ticket}")
                        print(
                            f"   Profit: ${position.profit:.2f} (Target: ${target:.2f})"
                        )
                        if close_position(
                            position.ticket, self.config["current"]["slippage"]
                        ):
                            print(f"   ✅ Position closed successfully!")
                        else:
                            print(f"   ❌ Failed to close position")
                        continue

                # 2. BREAKEVEN
                if self.config["current"]["bep"]:
                    self._check_breakeven(position)

                # 3. TRAILING STOP
                if self.config["current"]["stpp_trailing"]:
                    self._update_trailing_stop(position)

        except Exception as e:
            print(f"Error managing positions: {e}")

    def _check_breakeven(self, position) -> None:
        try:
            min_profit = self.config["current"]["bep_min_profit"]
            if position.profit < min_profit:
                return

            symbol_info = mt5.symbol_info(position.symbol)
            spread = symbol_info.ask - symbol_info.bid

            if position.type == 0:  # BUY
                bep_level = position.price_open + spread
                if position.sl < bep_level:
                    print(
                        f"🔒 Moving to BEP: {position.symbol} @ {bep_level:.{symbol_info.digits}f}"
                    )
                    modify_position(position.ticket, new_sl=bep_level)
            else:  # SELL
                bep_level = position.price_open - spread
                if position.sl > bep_level or position.sl == 0:
                    print(
                        f"🔒 Moving to BEP: {position.symbol} @ {bep_level:.{symbol_info.digits}f}"
                    )
                    modify_position(position.ticket, new_sl=bep_level)
        except Exception as e:
            print(f"BEP error: {e}")

    def _update_trailing_stop(self, position) -> None:
        try:
            step_init = self.config["current"]["step_lock_init"]
            step_size = self.config["current"]["step_step"]

            if position.profit < step_init:
                return

            symbol_info = mt5.symbol_info(position.symbol)
            point = symbol_info.point
            steps_passed = int((position.profit - step_init) / step_size)

            if steps_passed < 1:
                return

            new_sl_distance = step_init + (steps_passed * step_size)

            if "XAU" in position.symbol or "GOLD" in position.symbol:
                price_distance = new_sl_distance
            else:
                price_distance = new_sl_distance * point * 10

            if position.type == 0:  # BUY
                new_sl = position.price_open + price_distance
                if new_sl > position.sl:
                    print(
                        f"📈 Trailing SL: {position.symbol} @ {new_sl:.{symbol_info.digits}f}"
                    )
                    modify_position(position.ticket, new_sl=new_sl)
            else:  # SELL
                new_sl = position.price_open - price_distance
                if new_sl < position.sl or position.sl == 0:
                    print(
                        f"📉 Trailing SL: {position.symbol} @ {new_sl:.{symbol_info.digits}f}"
                    )
                    modify_position(position.ticket, new_sl=new_sl)
        except Exception as e:
            print(f"Trailing stop error: {e}")
