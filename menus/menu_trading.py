import os
import requests
import MetaTrader5 as mt5
import pandas as pd
from google import genai
from google.genai.errors import APIError
from google.genai.types import GenerationConfig
from analyzers.market_analyzer import MarketAnalyzer
from trading.trade_manager import TradeManager
from bot.bot_manager import TradingBot
from utils.mt5_utils import ambil_candle
from utils.config_manager import load_environment

env = load_environment()

def analyze_with_gemini_advanced(client: genai.Client, analysis: dict, df: pd.DataFrame, symbol: str) -> dict:
    """
    Advanced Gemini AI analysis with structured output
    """
    if not client:
        return {"recommendation": "WAIT", "confidence": 0, "reason": "Gemini not available"}

    # Prepare comprehensive data for AI
    last_close = df['close'].iloc[-1]
    price_change_5 = ((df['close'].iloc[-1] / df['close'].iloc[-5]) - 1) * 100 if len(df) >= 5 else 0
    price_change_20 = ((df['close'].iloc[-1] / df['close'].iloc[-20]) - 1) * 100 if len(df) >= 20 else 0
    
    # Get technical summary
    tech = analysis['technical']
    news = analysis['news']
    calendar = analysis['calendar']
    
    high = df['high'].tail(10).max()
    low = df['low'].tail(10).min()
    
    # Construct detailed prompt
    system_prompt = """You are an expert Forex/Crypto trading AI analyst. 
    Analyze the provided market data and give a trading recommendation in JSON format.
    
    You MUST respond in this exact JSON format:
    {
      "recommendation": "BUY" or "SELL" or "WAIT",
      "confidence": 0-100,
      "entry_price": suggested entry price,
      "stop_loss": suggested SL price,
      "take_profit": suggested TP price,
      "risk_reward_ratio": calculated R:R,
      "key_factors": [list of 3-5 key factors influencing decision],
      "warnings": [list of risks or concerns],
      "timeframe": "short-term" or "medium-term" or "long-term"
    }
    
    Base your analysis on:
    1. Technical indicators and trends
    2. News sentiment
    3. Economic calendar events
    4. Risk management principles
    5. Current market conditions
    """
    
    market_data = f"""
=== MARKET ANALYSIS FOR {symbol} ===

PRICE DATA:
- Current Price: {last_close:.5f}
- 5-bar Change: {price_change_5:+.2f}%
- 20-bar Change: {price_change_20:+.2f}%
- 10-bar High: {high:.5f}
- 10-bar Low: {low:.5f}

TECHNICAL ANALYSIS:
- Signal: {tech['signal']}
- Bullish Signals: {tech['bullish']}
- Bearish Signals: {tech['bearish']}
- Confidence: {tech.get('confidence', 0):.1%}
- Key Indicators:
{chr(10).join(['  • ' + s for s in tech['signals'][:5]])}

NEWS SENTIMENT:
- Impact: {news['impact']}
- Sentiment Score: {news.get('sentiment_score', 0)}
- Recent Headlines:
{chr(10).join(['  • ' + h[:80] for h in news.get('headlines', [])[:3]])}

ECONOMIC CALENDAR:
- Impact Level: {calendar['impact']}
- High Impact Events: {calendar.get('high_impact_count', 0)}
- Upcoming Events:
{chr(10).join(['  • ' + e for e in calendar.get('events', [])[:3]])}

OVERALL ANALYSIS:
- Combined Signal: {analysis['overall']['signal']}
- Signal Strength: {analysis['overall']['strength']:.1%}
- Key Reasons:
{chr(10).join(['  • ' + r for r in analysis['overall']['reasons'][:5]])}

=== TASK ===
Based on this comprehensive analysis, provide your expert trading recommendation.
Consider risk management, current volatility, and all factors above.
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=market_data,
            config={
                "system_instruction": system_prompt,
                "response_mime_type": "application/json",
                "temperature": 0.3,  # Lower temperature for more consistent output
            }
        )
        # Parse JSON response
        import json
        ai_analysis = json.loads(response.text)
        
        # Validate response
        required_keys = ['recommendation', 'confidence', 'key_factors']
        if all(key in ai_analysis for key in required_keys):
            return ai_analysis
        else:
            print("⚠️ AI response missing required fields")
            return {"recommendation": "WAIT", "confidence": 0, "reason": "Invalid AI response"}
            
    except json.JSONDecodeError as e:
        print(f"❌ AI JSON decode error: {e}")
        print(f"Raw response: {response.text[:200] if response.text else 'Empty response'}")
        return {"recommendation": "WAIT", "confidence": 0, "reason": "JSON decode failed"}
    except Exception as e:
        print(f"❌ Gemini AI Error: {e}")
        return {"recommendation": "WAIT", "confidence": 0, "reason": str(e)}


def menu_1_analyze_now(config: dict, gemini_client: genai.Client = None) -> None:
    print(f"\n🔍 Analyzing {config['current']['symbol']} ({config['current']['timeframe']})...")
    print(f"Mode: {config['current']['trade_mode']} | Threshold: {config['current'].get('min_signal_strength', 0.2):.0%}")
    
    df = ambil_candle(
        symbol=config["current"]["symbol"],
        timeframe=config["current"]["timeframe"],
        jumlah=config["current"]["candles"]
    )
    if df.empty: 
        print("❌ Cannot get candle data")
        return
    
    analyzer = MarketAnalyzer(
        news_api_key=env.get('news_api_key'),
        te_key=env.get('trading_economics_key')
    )
    
    analysis = analyzer.analyze_market(df, config['current']['symbol'], config)
    
    print("\n" + "="*80)
    print(f"📊 MARKET ANALYSIS - {config['current']['trade_mode']} MODE")
    print("="*80)
    
    print("\n🔧 TECHNICAL:")
    tech = analysis.get('technical', {})
    print(f"Signal: {tech.get('signal')} | Bullish: {tech.get('bullish')} | Bearish: {tech.get('bearish')}")
    for sig in tech.get('signals', [])[:5]:
        print(f"  • {sig}")
    
    if analysis.get('patterns', {}).get('count', 0) > 0:
        print("\n📊 CANDLESTICK PATTERNS:")
        for pattern in analysis['patterns']['patterns']:
            print(f"  🔥 {pattern}")
    
    if analysis.get('breakout', {}).get('count', 0) > 0:
        print("\n💥 BREAKOUTS:")
        for bo in analysis['breakout']['breakouts']:
            print(f"  🚀 {bo}")
    
    if config['current'].get('enable_scalping', True):
        scalp = analysis.get('scalping', {})
        if scalp.get('score', 0) != 0:
            print(f"\n⚡ SCALPING: Score {scalp['score']}")
            for sig in scalp.get('signals', []):
                print(f"  • {sig}")
                
    # AI Analysis (Optional - fast version)
    if gemini_client and config['current']['trade_mode'] != 'SCALPING':
        print("\n🤖 AI QUICK ANALYSIS:")
        try:
            quick_prompt = f"""
