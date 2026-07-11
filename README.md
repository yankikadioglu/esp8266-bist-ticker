# ESP8266 + OLED BIST Takip Ekranı

0.96" SSD1306 OLED üzerinde 20-30 BIST hissesi, BIST30, BIST100 ve gram
altın fiyatını, günlük % değişimle ve mini bir sparkline grafikle
gösteren küçük çaplı bir proje.

## Nasıl çalışıyor?

```
[GitHub Actions, 15 dk'da bir]        [ESP8266, 5 dk'da bir]
  fetch_bist.py  ---->  bist_data.json  ---->  OLED ekranda
  (Yahoo Finance)       (repo'da barınır)      döngüyle gösterir
```

Ağır işi (30 hisseyi Yahoo Finance'ten çekmek, TLS, veri işleme)
GitHub'ın ücretsiz sunucuları yapıyor. ESP8266 sadece ~3-4KB'lık
hazır, sıkıştırılmış bir JSON dosyasını okuyor — bu yüzden hem
hızlı hem kararlı çalışıyor.

## Kurulum

### 1) GitHub tarafı (veri kaynağı)

1. Bu klasördeki dosyaları içeren yeni bir **public** GitHub reposu oluştur
   (public olması şart, çünkü ESP8266 `raw.githubusercontent.com`
   üzerinden anonim erişecek).
2. `fetch_bist.py` içindeki `STOCKS` listesine takip etmek istediğin
   20-30 hisseyi `.IS` uzantısıyla ekle (örn. `"THYAO.IS"`).
   Ticker'ı Yahoo Finance'te (finance.yahoo.com) arayarak doğrulayabilirsin.
3. `.github/workflows/fetch.yml` reponun `Actions` sekmesinde otomatik
   görünecek — istersen "Run workflow" ile elle bir kere tetikleyip
   `bist_data.json`'ın oluştuğunu kontrol et.
4. Oluşan dosyanın RAW linkini not al:
   `https://raw.githubusercontent.com/KULLANICI_ADIN/REPO_ADIN/main/bist_data.json`

### 2) Donanım

- ESP8266 (NodeMCU / Wemos D1 mini)
- 0.96" SSD1306 128x64 I2C OLED
- Bağlantı:
  - `VCC` → 3.3V
  - `GND` → GND
  - `SDA` → D2 (GPIO4)
  - `SCL` → D1 (GPIO5)

### 3) Arduino IDE

1. Kütüphane yöneticisinden kur: **ArduinoJson**, **Adafruit GFX
   Library**, **Adafruit SSD1306**.
2. `esp8266_bist_ticker.ino` dosyasını aç.
3. `WIFI_SSID`, `WIFI_PASS` ve `DATA_URL` değerlerini kendi bilgilerinle
   değiştir.
4. Board olarak kullandığın ESP8266 kartını seç, yükle.

## Özelleştirme fikirleri

- `CYCLE_INTERVAL_MS` → ekranın her hissede ne kadar bekleyeceği
- `FETCH_INTERVAL_MS` → ESP8266'nın veriyi ne sıklıkla tekrar çekeceği
- `HISTORY_DAYS` / `SPARK_HEIGHT` (Python tarafında) → sparkline'ın
  kaç günlük veriden oluşacağı ve dikey çözünürlüğü
- Bir buton ekleyip otomatik döngü yerine elle sonraki/önceki hisseye
  geçiş yaptırabilirsin.
- İleride ESP32 + biraz daha büyük bir renkli TFT'ye geçersen aynı
  JSON formatını kullanarak çok daha detaylı grafikler çizebilirsin.

## Önemli notlar

- Yahoo Finance verisi BIST için **gecikmeli** (genelde 15-20 dk),
  gerçek zamanlı işlem için kullanılmamalı.
- `client.setInsecure()` sertifika doğrulamasını atlıyor — hobi
  projesi için pratik ama üretim/güvenlik açısından ideal değil.
- Gram altın hesabı `GC=F` (ons altın, USD) × `TRY=X` (USD/TRY)
  üzerinden yaklaşık olarak hesaplanıyor; gerçek kuyumcu fiyatından
  küçük farklar olabilir (işçilik/kar marjı dahil değil).
