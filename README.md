# BIST Sistematik Değerleme Tarayıcısı v2.6b

**3 Dönem Backtest Doğrulanmış** — Katalistli hisseler ortalama **+65.5% alfa**, katalistsiz **+5.5%**. Fark: **+59.9pt**.

## Son Tarama: Q4 2025 (22 Mart 2026)

| # | Kod | Sektör | Skor | Sinyal | Katalist |
|---|-----|--------|------|--------|----------|
| 1 | PLTUR | Araç Kiralama | 86p | 🏆 ALTIN | T1 İBB+kamu ihaleleri |
| 2 | ESCOM | Bilişim | 78p | 🟡 FWD | - (proje bazlı R16) |
| 3 | THYAO | Ulaştırma | 78p | 🏆 ALTIN | T1 AJet+kapasite+yolcu rekoru |
| 4 | A1CAP | Aracı Kurum | 75p | 🟡 FWD | - |
| 5 | INFO | Aracı Kurum | 74p | 🟡 FWD | T1 Varlık edinimi+pay devir |
| 6 | PGSUS | Ulaştırma | 71p | 🟡 FWD | T1 Uçuş kapasitesi artışı |
| 7 | ORGE | Enerji Tek. | 69p | 🟡 FWD | T1 4 metro/havalimanı sözleşmesi |
| 8 | KATMR | Metal Makine | 67p | 🟡 FWD | T1 MSB savunma sözleşmesi |
| 9 | KRSTL | Gıda | 66p | 🟡 FWD | - |
| 10 | ATATP | Bilişim | 65p | 🟡 FWD | T1 EEX+yazılım lisans |

**Dağılım:** 2 Altın, 11 Forward, 22 Tavsiye, 18 İzleme, 23 Elen (76 hisse tarandı)

## Framework Özeti

- **TCMB %37** (indirim trendi) → Adil F/K 3.88x
- **4 Faz Pipeline:** Finansal Tarama → Kâr Kalitesi → KAP Katalist → Final Skor
- **Kurallar:** Rule 9-16 (kâr kalitesi, iştirak tuzağı, yatırım geliri, F/K veri güvenilirliği, sektör tavanı, Q4 yoğunlaşma)
- **Faz 3 ZORUNLU:** AYI piyasasında Faz 1-2 tek başına çalışmıyor (α=-1.9%)

## 3 Dönem Backtest

| Dönem | Piyasa | XU100 | Katalistli α | Katalistsiz α | Fark |
|-------|--------|-------|-------------|--------------|------|
| Q1 2023 | Süper Boğa | +70.9% | +68.4% | +17.6% | +50.8pt |
| Q1 2025 | Boğa | +13.9% | +88.4% | +5.8% | +82.6pt |
| Q2 2025 | Ayı | -2.8% | +39.6% | -6.8% | +46.4pt |
| **Ortalama** | | | **+65.5%** | **+5.5%** | **+59.9pt** |

## Dosya Yapısı

```
├── README.md
├── data/
│   ├── son_tarama.csv          # En güncel tarama sonuçları
│   └── arsiv/
│       └── 2025_Q4.csv         # Q4 2025 arşiv
├── docs/
│   ├── SKILL_v26.md            # Framework v2.6b (799 satır)
│   ├── sql-sorgulari_v26.md    # SQL şablonları
│   ├── backtest-bulgular_v26.md # Backtest sonuçları (3 dönem + vakalar)
│   ├── haber-katalist-avcisi.md # Katalist Avcısı metodolojisi
│   ├── prompt-kullanim.md       # Kullanım örnekleri
│   └── sektor-detay.md          # Sektör çarpanları
└── scripts/
    └── pipeline_v24.py          # Python pipeline
```

## Veri Kaynağı

Tüm veriler [Fintables MCP](https://evo.fintables.com/mcp) üzerinden gerçek zamanlı çekilir. Demo data kullanılmaz.
