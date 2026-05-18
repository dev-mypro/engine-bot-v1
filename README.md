## 🤖 Bot Trading MT5 Agresif Cerdas (Python)

Bot trading ini dirancang khusus untuk **MetaTrader 5 (MT5)**, mengadopsi pendekatan **Rapid Fire** dan **Agresif** dengan berbagai strategi multi-posisi. Skrip ini menampilkan manajemen posisi dinamis, kontrol risiko canggih, dan potensi integrasi dengan **Gemini API** untuk analisis yang ditingkatkan oleh AI.

---

## 🚀 Fitur & Kemampuan Utama

Bot ini beroperasi dengan fokus pada kecepatan dan volume, sangat cocok untuk pasar yang volatil dan strategi _scalping_.

### 💰 Trading & Eksekusi

- **Mode Rapid Fire Trading:** Mode frekuensi tinggi yang dirancang untuk memeriksa banyak simbol dan _timeframe_ setiap 10 detik, bertujuan untuk mengisi batas `Max Total Positions` dengan cepat.
- **Manajemen Multi-Posisi:** Memungkinkan trading simultan di beberapa pasangan mata uang dan/atau _timeframe_.
  - `max_total_positions`: Batas global untuk _open trades_ (standar: 10).
  - `max_positions_per_symbol`: Batas untuk _trades_ pada aset tunggal (standar: 3).
- **Ukuran Lot Dinamis (Berdasarkan Risiko):** Menghitung ukuran lot untuk setiap _trade_ berdasarkan persentase tetap dari saldo akun (`risk_percent_per_trade`), memastikan manajemen risiko yang konsisten.
  - Bot mengukur risiko dengan mengestimasi jarak SL dalam USD.
- **Stop Loss (SL) & Take Profit (TP) Berbasis ATR:** Menghitung level SL/TP secara dinamis berdasarkan **Average True Range (ATR)** pasar, menyesuaikan dengan volatilitas saat ini.
  - Menggunakan pengali (1.5x ATR untuk SL, 2.0x ATR untuk TP) untuk rasio risiko/imbalan yang terhitung.
- **Manajemen Posisi Lanjutan (TradeManager):**
  - **Auto-Close Profit:** Menutup posisi segera setelah mencapai target profit tetap dalam USD (`auto_close_target`).
  - **Breakeven (BEP):** Secara otomatis memindahkan Stop Loss ke harga _entry_ (ditambah _spread_) setelah ambang profit minimum (`bep_min_profit`) tercapai.
  - **Trailing Stop (STPP Trailing):** Terus menyesuaikan SL dalam langkah-langkah profit tetap (`step_step`), mengunci keuntungan yang telah direalisasi.
- **Sinyal Cepat Scalping:** Memanfaatkan indikator momentum jangka pendek dan pergerakan candlestick berurutan untuk sinyal trading yang sangat cepat.

### 🔍 Analisis Pasar & Strategi (Mode Agresif)

Bot menggunakan strategi _multi-strategy_ sensitivitas tinggi, menggabungkan sinyal dari berbagai sumber untuk menghasilkan keputusan trading.

| Komponen Analisis      | Bobot | Keterangan                                                                                    |
| :--------------------- | :---- | :-------------------------------------------------------------------------------------------- |
| **Indikator Teknikal** | 30%   | _Fast MA Cross_, Posisi Harga, RSI sensitif (40/60), MACD, dan Stochastic cepat (30/70).      |
| **Pola Candlestick**   | 25%   | Mendeteksi Pola Kuat seperti _Engulfing_, _Morning/Evening Star_, dan _Three Soldiers/Crows_. |
| **Deteksi Breakout**   | 20%   | Memantau _breakout_ tinggi/rendah baru-baru ini dan pergerakan volatilitas tinggi.            |
| **Support/Resistance** | 15%   | Memberi sinyal ketika harga mendekati level S/R utama (berbasis Pivot).                       |
| **Sinyal Scalping**    | 10%   | Momentum sangat jangka pendek, lonjakan volume, dan pergerakan _candle_ berurutan.            |

