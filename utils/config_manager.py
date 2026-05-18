import os
import json
from dotenv import load_dotenv

def load_environment():
    """
    Load .env and return a dict with multiple key formats to avoid
    mismatches between UPPER and snake_case usages in the code.
    """
    load_dotenv()  # load .env into os.environ

    # Basic presence debug (masked) - will not print the full key
    raw_key = os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")
    if raw_key:
        masked = raw_key[:4] + "..." + raw_key[-4:] if len(raw_key) > 8 else "****"
        print(f"\n✅ GEMINI_API_KEY found in environment (masked): {masked}")
    else:
        print("\n⚠️ GEMINI_API_KEY not found in environment variables")

    env = {
        # UPPER keys (if other parts of code expect these)
        "MT5_LOGIN": os.getenv("MT5_LOGIN"),
        "MT5_PASSWORD": os.getenv("MT5_PASSWORD"),
        "MT5_SERVER": os.getenv("MT5_SERVER"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "NEWS_API_KEY": os.getenv("NEWS_API_KEY"),
        "TRADING_ECONOMICS_KEY": os.getenv("TRADING_ECONOMICS_KEY", "guest:guest"),

        # snake_case keys (common in this project)
        "mt5_login": int(os.getenv("MT5_LOGIN")) if os.getenv("MT5_LOGIN") and os.getenv("MT5_LOGIN").isdigit() else 0,
        "mt5_password": os.getenv("MT5_PASSWORD", ""),
        "mt5_server": os.getenv("MT5_SERVER", ""),
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "news_api_key": os.getenv("NEWS_API_KEY", ""),
        "trading_economics_key": os.getenv("TRADING_ECONOMICS_KEY", "guest:guest"),
    }
    return env

def load_config(config_path: str = "config.json") -> dict:
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {config_path} tidak ditemukan!")
        return None

def save_config(config: dict, config_path: str = "config.json") -> None:
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print(f"✅ Konfigurasi disimpan ke {config_path}")
    except Exception as e:
        print(f"❌ Gagal menyimpan konfigurasi: {str(e)}")
