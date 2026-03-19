# 📊 BIST Bilanço Sonrası Değerleme Tarayıcısı

> Fintables MCP entegrasyonu ile BIST hisselerinde sistematik 6 yöntem değerleme taraması.
> Deterministik pipeline: **MCP → CSV → Skorlama → GitHub**

---

## ⚙️ Parametreler

| Parametre | Değer |
|-----------|-------|
| TCMB Politika Faizi | %37 |
| Faiz Trendi | İNDİRİM (5 ardışık sonrası ilk sabit) |
| Baz Adil F/K | 3.89x |
| Dönem | Q4 2025 (2025/12) |
| Son Güncelleme | 2026-03-19 |

---

## 📋 Son Tarama Sonuçları

| # | Kod | Sektör | PD (B₺) | NK TTM (M₺) | Q4 NK (M₺) | FAVÖK TTM (M₺) | PD/DD | ROE% | Skor | Sinyal |
|---|-----|--------|---------|-------------|------------|----------------|-------|------|------|--------|
| 1 | MAVI | Tekstil, Giyim | 35.1 | 2,294 | -60 | 8,841 | 2.54 | 16.8 | 26 | 🔴 ELEN (Skor<30) |
| 2 | KLGYO | Gayrimenkul | 7.8 | -660 | 103 | 204 | 0.33 | -2.8 | 32 | ⚪ İZLEME |
| 3 | BRLSM | Enerji Tek. | 3.5 | -201 | -177 | 433 | 2.29 | -11.4 | 0 | 🔴 ELEN (NK Çift Zarar) |
| 4 | IEYHO | Holding | 48.4 | -711 | -285 | -131 | 21.44 | -26.0 | 15 | 🔴 ELEN (PD/DD Primli) |
| 5 | ARZUM | Dayanıklı Tük. | 1.6 | -931 | -432 | -100 | -5.70 | -2314 | 0 | 🔴 ELEN (FAVÖK Negatif) |

> **Not:** Bu 5 bilançodan 4'ü zarar açıklamış. %37 faiz ortamında Adil F/K 3.89x — çoğu hisse bu çarpanın çok üzerinde.

---

## 📁 Repo Yapısı

```
Fintables/
├── README.md                    ← Güncel özet (bu dosya)
├── config.json                  ← Faiz, dönem, filtre parametreleri
├── data/
│   ├── son_tarama.csv           ← Her zaman en güncel sonuç
│   ├── cumulative.csv           ← Tüm zamanların birleşik tablosu
│   └── arsiv/
│       └── 2026-03-19.csv       ← Tarih bazlı arşiv
├── reports/
│   └── *.xlsx                   ← Excel raporlar
└── scripts/
    └── pipeline_v24.py          ← Skorlama pipeline
```

## 🔄 Güncelleme Akışı

1. KAP'ta yeni bilanço açıklanır
2. Claude'a "X bilançosunu değerle" yazılır
3. Fintables MCP'den canlı veri çekilir → 6 yöntem skorlama
4. CSV + Excel üretilir → GitHub'a push edilir
5. README otomatik güncellenir

---

## 📖 Metodoloji

**6 Yöntem Değerleme:**
- Y1: FD/FAVÖK İskontosu (3Y ort. karşılaştırma)
- Y2: F/K İskontosu (12Q mean-reversion)
- Y3: Net Kâr Kapitalizasyonu
- Y4: PD/DD Değerleme
- Y5: ROE Kalite
- Y6: Forward vs TTM Momentum

**Sektör Çarpanları:** Teknoloji 1.875x | Sanayi 1.00x | Banka 0.50x (F/DD) | Enerji 0.75x

**GYO/Holding:** NAV bazlı çift filtre (PD/DD + F/K iskontosu)

**v2.4 Filtreleri:**
- NK Q4 ≤ 0 + TTM NK ≤ 0 → ELEN
- Forward F/K N/A → potansiyel × 0.7
- Minimum skor < 30 → ELEN

---

## ⚠️ Sorumluluk Reddi

Bu repo yatırım tavsiyesi değildir. Sistematik tarama aracı olarak tasarlanmıştır.
Yatırım kararlarınızı kendi araştırmanıza dayandırın.