### 🧠 Integrasi AI (Gemini)

- **Inisialisasi Gemini:** Skrip mencoba menginisialisasi klien Gemini dan melakukan tes koneksi saat startup.
- **Analisis Cepat AI (Menu 1):** Opsi _Analyze Now_ (Menu 1) dapat menggunakan Gemini AI untuk memberikan opini cepat, satu kalimat, tentang situasi pasar berdasarkan ringkasan teknikal.

---

## 📈 Kelebihan & Kekurangan (Pros & Cons)

| Kategori      | Kelebihan (Pros)                                                              | Kekurangan (Cons)                                                                                                               |
| :------------ | :---------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| **Strategi**  | ✅ Fokus pada _high-frequency trading_ & _scalping_.                          | ❌ Peka terhadap _noise_ pasar karena ambang sinyal rendah dan sensitivitas tinggi.                                             |
| **Manajemen** | ✅ Ukuran lot dinamis berbasis risiko untuk konsistensi risiko.               | ❌ Parameter ATR, SL/TP harus disesuaikan secara manual per instrumen jika menggunakan aset yang sangat berbeda (misal BTCUSD). |
| **Fitur**     | ✅ Manajemen posisi canggih (BEP, Trailing, Auto-Close).                      | ❌ Fitur _backtest_ hanya menyediakan data mentah (ke CSV), tidak ada simulasi _trade_.                                         |
| **Eksekusi**  | ✅ Mendukung _multi-symbol_ dan _multi-timeframe_ untuk peluang lebih banyak. | ❌ Ketergantungan pada koneksi MT5 yang stabil untuk _real-time execution_.                                                     |
| **AI**        | ✅ Potensi untuk analisis dan validasi sinyal tambahan dari AI (Gemini).      | ❌ Analisis AI memerlukan koneksi internet stabil dan `GEMINI_API_KEY` yang valid.                                              |

---

## 🛠️ Instalasi & Persiapan

### 1\. File Requirements

Buat file bernama `requirements.txt` dengan konten berikut:

```requirements.txt
# Core Dependencies
metatrader5
python-dotenv>=1.0.0
newsapi-python>=0.2.7
tradingeconomics>=0.3.4
ta-lib>=0.4.26
rich>=13.5.2
scikit-learn>=1.3.0
ta>=0.10.2
requests
python-dateutil>=2.8.2
numpy==1.26.4
pandas==2.2.2
google-genai
python-dotenv==0.21.1
google-generativeai==0.5.4
yfinance==0.2.38
matplotlib==3.8.4
```

### 2\. Python Setup

Jalankan perintah berikut untuk menginstal semua _dependency_:

```bash
pip install -r requirements.txt
```

### 3\. Konfigurasi Lingkungan (`.env`)

Buat file bernama **`.env`** di direktori _root_ dan isi detail _login_ serta _API key_ Anda.

| Variabel                | Keterangan                                                               | Sumber            |
| :---------------------- | :----------------------------------------------------------------------- | :---------------- |
| `MT5_LOGIN`             | Nomor _login_ akun MT5 Anda.                                             | Broker Forex Anda |
| `MT5_PASSWORD`          | Kata sandi akun MT5 Anda.                                                | Broker Forex Anda |
| `MT5_SERVER`            | Nama _server_ MT5 broker Anda (misalnya, `Exness-MT5Trial6`).            | Broker Forex Anda |
| `GEMINI_API_KEY`        | _API key_ Anda untuk Gemini AI.                                          | Google AI Studio  |
| `NEWS_API_KEY`          | (_Opsional_) _API key_ untuk mengambil berita keuangan.                  | NewsAPI.org       |
| `TRADING_ECONOMICS_KEY` | (_Opsional_) Kunci untuk data kalender ekonomi (standar: `guest:guest`). | Trading Economics |

**Contoh `.env`:**

```dotenv
MT5_LOGIN=123
MT5_PASSWORD=123
MT5_SERVER=server
GEMINI_API_KEY=APIKEY
NEWS_API_KEY=APIKEY
TRADING_ECONOMICS_KEY=guest:guest
```