Analyze {config['current']['symbol']}:
- Technical: {tech.get('signal')} ({tech.get('bullish')} bull, {tech.get('bearish')} bear)
- Patterns: {analysis.get('patterns', {}).get('patterns', [])}
- Price: {df['close'].iloc[-1]:.5f}

Give ONE sentence: BUY/SELL/WAIT and why.
"""
            response = gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=quick_prompt
            )
            if response.text:
                print(f"  {response.text.strip()}")
        except Exception as e:
            print(f"  ⚠️ AI analysis error: {e}")
    
    print("\n🎯 FINAL DECISION:")
    overall = analysis.get('overall', {})
    print(f"Signal: {overall.get('signal')} | Strength: {overall.get('strength', 0):.1%}")
    for reason in overall.get('reasons', [])[:5]:
        print(f"  {reason}")
    
    symbol_info = mt5.symbol_info(config['current']['symbol'])
    if symbol_info:
        print(f"\n💱 Market: Bid {symbol_info.bid:.5f} | Ask {symbol_info.ask:.5f}")
    
    print("="*80)

def menu_7_launch_trainer(config: dict) -> None:
    print("\n📚 Launching Trainer Mode...")
    try:
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        import matplotlib.dates as mdates
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8))
        fig.suptitle(f"Trading Trainer - {config['current']['symbol']} ({config['current']['timeframe']})")
        
        def update_chart(frame):
            df = ambil_candle(config["current"]["symbol"], config["current"]["timeframe"], config["current"]["candles"])
            if df.empty: return
            
            ax1.clear()
            ax2.clear()
            ax3.clear()
            
            ax1.plot(df['time'], df['close'], label='Close', color='blue', linewidth=1)
            df['SMA_20'] = df['close'].rolling(window=20).mean()
            df['SMA_50'] = df['close'].rolling(window=50).mean()
            ax1.plot(df['time'], df['SMA_20'], label='SMA 20', color='orange', alpha=0.7)
            ax1.plot(df['time'], df['SMA_50'], label='SMA 50', color='red', alpha=0.7)
            ax1.set_title('Price Action & Moving Averages')
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            
            colors = ['g' if df['close'].iloc[i] > df['open'].iloc[i] else 'r' for i in range(len(df))]
            ax2.bar(df['time'], df['tick_volume'], color=colors, alpha=0.5)
            ax2.set_title('Volume')
            ax2.grid(True, alpha=0.3)
            
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            ax3.plot(df['time'], df['RSI'], label='RSI', color='purple')
            ax3.axhline(y=70, color='r', linestyle='--', alpha=0.5)
            ax3.axhline(y=30, color='g', linestyle='--', alpha=0.5)
            ax3.fill_between(df['time'], 30, 70, alpha=0.1)
            ax3.set_title('RSI (14)')
            ax3.set_ylim(0, 100)
            ax3.legend(loc='upper left')
            ax3.grid(True, alpha=0.3)
            
            last_price = df['close'].iloc[-1]
            ax1.annotate(f'${last_price:.2f}', xy=(df['time'].iloc[-1], last_price), xytext=(10, 10), textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5), arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
            plt.tight_layout()
        
        ani = FuncAnimation(fig, update_chart, interval=10000, cache_frame_data=False)
        plt.show()
    except ImportError:
        print("❌ Matplotlib tidak terinstall. Install dengan: pip install matplotlib")
        print("\n💡 Alternatif: Gunakan menu 1 (Analyze Now) untuk analisis manual")
    except Exception as e:
        print(f"❌ Error: {e}")

def menu_99_start_trading(config: dict, gemini_client: genai.Client = None) -> None:
    defaults = {
        'min_signal_strength': 0.1,
        'enable_scalping': True,
        'enable_pattern_trading': True,
        'enable_breakout_trading': True,
        'max_daily_trades': 50,
        'ignore_economic_calendar': False
    }
    for key, default_value in defaults.items():
        if key not in config['current']:
            config['current'][key] = default_value
    
    print("\n🚀 Starting Auto Trading...")
    print(f"Symbol: {config['current']['symbol']}")
    print(f"Timeframe: {config['current']['timeframe']}")
    print(f"Mode: {config['current']['trade_mode']}")
    print(f"Lot: {config['current']['lot']}")
    print(f"Min Signal: {config['current']['min_signal_strength']:.1%}")
    print(f"Max Daily Trades: {config['current']['max_daily_trades']}")
    print(f"Check Interval: {config['current']['auto_analyze_interval']} min")
    
    try:
        analyzer = MarketAnalyzer(
            news_api_key=env.get('news_api_key'),
            te_key=env.get('trading_economics_key')
        )
        trader = TradeManager(config)
        bot = TradingBot(config, analyzer, trader, gemini_client)
        
        print("\n✅ All systems ready!")
        print("⚠️ Trading active")
        print("\nPress Ctrl+C to stop\n")
        bot.start()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
