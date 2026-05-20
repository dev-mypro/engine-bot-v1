import pandas as pd
from typing import Dict
from analyzers.indicators import (
    calculate_rsi,
    calculate_macd,
    calculate_stochastic,
    calculate_atr,
    calculate_atr_value,
    calculate_bollinger_bands,
)
from analyzers.patterns import (
    detect_candlestick_patterns,
    detect_breakouts,
    find_support_resistance,
)
from analyzers.sentiment import analyze_news_simple, get_economic_calendar_light
import MetaTrader5 as mt5


class MarketAnalyzer:
    def __init__(self, news_api_key: str = None, te_key: str = None):
        self.news_api_key = news_api_key
        self.te_key = te_key

    def analyze_market(
        self,
        df: pd.DataFrame,
        symbol: str,
        config: dict = None,
        ai_bias: str = "NEUTRAL",
    ) -> Dict:
        """Comprehensive market analysis with trade_mode filter"""
        if config is None:
            config = {
                "current": {
                    "trade_mode": "AGGRESSIVE",
                    "enable_scalping": True,
                    "enable_pattern_trading": True,
                    "enable_breakout_trading": True,
                    "ignore_economic_calendar": False,
                    "signal_threshold": "LOW",
                    "min_signal_strength": 0.1,
                }
            }

        trade_mode = config["current"].get("trade_mode", "AGGRESSIVE").upper()

        analysis = {
            "technical": self._analyze_technical(df),
            "patterns": detect_candlestick_patterns(df),
            "breakout": detect_breakouts(df),
            "support_resistance": find_support_resistance(df),
            "scalping": self._scalping_signals(df),
            "news": analyze_news_simple(symbol),
            "calendar": get_economic_calendar_light(config),
            "overall": {"signal": "WAIT", "strength": 0, "reasons": []},
        }

        analysis["overall"] = self._combine_signals_aggressive(
            analysis, config, ai_bias=ai_bias
        )

        return analysis

    def _analyze_technical(self, df: pd.DataFrame) -> Dict:
        """Fast technical analysis for aggressive trading"""
        if df.empty or len(df) < 50:
            return {"signal": "WAIT", "signals": [], "bullish": 0, "bearish": 0}

        df = df.copy()
        df["SMA_10"] = df["close"].rolling(window=10).mean()
        df["SMA_20"] = df["close"].rolling(window=20).mean()
        df["SMA_50"] = df["close"].rolling(window=50).mean()
        df["EMA_9"] = df["close"].ewm(span=9).mean()
        df["RSI"] = calculate_rsi(df["close"], period=14)
        df["MACD"], df["Signal"], _ = calculate_macd(df["close"])
        df["Stoch_K"], df["Stoch_D"] = calculate_stochastic(df, period=5)

        signals = []
        bullish = 0
        bearish = 0

        last_close = df["close"].iloc[-1]
        last_sma10 = df["SMA_10"].iloc[-1]
        last_sma20 = df["SMA_20"].iloc[-1]
        last_rsi = df["RSI"].iloc[-1]
        last_macd = df["MACD"].iloc[-1]
        last_signal = df["Signal"].iloc[-1]
        last_stoch = df["Stoch_K"].iloc[-1]

        if last_sma10 > last_sma20:
            signals.append("EMA Cross UP")
            bullish += 1
        else:
            signals.append("EMA Cross DOWN")
            bearish += 1

        if last_close > last_sma10:
            bullish += 1
        else:
            bearish += 1

        if last_rsi < 40:
            signals.append(f"RSI Low ({last_rsi:.0f})")
            bullish += 2
        elif last_rsi > 60:
            signals.append(f"RSI High ({last_rsi:.0f})")
            bearish += 2

        if last_macd > last_signal:
            signals.append("MACD Bullish")
            bullish += 1
        else:
            signals.append("MACD Bearish")
            bearish += 1

        if last_stoch < 30:
            signals.append(f"Stoch Oversold")
            bullish += 2
        elif last_stoch > 70:
            signals.append(f"Stoch Overbought")
            bearish += 2

        momentum_3 = (last_close / df["close"].iloc[-4] - 1) * 100
        if momentum_3 > 0.1:
            signals.append(f"Momentum UP ({momentum_3:+.2f}%)")
            bullish += 1
        elif momentum_3 < -0.1:
            signals.append(f"Momentum DOWN ({momentum_3:+.2f}%)")
            bearish += 1

        if bullish > bearish:
            signal = "BUY"
        elif bearish > bullish:
            signal = "SELL"
        else:
            signal = "WAIT"

        return {
            "signal": signal,
            "signals": signals,
            "bullish": bullish,
            "bearish": bearish,
            "confidence": abs(bullish - bearish) / max(bullish + bearish, 1),
        }

    def _scalping_signals(self, df: pd.DataFrame) -> Dict:
        """SUPER-STRICT v4 SCALPING: Maximum accuracy with 3-candle momentum + price action"""
        if len(df) < 50:
            return {"signal": "WAIT", "signals": [], "score": 0, "strength": 0}

        df = df.copy()
        signals = []
        score = 0
        confirmation_count = 0

        df["RSI"] = calculate_rsi(df["close"], period=14)
        df["RSI_5"] = calculate_rsi(df["close"], period=5)
        df["MACD"], df["Signal"], df["Histogram"] = calculate_macd(df["close"])
        df["EMA_5"] = df["close"].ewm(span=5).mean()
        df["EMA_9"] = df["close"].ewm(span=9).mean()
        df["EMA_21"] = df["close"].ewm(span=21).mean()
        df["ATR"] = calculate_atr(df)
        df["BB_Upper"], df["BB_Middle"], df["BB_Lower"] = calculate_bollinger_bands(
            df, period=20, std_dev=2
        )

        last_close = df["close"].iloc[-1]
        last_open = df["open"].iloc[-1]
        last_high = df["high"].iloc[-1]
        last_low = df["low"].iloc[-1]

        prev_close = df["close"].iloc[-2]
        prev_open = df["open"].iloc[-2]
        prev_low = df["low"].iloc[-2]
        prev_high = df["high"].iloc[-2]

        prev2_close = df["close"].iloc[-3]
        prev2_open = df["open"].iloc[-3]
        prev2_low = df["low"].iloc[-3]
        prev2_high = df["high"].iloc[-3]

        last_rsi = df["RSI"].iloc[-1]
        last_macd = df["MACD"].iloc[-1]
        last_signal_line = df["Signal"].iloc[-1]
        last_histogram = df["Histogram"].iloc[-1]

        last_ema5 = df["EMA_5"].iloc[-1]
        last_ema9 = df["EMA_9"].iloc[-1]
        last_ema21 = df["EMA_21"].iloc[-1]

        atr = df["ATR"].iloc[-1]
        last_bb_upper = df["BB_Upper"].iloc[-1]
        last_bb_lower = df["BB_Lower"].iloc[-1]

        avg_atr = df["ATR"].tail(20).mean()
        if atr < avg_atr * 0.70:
            return {
                "signal": "WAIT",
                "signals": ["❌ Volatility too low"],
                "score": 0,
                "strength": 0,
            }
        confirmation_count += 1
        signals.append("✅ High volatility")

        trend_confirmed = False
        trend_direction = None
        if last_ema5 > last_ema9 > last_ema21:
            trend_confirmed = True
            trend_direction = "UP"
        elif last_ema5 < last_ema9 < last_ema21:
            trend_confirmed = True
            trend_direction = "DOWN"

        if not trend_confirmed:
            return {
                "signal": "WAIT",
                "signals": ["❌ EMA not aligned"],
                "score": 0,
                "strength": 0,
            }

        confirmation_count += 1
        signals.append(f"✅ Trend {trend_direction}")

        momentum_valid = False
        if trend_direction == "UP":
            candle_1_bullish = last_close > last_open
            candle_2_bullish = prev_close > prev_open
            candle_3_bullish = prev2_close > prev2_open
            body_1 = abs(last_close - last_open)
            body_2 = abs(prev_close - prev_open)
            strength_increasing = body_1 >= body_2 * 0.8
            momentum_valid = (
                candle_1_bullish
                and candle_2_bullish
                and candle_3_bullish
                and strength_increasing
            )
            if momentum_valid:
                signals.append(f"✅ 3-candle bullish momentum")
        else:
            candle_1_bearish = last_close < last_open
            candle_2_bearish = prev_close < prev_open
            candle_3_bearish = prev2_close < prev2_open
            body_1 = abs(last_close - last_open)
            body_2 = abs(prev_close - prev_open)
            strength_maintaining = body_1 >= body_2 * 0.8
            momentum_valid = (
                candle_1_bearish
                and candle_2_bearish
                and candle_3_bearish
                and strength_maintaining
            )
            if momentum_valid:
                signals.append(f"✅ 3-candle bearish momentum")

        if not momentum_valid:
            return {
                "signal": "WAIT",
                "signals": ["❌ Weak momentum (not 3 confirmed)"],
                "score": 0,
                "strength": 0,
            }
        confirmation_count += 1

        price_action_valid = False
        if trend_direction == "UP":
            price_action_valid = (last_low > prev_low) and (prev_low > prev2_low)
            if price_action_valid:
                signals.append("✅ Higher lows confirmed")
        else:
            price_action_valid = (last_high < prev_high) and (prev_high < prev2_high)
            if price_action_valid:
                signals.append("✅ Lower highs confirmed")

        if not price_action_valid:
            return {
                "signal": "WAIT",
                "signals": ["❌ Price action broken"],
                "score": 0,
                "strength": 0,
            }
        confirmation_count += 1

        pullback_valid = False
        if trend_direction == "UP":
            pullback_valid = (
                prev_close > last_ema9
                and last_close < last_ema9
                and last_close > last_ema21
            )
        else:
            pullback_valid = (
                prev_close < last_ema9
                and last_close > last_ema9
                and last_close < last_ema21
            )

        if pullback_valid:
            signals.append("✅ Pullback to EMA9")
        else:
            return {
                "signal": "WAIT",
                "signals": ["❌ No EMA9 pullback"],
                "score": 0,
                "strength": 0,
            }
        confirmation_count += 1

        rsi_valid = False
        if trend_direction == "UP":
            rsi_valid = 25 <= last_rsi <= 55
        else:
            rsi_valid = 45 <= last_rsi <= 75

        if rsi_valid:
            signals.append(f"✅ RSI valid ({last_rsi:.0f})")
        else:
            return {
                "signal": "WAIT",
                "signals": [f"❌ RSI invalid ({last_rsi:.0f})"],
                "score": 0,
                "strength": 0,
            }
        confirmation_count += 1

        macd_valid = False
        if trend_direction == "UP":
            macd_valid = last_histogram > 0 and last_macd > last_signal_line
        else:
            macd_valid = last_histogram < 0 and last_macd < last_signal_line

        if macd_valid:
            signals.append("✅ MACD valid")
        else:
            return {
                "signal": "WAIT",
                "signals": ["❌ MACD misaligned"],
                "score": 0,
                "strength": 0,
            }
        confirmation_count += 1

        bb_valid = last_close > last_bb_lower and last_close < last_bb_upper
        if bb_valid:
            signals.append("✅ Price in BB range")
            confirmation_count += 1

        current_volume = df["tick_volume"].iloc[-1]
        avg_volume = df["tick_volume"].tail(20).mean()
        if current_volume >= avg_volume * 1.0:
            signals.append(f"✅ Volume surge ({current_volume:.0f})")
            confirmation_count += 1

        required_confirmations = 7
        if confirmation_count >= required_confirmations:
            signal = "BUY" if trend_direction == "UP" else "SELL"
            score = 1 if signal == "BUY" else -1
            strength = min(confirmation_count / 9, 1.0)
            signals.append(f"\\n🎯 SIGNAL VALID: {confirmation_count}/9 ✓")
        else:
            signal = "WAIT"
            score = 0
            strength = 0
            signals.append(f"\\n❌ Only {confirmation_count}/9 - INSUFFICIENT")

        return {
            "signal": signal,
            "signals": signals,
            "score": score,
            "strength": strength,
            "confirmations": confirmation_count,
            "trend": trend_direction,
        }

    def _combine_signals_aggressive(
        self, analysis: Dict, config: dict, ai_bias: str = "NEUTRAL"
    ) -> Dict:
        reasons = []
        strength = 0.0

        tech = analysis.get("technical", {})
        patterns = analysis.get("patterns", {})
        breakout = analysis.get("breakout", {})
        sr = analysis.get("support_resistance", {})
        scalp = analysis.get("scalping", {})

        scalp_confirmations = scalp.get("confirmations", 0)

        if scalp.get("signal") in ["BUY", "SELL"] and scalp_confirmations >= 5:
            master_direction = scalp["signal"]
            base_strength = min(scalp_confirmations / 7, 1.0)
            reasons.append(
                f"🎯 SCALPING SIGNAL: {master_direction} ({scalp_confirmations}/7 confirmations)"
            )
            reasons.append(f"Trend: {scalp.get('trend', '?').upper()}")
            strength = base_strength
        elif scalp.get("signal") in ["BUY", "SELL"] and scalp_confirmations >= 4:
            master_direction = scalp["signal"]
            strength = 0.65
            reasons.append(
                f"⚠️ Scalping signal: {scalp_confirmations}/7 confirmations (acceptable)"
            )
        else:
            master_direction = "WAIT"
            if tech.get("signal") in ["BUY", "SELL"]:
                master_direction = tech["signal"]
                strength = 0.5
                reasons.append(f"📊 Technical signal: {master_direction}")

            if master_direction == "WAIT":
                return {
                    "signal": "WAIT",
                    "strength": 0.0,
                    "reasons": ["⏸️ No high-quality signals"],
                    "raw_strength": 0,
                }

        if scalp_confirmations < 4:
            if master_direction == "BUY":
                reasons.append("🌊 Master Trend: BULLISH")
                if tech.get("signal") == "BUY":
                    strength += 0.35
                    reasons.append("✅ Teknikal Searah")
                if patterns.get("signal") == "BUY":
                    strength += 0.25
                    reasons.append("✅ Pola Candle Mendukung")
                if sr.get("signal") == "BUY":
                    strength += 0.20
                    reasons.append("✅ Memantul dari Support")
                if breakout.get("signal") == "BUY":
                    strength += 0.20
                    reasons.append("✅ Momentum Breakout UP")
            elif master_direction == "SELL":
                reasons.append("🌊 Master Trend: BEARISH")
                if tech.get("signal") == "SELL":
                    strength += 0.35
                    reasons.append("🔻 Teknikal Searah")
                if patterns.get("signal") == "SELL":
                    strength += 0.25
                    reasons.append("🔻 Pola Candle Mendukung")
                if sr.get("signal") == "SELL":
                    strength += 0.20
                    reasons.append("🔻 Terpantul dari Resistance")
                if breakout.get("signal") == "SELL":
                    strength += 0.20
                    reasons.append("🔻 Momentum Breakout DOWN")

        if ai_bias != "NEUTRAL":
            if ai_bias == master_direction:
                strength += 0.15
                reasons.append(f"🤖 Gemini AI Setuju: {ai_bias}")
            else:
                strength -= 0.30
                reasons.append(f"⚠️ Gemini AI Berlawanan: Membaca {ai_bias}")

        abs_strength = min(abs(strength), 1.0)
        min_threshold = max(
            config.get("current", {}).get("min_signal_strength", 0.60), 0.60
        )

        if abs_strength >= min_threshold:
            signal = master_direction
            reasons.append(
                f"🚀 EKSEKUSI VALID ({abs_strength:.0%} >= {min_threshold:.0%})"
            )
        else:
            signal = "WAIT"
            reasons.append(
                f"⏸️ Batal: Syarat konfirmasi kurang ({abs_strength:.0%} < {min_threshold:.0%})"
            )

        return {
            "signal": signal,
            "strength": abs_strength,
            "reasons": reasons,
            "raw_strength": strength if master_direction == "BUY" else -strength,
        }
