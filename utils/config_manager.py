import os
import json
from dotenv import load_dotenv


_gemini_key_logged = False


def load_environment():
    """
    Load .env and return a dict with multiple key formats to avoid
    mismatches between UPPER and snake_case usages in the code.
    """
    global _gemini_key_logged
    load_dotenv()  # load .env into os.environ

    # Basic presence debug (masked) - will not print the full key
    if not _gemini_key_logged:
        raw_key = os.getenv("GEMINI_API_KEY") or os.getenv("gemini_api_key")
        if raw_key:
            masked = raw_key[:4] + "..." + raw_key[-4:] if len(raw_key) > 8 else "****"
            print(f"\n✅ GEMINI_API_KEY found in environment (masked): {masked}")
        else:
            print("\n⚠️ GEMINI_API_KEY not found in environment variables")
        _gemini_key_logged = True

    env = {
        # Legacy / Generic Credentials
        "MT5_LOGIN": os.getenv("MT5_LOGIN"),
        "MT5_PASSWORD": os.getenv("MT5_PASSWORD"),
        "MT5_SERVER": os.getenv("MT5_SERVER"),
        
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "NEWS_API_KEY": os.getenv("NEWS_API_KEY"),
        "TRADING_ECONOMICS_KEY": os.getenv("TRADING_ECONOMICS_KEY", "guest:guest"),

        # snake_case keys for legacy compatibility
        "mt5_login": int(os.getenv("MT5_LOGIN")) if os.getenv("MT5_LOGIN") and os.getenv("MT5_LOGIN").isdigit() else 0,
        "mt5_password": os.getenv("MT5_PASSWORD", ""),
        "mt5_server": os.getenv("MT5_SERVER", ""),
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "news_api_key": os.getenv("NEWS_API_KEY", ""),
        "trading_economics_key": os.getenv("TRADING_ECONOMICS_KEY", "guest:guest"),
    }
    
    # Dynamically inject all keys starting with MT5_ from os.environ
    for key, val in os.environ.items():
        if key.startswith("MT5_"):
            env[key] = val
            env[key.lower()] = val
            
    return env


def load_config(config_path: str = "config.json") -> dict:
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            
        # Dynamically auto-detect account providers defined in .env
        providers = []
        load_dotenv()
        for key in os.environ.keys():
            if key.startswith("MT5_") and key.endswith("_LOGIN") and key != "MT5_LOGIN":
                provider = key[4:-6].upper()
                if provider not in providers:
                    providers.append(provider)
                    
        if not providers:
            providers = ["DEMO", "FINEX"]
            
        if "options" in config:
            config["options"]["accounts"] = sorted(list(set(providers)))
            
            # If current active account is not in the detected providers, set it to the first one
            if "current" in config and config["current"].get("account") not in config["options"]["accounts"]:
                config["current"]["account"] = config["options"]["accounts"][0]
                save_config(config, config_path)
                
        return config
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