### 4\. Konfigurasi Bot (`config.json`)

File ini berisi pengaturan logika inti. File yang disediakan sudah dikonfigurasi untuk **Rapid Fire Mode** pada tiga simbol (`XAUUSDm`, `EURUSDm`, `GBPUSDm`) dengan **Dynamic Lot Sizing** diaktifkan.

**Pengaturan Kunci (di bagian `"current"`):**

| Kunci                      | Nilai Standar | Keterangan                                                                     |
| :------------------------- | :------------ | :----------------------------------------------------------------------------- |
| `"rapid_fire_mode"`        | `true`        | Mengaktifkan pemeriksaan cepat _multi-symbol_/_multi-timeframe_.               |
| `"dynamic_lot_sizing"`     | `true`        | Menghitung lot berdasarkan risiko per _trade_.                                 |
| `"risk_percent_per_trade"` | `1.0`         | Persentase saldo yang dipertaruhkan per _trade_ (digunakan dalam lot dinamis). |
| `"max_total_positions"`    | `10`          | Jumlah maksimum _trade_ yang dibuka secara bersamaan.                          |
| `"max_daily_trades"`       | `100`         | Jumlah maksimum _trade_ yang diizinkan dalam satu hari.                        |
| `"auto_close_target"`      | `0.4`         | Profit dalam USD yang memicu _Auto-Close_.                                     |

---

## ▶️ Cara Penggunaan

### 1\. Jalankan Skrip

Mulai bot dari terminal Anda:

```bash
python main.py
```

### 2\. Koneksi & Menu

- Skrip pertama-tama akan mencoba terhubung ke MT5 menggunakan detail di `.env` dan menginisialisasi klien Gemini.
- Anda akan melihat menu utama, menampilkan pengaturan saat ini dan ringkasan akun.

### 3\. Memulai Trading Otomatis

1.  **Tinjau Pengaturan:** Gunakan opsi menu 2-31 untuk menyesuaikan simbol, _timeframe_, mode _trade_, dan batas posisi jika diperlukan.
    - _Rekomendasi:_ Gunakan **Menu 31** untuk mengatur preset **Rapid Fire** atau **Moderate** dengan cepat.

2.  **Mulai Trading:** Pilih opsi **`99`** dan tekan Enter.

    ```
    99) START TRADING
    ```

    Bot akan memulai siklus analisis dan eksekusi _trade_ berkelanjutan.

### 4\. Hentikan Bot

- Tekan **`Ctrl+C`** di jendela terminal untuk menghentikan bot dengan aman. Bot akan mencetak statistik akhir sebelum mematikan koneksi MT5.

---

## 📋 File-file Utama

| File                 | Keterangan                                                                                                                                    |
| :------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------- |
| `main.py`            | Titik masuk utama. Menangani _setup_, koneksi MT5, _loop_ menu, dan memulai `TradingBot`. Mengandung inisialisasi Gemini.                     |
| `bot_manager.py`     | Kelas `TradingBot` inti. Mengelola siklus _trading_ (termasuk _Rapid Fire_), menegakkan batas posisi, dan menjalankan sinyal.                 |
| `trade_manager.py`   | Menangani semua operasi _trade_ MT5. Berisi logika untuk **SL/TP Berbasis ATR**, **Breakeven**, **Step Trailing**, dan **Auto-Close Profit**. |
| `market_analyzer.py` | Kelas `MarketAnalyzer`. Menerapkan analisis _multi-strategy_ agresif, menggabungkan sinyal teknikal, pola, _breakout_, dan _scalping_.        |
| `config.json`        | Menyimpan konfigurasi pengguna, termasuk simbol yang dipilih, mode _trading_, parameter risiko, dan pengaturan manajemen.                     |
| `requirements.txt`   | Daftar semua paket Python yang diperlukan.                                                                                                    |
| `.env`               | Menyimpan variabel lingkungan sensitif (_login_ MT5 dan _API keys_).                                                                          |

---
