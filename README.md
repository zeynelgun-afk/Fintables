# BIST Sistematik Değerleme Tarayıcısı v2.6b

**3 Dönem Backtest Doğrulanmış** — Katalistli hisseler ortalama **+65.5% alfa**, katalistsiz **+5.5%**. Fark: **+59.9pt**.

## Son Tarama: Q4 2025 (22 Mart 2026)

> ⚠️ **MAKRO RİSK AKTİF:** İran Savaşı (23. gün) + Petrol Krizi (%50+ artış) | Şiddet: YÜKSEK
> Havacılık ×0.55, Turizm ×0.70, Savunma ×1.20, Enerji üretici ×1.15

| # | Kod | Sektör | Faz3 | Makro | Final | Sinyal | Katalist |
|---|-----|--------|------|-------|-------|--------|----------|
| 1 | **KATMR** | Metal Makine | 67 | ×1.20 | **80** | 🏆 ALTIN | T1 MSB savunma sözleşmesi |
| 2 | ESCOM | Bilişim | 78 | ×1.0 | 78 | 🟡 FWD | - (proje bazlı R16) |
| 3 | **ORGE** | Enerji Tek. | 69 | ×1.10 | **76** | 🏆 ALTIN | T1 4 metro/havalimanı sözleşmesi |
| 4 | PLTUR | Araç Kiralama | 86 | ×0.85 | 73 | 🟡 FWD | T1 İBB+kamu ihaleleri |
| 5 | A1CAP | Aracı Kurum | 75 | ×0.95 | 71 | 🟡 FWD | - |
| 6 | **INFO** | Aracı Kurum | 74 | ×0.95 | 70 | 🟡 FWD | T1 Varlık edinimi |
| 7 | KRSTL | Gıda | 66 | ×1.0 | 66 | 🟡 FWD | - |
| 8 | **ATATP** | Bilişim | 65 | ×1.0 | 65 | 🟡 FWD | T1 EEX+yazılım lisans |
| 9 | BNTAS | Ambalaj | 62 | ×1.0 | 62 | 🟡 FWD | - |
| 10 | TTKOM | Haberleşme | 61 | ×1.0 | 61 | 🟡 FWD | - |
| ⚠️ 25 | ~~THYAO~~ | ~~Ulaştırma~~ | ~~78~~ | ~~×0.55~~ | **43** | 🟠 TAVSİYE | ~~T1~~ savaş riski |
| ⚠️ 32 | ~~PGSUS~~ | ~~Ulaştırma~~ | ~~71~~ | ~~×0.55~~ | **39** | ⚪ İZLEME | ~~T1~~ savaş riski |

**Dağılım:** 2 Altın, 8 Forward, 22 Tavsiye, 20 İzleme, 24 Elen (76 hisse)

### Faz 3.5 Makro Etki — İran Savaşı
- THYAO: 78p → **43p** (🏆 ALTIN → 🟠 TAVSİYE) — yakıt+sigorta+rota maliyeti
- PGSUS: 71p → **39p** (🟡 FWD → ⚪ İZLEME) — aynı etkiler
- KATMR: 67p → **80p** (🟡 FWD → 🏆 ALTIN) — savunma harcamaları artışı
- ORGE: 69p → **76p** (🟡 FWD → 🏆 ALTIN) — altyapı yatırımı devam

## Framework Özeti

- **TCMB %37** (indirim trendi) → Adil F/K 3.88x
- **5 Faz Pipeline:** Finansal → Kâr Kalitesi → KAP Katalist → Makro Risk → Final
- **Kurallar:** Rule 9-16 (kâr kalitesi, iştirak tuzağı, yatırım geliri, F/K veri güvenilirliği, sektör tavanı, Q4 yoğunlaşma)
- **Faz 3 ZORUNLU:** Katalist 3/3 dönemde +59.9pt fark
- **Faz 3.5 DİNAMİK:** Sabit anahtar kelime yok — her taramada güncel risk taranır

## 3 Dönem Backtest (Doğrulanmış)

| Dönem | Piyasa | XU100 | Katalistli α | Katalistsiz α | Fark |
|-------|--------|-------|-------------|--------------|------|
| Q1 2023 | Süper Boğa | +70.9% | +68.4% | +17.6% | +50.8pt |
| Q1 2025 | Boğa | +13.9% | +88.4% | +5.8% | +82.6pt |
| Q2 2025 | Ayı | -2.8% | +39.6% | -6.8% | +46.4pt |
| **Ortalama** | | | **+65.5%** | **+5.5%** | **+59.9pt** |

Katalistli isabet: **21/22 = %95** (3 dönem toplamı)

## Dosya Yapısı

```
├── README.md
├── data/
│   ├── son_tarama.csv          # Q4 2025 (Faz 3.5 makro risk dahil)
│   └── arsiv/
│       └── 2025_Q4.csv         # Arşiv
├── docs/
│   ├── SKILL_v26.md            # Framework v2.6b (876 satır)
│   ├── sql-sorgulari_v26.md    # SQL şablonları
│   ├── backtest-bulgular_v26.md # 3 dönem backtest + vakalar
│   ├── haber-katalist-avcisi.md
│   ├── prompt-kullanim.md
│   └── sektor-detay.md
└── scripts/
    └── pipeline_v24.py
```

## Veri Kaynağı

Tüm veriler [Fintables MCP](https://evo.fintables.com/mcp) üzerinden gerçek zamanlı çekilir. Demo data kullanılmaz.

---
*Son güncelleme: 22 Mart 2026 — Faz 3.5 Makro Risk Overlay (İran Savaşı+Petrol Krizi) uygulandı*
