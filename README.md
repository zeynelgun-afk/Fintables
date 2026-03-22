# BIST Sistematik Değerleme Tarayıcısı v2.6b

**3 Dönem Backtest Doğrulanmış** — Katalistli hisseler ortalama **+65.5% alfa**, katalistsiz **+5.5%**

## Son Tarama: Q4 2025 (22 Mart 2026) — 5 Yöntem Hedef Fiyat

> ⚠️ **MAKRO RİSK:** İran Savaşı (23. gün) + Petrol Krizi | Havacılık ×0.55, Savunma ×1.20

| # | Kod | Sektör | Son₺ | Hedef₺ | **POT%** | Sinyal | Katalist |
|---|-----|--------|------|--------|---------|--------|----------|
| 1 | GLRYH | Holding | 4.33 | 27.43 | **+534%** | 🟡 FWD | - |
| 2 | HLGYO | Gayrimenkul | 5.20 | 16.62 | **+220%** | 🟠 TAVSİYE | - |
| 3 | MTRKS | Bilişim | 21.70 | 65.21 | **+200%** | 🟠 TAVSİYE | - |
| 4 | A1CAP | Aracı Kurum | 15.73 | 40.96 | **+160%** | 🟡 FWD | - |
| 5 | **ESCOM** | Bilişim | 5.43 | 12.81 | **+136%** | 🟡 FWD | R16 |
| 6 | **ATATP** | Bilişim | 146.80 | 331.29 | **+126%** | 🟡 FWD | T1 EEX |
| 7 | **CATES** | Enerji | 48.78 | 94.08 | **+93%** | 🟡 FWD | T1 EÜAŞ R17 |
| 8 | KRSTL | Gıda | 8.74 | 15.35 | **+76%** | 🟡 FWD | - |
| 9 | **ORGE** | Enerji Tek. | 67.50 | 92.69 | **+37%** | 🏆 ALTIN | T1 Metro |
| 10 | **KATMR** | Metal Makine | 2.98 | 4.08 | **+37%** | 🏆 ALTIN | T1 MSB |

### 5 Yöntem Açıklama
- **Y1 Mean Reversion:** 3Y Ort F/K × TTM NK / Hisse Adedi (Rule 13/15 düzeltmeli)
- **Y2 Forward:** Sektör Adil F/K × Forward NK / Hisse Adedi (Rule 16 mevsimsellik)
- **Y3 PD/DD:** 3Y Ort PD/DD × Özkaynak / Hisse Adedi
- **Y4 Broker:** Analist konsensüs hedef fiyat (varsa, ağırlık yüksek)
- **Y5 Core:** Faal.Kâr × Sektör Adil F/K / Hisse Adedi

### ⚠️ Makro Risk Etkisi
- THYAO: Hedef 407₺ × 0.55 = 224₺ → **-23%** (savaş riski)
- PGSUS: Hedef 238₺ × 0.55 = 131₺ → **-26%** (savaş riski)
- KATMR: Hedef 3.40₺ × 1.20 = 4.08₺ → **+37%** (savunma talebi)

## Arşiv
| Dönem | Dosya | Hisse | TOP 3 |
|-------|-------|-------|-------|
| Q4 2025 | `data/arsiv/2025_Q4.csv` | 18 hedef fiyatlı | GLRYH, HLGYO, MTRKS |
| Q3 2025 | `data/arsiv/2025_Q3.csv` | 99→69 geçen | THYAO, GOKNR, PGSUS |

## Veri Kaynağı
Tüm veriler [Fintables MCP](https://evo.fintables.com/mcp) üzerinden gerçek zamanlı çekilir. Demo data kullanılmaz.

---
*Son güncelleme: 22 Mart 2026 — 5 yöntem hedef fiyat + Faz 3.5 Makro Risk + Rule 17 Sözleşme Bonusu*
