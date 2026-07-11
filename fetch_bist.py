"""
BIST hisse/endeks verilerini Yahoo Finance'ten cekip ESP8266 icin
kompakt bir JSON dosyasi (bist_data.json) uretir.

Gereksinim:  pip install yfinance
Calistirma:  python fetch_bist.py
(Bu script GitHub Actions workflow'u tarafindan periyodik olarak
 otomatik calistirilacak sekilde tasarlandi, bkz. .github/workflows/fetch.yml)
"""

import json
from datetime import datetime, timezone

import yfinance as yf

# --- AYARLAR -----------------------------------------------------------
# Takip etmek istedigin 20-30 hisseyi buraya .IS uzantisiyla ekle
STOCKS = [
    "THYAO.IS", "GARAN.IS", "ASELS.IS", "SISE.IS", "KCHOL.IS",
    "EREGL.IS", "BIMAS.IS", "TUPRS.IS", "AKBNK.IS", "YKBNK.IS",
    "SASA.IS", "PETKM.IS", "KOZAL.IS", "TCELL.IS", "ARCLK.IS",
    "FROTO.IS", "TOASO.IS", "PGSUS.IS", "HALKB.IS", "ISCTR.IS",
    "BETAE.IS", "ORZAX.IS", "BIGEN.IS", "ALFAS.IS", "NETCD.IS",
    "DSTKF.IS", "IHAAS.IS", "TERA.IS", "KTLEV.IS", "ASTOR.IS",
    # ... kendi listenle tamamla (20-30 arasi onerilir)
]

# Genel endeksler
INDICES = {
    "BIST100": "XU100.IS",
    "BIST30": "XU030.IS",
}

HISTORY_DAYS = 20      # sparkline icin gun sayisi
SPARK_HEIGHT = 30      # OLED'de grafigin dikey cozunurlugu (0-30 araligina normalize edilir)
OUTPUT_FILE = "bist_data.json"


def fetch_symbol(symbol: str):
    """Bir sembol icin son fiyat, gunluk degisim ve sparkline verisini dondurur."""
    try:
        hist = yf.Ticker(symbol).history(period=f"{HISTORY_DAYS + 5}d")["Close"].dropna()
        if hist.empty:
            print(f"UYARI: {symbol} icin veri bulunamadi")
            return None

        closes = hist.tail(HISTORY_DAYS).tolist()
        last = closes[-1]
        prev = closes[-2] if len(closes) > 1 else last
        change_pct = ((last - prev) / prev) * 100 if prev else 0.0

        lo, hi = min(closes), max(closes)
        span = (hi - lo) or 1
        spark = [round((c - lo) / span * SPARK_HEIGHT) for c in closes]

        return {"p": round(last, 2), "c": round(change_pct, 2), "h": spark}
    except Exception as exc:
        print(f"UYARI: {symbol} alinamadi: {exc}")
        return None


def fetch_gram_altin():
    """Gram altin (TL) fiyatini USD ons altin x USD/TRY uzerinden yaklasik hesaplar."""
    try:
        xau = yf.Ticker("GC=F").history(period="5d")["Close"].dropna()   # ons altin, USD
        usdtry = yf.Ticker("TRY=X").history(period="5d")["Close"].dropna()  # USD/TRY
        if xau.empty or usdtry.empty:
            return None

        def gram(i):
            return (xau.iloc[i] / 31.1035) * usdtry.iloc[i]

        last = gram(-1)
        prev = gram(-2) if len(xau) > 1 and len(usdtry) > 1 else last
        change_pct = ((last - prev) / prev) * 100 if prev else 0.0
        return {"p": round(last, 2), "c": round(change_pct, 2), "h": []}
    except Exception as exc:
        print(f"UYARI: gram altin hesaplanamadi: {exc}")
        return None


def main():
    data = {"ts": datetime.now(timezone.utc).isoformat(), "items": {}}

    for name, symbol in INDICES.items():
        r = fetch_symbol(symbol)
        if r:
            data["items"][name] = r

    gold = fetch_gram_altin()
    if gold:
        data["items"]["GRAMALTIN"] = gold

    for symbol in STOCKS:
        r = fetch_symbol(symbol)
        if r:
            data["items"][symbol.replace(".IS", "")] = r

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print(f"Tamamlandi: {len(data['items'])} kalem '{OUTPUT_FILE}' dosyasina yazildi.")


if __name__ == "__main__":
    main()
