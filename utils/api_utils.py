import requests
from google import genai
from google.genai.errors import APIError
from google.genai.types import GenerationConfig


def init_gemini(env: dict) -> genai.Client:
    """Initialize Gemini API with the latest model"""
    api_key = env.get("GEMINI_API_KEY") or env.get("gemini_api_key")

    if not api_key or api_key == "":
        print("\n⚠️ GEMINI_API_KEY tidak ditemukan di .env!")
        return None

    try:
        # 1. Initialize Gemini with the API Key
        client = genai.Client(
            api_key=api_key
        )  # Pass key to Client for a modern approach

        # 2. Test connection (by using a model on the client)
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Specify the model here
            contents="test connection",
        )

        if response.text:  # Check if the content was generated successfully
            print("\n✅ Gemini AI siap digunakan!")
            return client  # Return the client instance

    except Exception as e:
        print(f"\n❌ Gagal inisialisasi Gemini: {e}")
        print("ℹ️ Bot akan berjalan tanpa analisis AI")
        print("💡 Pastikan:")
        print("1. API key valid dan aktif")
        print("2. Package google-genai terinstall versi terbaru")
        print("3. Koneksi internet stabil")
    return None


def fetch_latest_news(api_key, symbol):
    """Fetch latest news relevant to the symbol (e.g., Gold/XAUUSD)"""
    if not api_key:
        return "No News API Key available."

    # Example URL to search for news about 'Gold' or 'USD'
    url = f"https://newsapi.org/v2/everything?q={symbol}&sortBy=publishedAt&apiKey={api_key}&pageSize=5"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data["status"] == "ok" and data["articles"]:
            # Combine title and description of several articles into a single string for Gemini analysis
            combined_text = "\n".join(
                [f"- {a['title']}: {a['description']}" for a in data["articles"]]
            )
            return combined_text
        else:
            return f"No relevant news found for {symbol} today."

    except requests.RequestException as e:
        return f"News API Request Failed: {e}"
