import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from bot.signal_executor import analyze_symbol_timeframe, execute_signal


class CycleRunner:
    def __init__(self, bot):
        self.bot = bot

    def run_rapid_fire_cycle(self) -> None:
        """Rapid fire mode - CHECK LIMITS FIRST"""
        try:
            self.bot.trader.manage_open_positions()

            current_positions = self.bot.tracker.get_current_positions()
            total_open = len(current_positions)

            if total_open >= self.bot.tracker.max_total_positions:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(
                    f"[{timestamp}] ⚠️ MAX POSITIONS REACHED ({total_open}/{self.bot.tracker.max_total_positions}) - Waiting for close..."
                )

                if total_open > 0:
                    total_profit = sum(p.profit for p in current_positions)
                    print(
                        f"           Open P/L: ${total_profit:+.2f} | Target: ${self.bot.config['current']['auto_close_target']:.2f}"
                    )

                    for p in current_positions[:3]:
                        print(
                            f"           {p.symbol} {p.type} | Profit: ${p.profit:+.2f}"
                        )

                    if total_open > 3:
                        print(f"           ... and {total_open - 3} more")
                return

            if self.bot.tracker.trades_today >= self.bot.tracker.max_daily_trades:
                print(
                    f"⚠️ Daily limit reached ({self.bot.tracker.trades_today}/{self.bot.tracker.max_daily_trades})"
                )
                return

            symbols = (
                self.bot.symbols_to_trade
                if self.bot.enable_multi_symbol
                else [self.bot.config["current"]["symbol"]]
            )
            remaining_slots = self.bot.tracker.max_total_positions - total_open

            if remaining_slots <= 0:
                return

            timestamp = datetime.now().strftime("%H:%M:%S")
            print(
                f"[{timestamp}] Analyzing {len(symbols)} symbols | Positions: {total_open}/{self.bot.tracker.max_total_positions} | Slots: {remaining_slots}"
            )

            signals = []

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {}

                for symbol in symbols:
                    symbol_positions = len(
                        [p for p in current_positions if p.symbol == symbol]
                    )
                    if symbol_positions >= self.bot.tracker.max_positions_per_symbol:
                        continue

                    if self.bot.enable_multi_timeframe:
                        for tf in self.bot.timeframes_to_check:
                            future = executor.submit(
                                analyze_symbol_timeframe,
                                symbol,
                                tf,
                                self.bot.analyzer,
                                self.bot.config,
                                self.bot._get_market_data_for,
                            )
                            futures[future] = (symbol, tf)
                    else:
                        tf = self.bot.config["current"]["timeframe"]
                        future = executor.submit(
                            analyze_symbol_timeframe,
                            symbol,
                            tf,
                            self.bot.analyzer,
                            self.bot.config,
                            self.bot._get_market_data_for,
                        )
                        futures[future] = (symbol, tf)

                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result and result["signal"] != "WAIT":
                            signals.append(result)
                    except Exception:
                        pass

            if len(signals) > 0:
                print(f"   Found {len(signals)} signals")

            if signals and remaining_slots > 0:
                signals.sort(key=lambda x: x["strength"], reverse=True)
                signals_to_execute = signals[:remaining_slots]

                print(f"   Executing top {len(signals_to_execute)} signal(s)...")

                executed = 0
                for signal in signals_to_execute:
                    if execute_signal(
                        signal,
                        self.bot.trader,
                        self.bot.tracker,
                        self.bot.config,
                        self.bot.starting_balance,
                        self.bot.dynamic_lot_sizing,
                        self.bot.risk_percent,
                    ):
                        executed += 1

                        current_total = len(self.bot.tracker.get_current_positions())
                        if current_total >= self.bot.tracker.max_total_positions:
                            print(f"\n🔴 MAX POSITIONS REACHED - Stopping new orders!")
                            break

                        if executed < len(signals_to_execute):
                            time.sleep(0.5)

                if executed > 0:
                    print(f"   ✅ Opened {executed} new position(s)")

        except Exception as e:
            print(f"❌ Rapid fire cycle error: {e}")
            import traceback

            traceback.print_exc()

    def run_cycle(self) -> None:
        """Standard trading cycle (single symbol)"""
        try:
            self.bot.trader.manage_open_positions()

            current_positions = self.bot.tracker.get_current_positions()
            total_open = len(current_positions)

            if total_open >= self.bot.tracker.max_total_positions:
                print(
                    f"⚠️ Max total positions reached ({total_open}/{self.bot.tracker.max_total_positions})"
                )
                return

            symbol_positions = len(
                [
                    p
                    for p in current_positions
                    if p.symbol == self.bot.config["current"]["symbol"]
                ]
            )

            if symbol_positions >= self.bot.tracker.max_positions_per_symbol:
                print(
                    f"⚠️ Max positions for {self.bot.config['current']['symbol']} ({symbol_positions}/{self.bot.tracker.max_positions_per_symbol})"
                )
                return

            if self.bot.tracker.trades_today >= self.bot.tracker.max_daily_trades:
                return

            df = self.bot._get_market_data()
            if df.empty:
                return

            analysis = self.bot.analyzer.analyze_market(
                df, self.bot.config["current"]["symbol"], self.bot.config
            )

            signal = analysis["overall"]["signal"]
            strength = analysis["overall"]["strength"]

            timestamp = datetime.now().strftime("%H:%M:%S")
            print(
                f"\n[{timestamp}] {signal} ({strength:.0%}) | Positions: {total_open}/{self.bot.tracker.max_total_positions}"
            )

            if self.bot._should_trade() and signal != "WAIT":
                execute_signal(
                    {
                        "symbol": self.bot.config["current"]["symbol"],
                        "timeframe": self.bot.config["current"]["timeframe"],
                        "signal": signal,
                        "strength": strength,
                        "analysis": analysis,
                    },
                    self.bot.trader,
                    self.bot.tracker,
                    self.bot.config,
                    self.bot.starting_balance,
                    self.bot.dynamic_lot_sizing,
                    self.bot.risk_percent,
                )

        except Exception as e:
            print(f"❌ Cycle error: {e}")
