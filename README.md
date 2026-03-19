# 📊 BIST Bilanço Sonrası Değerleme Tarayıcısı

> Fintables MCP entegrasyonu ile BIST hisselerinde sistematik 6 yöntem değerleme taraması.
> Pipeline: **MCP CTE Sorgu (6 batch) → SQL Filtreleme → Python Skorlama → GitHub**

## ⚙️ Parametreler

| Parametre | Değer |
|-----------|-------|
| TCMB Politika Faizi | %37 |
| Faiz Trendi | İNDİRİM (5 ardışık sonrası ilk sabit) |
| Baz Adil F/K | 3.89x |
| Dönem | Q4 2025 (2025/12) |
| Taranan Hisse | 574 |
| Filtre Geçen | 93 (NK>0 + FAVÖK>0 + F/K iskontolu) |
| Son Güncelleme | 2026-03-19 |

## 📋 Son Tarama — TOP 20

| # | Kod | Skor | Sektör | PD (B₺) | F/K İsk% | PD/DD | Sinyal |
|---|-----|------|--------|---------|----------|-------|--------|
| 1 | **EUHOL** | 85 | Holding | 1.9 | 96.5 | 0.44 | 🟢 ALTIN FIRSAT |
| 2 | **HLGYO** | 83 | Gayrimenkul | 20.0 | 71.8 | 0.36 | 🟢 ALTIN FIRSAT |
| 3 | **GLRYH** | 80 | Holding | 2.6 | 83.6 | 0.50 | 🟢 ALTIN FIRSAT |
| 4 | **RGYAS** | 80 | Gayrimenkul | 53.2 | 79.0 | 0.40 | 🟢 ALTIN FIRSAT |
| 5 | **ESCOM** | 70 | Bilişim | 3.8 | 57.5 | 1.13 | 🟡 FORWARD UCUZ |
| 6 | **RTALB** | 68 | İlaç/Sağlık | 1.9 | 81.1 | 0.64 | 🟡 FORWARD UCUZ |
| 7 | **SRVGY** | 65 | Gayrimenkul | 10.8 | 11.4 | 0.38 | 🟡 FORWARD UCUZ |
| 8 | **AKFGY** | 64 | Gayrimenkul | 11.3 | 18.9 | 0.34 | 🟡 FORWARD UCUZ |
| 9 | **A1CAP** | 60 | Aracı Kurum | 10.6 | 78.6 | 1.17 | 🟡 FORWARD UCUZ |
| 10 | **CATES** | 60 | Enerji | 8.1 | 67.7 | 0.58 | 🟡 FORWARD UCUZ |
| 11 | MERIT | 58 | Turizm | 5.4 | 77.6 | 0.32 | 🟠 TAVSİYE |
| 12 | MHRGY | 58 | Gayrimenkul | 4.3 | 73.2 | 0.52 | 🟠 TAVSİYE |
| 13 | KRSTL | 58 | Gıda | 1.7 | 64.9 | 0.97 | 🟠 TAVSİYE |
| 14 | KZBGY | 56 | Gayrimenkul | 12.5 | 37.2 | 0.57 | 🟠 TAVSİYE |
| 15 | AYES | 53 | İmalat | 4.8 | 78.7 | 1.60 | 🟠 TAVSİYE |
| 16 | ATATP | 53 | Bilişim | 13.8 | 76.1 | 3.09 | 🟠 TAVSİYE |
| 17 | GSDDE | 53 | Ulaştırma | 1.5 | 75.0 | 0.54 | 🟠 TAVSİYE |
| 18 | MTRKS | 51 | Bilişim | 2.2 | 73.2 | 2.24 | 🟠 TAVSİYE |
| 19 | FORTE | 49 | Bilişim | 7.1 | 8.5 | 2.64 | 🟠 TAVSİYE |
| 20 | THYAO | 45 | Ulaştırma | 399.5 | 9.4 | 0.44 | 🟠 TAVSİYE |

> Tam 93 hisse listesi: [`data/son_tarama.csv`](data/son_tarama.csv)

## 📊 Sinyal Dağılımı

| Sinyal | Sayı |
|--------|------|
| 🟢 ALTIN FIRSAT | 4 |
| 🟡 FORWARD UCUZ | 6 |
| 🟠 TAVSİYE | 28 |
| ⚪ İZLEME | 17 |
| 🔴 ELEN | 38 |
| ❌ Ön Filtre Elenen | 481 |

## 📁 Repo Yapısı

```
Fintables/
├── README.md              ← Güncel özet
├── config.json            ← Parametreler
├── data/
│   ├── son_tarama.csv     ← En güncel sonuç
│   ├── cumulative.csv     ← Tüm zamanlar
│   └── arsiv/2025_4Q.csv  ← Çeyrek arşivi
├── reports/2025_4Q.xlsx
└── scripts/pipeline_v24.py
```

## 🔄 Güncelleme Akışı

1. Claude'a "bilanço tarama yap" yaz
2. Tek CTE sorgusu ile 574 hisse çekilir (6 batch × 100)
3. SQL filtreleme → Python skorlama → CSV
4. GitHub'a push

## ⚠️ Sorumluluk Reddi

Bu repo yatırım tavsiyesi değildir.
