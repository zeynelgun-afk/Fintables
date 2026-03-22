# Fintables — BIST Değerleme Tarayıcısı

## Son Tarama: Q4 2025 (22 Mart 2026 — v2.6 düzeltmeli)

| Parametre | Değer |
|-----------|-------|
| TCMB Faizi | %37 (sabit, önceki 5 toplantı indirim) |
| Adil F/K | 3.88x |
| Taranan | 574 hisse |
| Geçen | 61 hisse (v2.5 kâr kalitesi sonrası) |
| Pipeline | v2.6 |

### Sinyal Dağılımı

| Sinyal | Sayı |
|--------|------|
| 🏆 ALTIN KATALİSTLİ | 1 |
| 🟢 DERİN İSKONTO | 3 |
| 🟡 FORWARD UCUZ | 7 |
| 🟠 TAVSİYE | 21 |
| ⚪ İZLEME | 29 |

### TOP 10

| # | Kod | Sektör | Skor | F/K İsk | Sinyal | Not |
|---|-----|--------|------|---------|--------|-----|
| 1 | PLTUR | Araç Kiralama | 96p | %21.3 | 🏆 ALTIN | İBB sözleşme katalist |
| 2 | THYAO | Ulaştırma | 89p | %9.4 | 🟢 DERİN | Boeing 50 uçak katalist |
| 3 | A1CAP | Aracı Kurum | 84p | %78.6 | 🟢 DERİN | |
| 4 | ESCOM | Bilişim | 84p | %57.5 | 🟢 DERİN | |
| 5 | OYYAT | Aracı Kurum | 69p | %32.9 | 🟡 FWD | |
| 6 | ALBRK | Bankacılık | 68p | %50.5 | 🟡 FWD | |
| 7 | AKGRT | Sigorta | 66p | %38.3 | 🟡 FWD | |
| 8 | BNTAS | Ambalaj | 66p | %23.4 | 🟡 FWD | |
| 9 | RAYSG | Sigorta | 65p | %69.4 | 🟠 TAVSİYE | |
| 10 | TTKOM | Haberleşme | 59p | %40.3 | 🟡 FWD | |

### v2.6 Düzeltme Notları (22 Mart 2026)

GSDDE vakası analizi sonrası 3 yeni kural eklendi:

| Kural | Açıklama | Etkilenen |
|-------|----------|-----------|
| **Rule 13** | F/K veri sayısı < %50 → Y2 × 0.5 | GSDDE (38%), BULGS (26%), CGCAM (35%) |
| **Rule 14** | Yatırım Geliri/Ciro > %50 → skor × 0.5 | GSDDE (52% — gemi satışı) |
| **Rule 15** | Referans F/K = min(3Y ort, sektör ort×1.5, adil×1.5) | GSDDE, CGCAM |

Önceki v2.5 düzeltmeleri (19 Mart): RTALB, CATES, IHGZT elendi. AYES, MERIT, KIMMR skor düştü.

### Dosyalar
- `data/son_tarama.csv` — Son tarama (v2.6 düzeltmeli)
- `data/arsiv/2025_Q4.csv` — Q4 2025 arşiv (v2.5 orijinal)
- `docs/SKILL_v26.md` — Framework v2.6
- `docs/sql-sorgulari_v26.md` — SQL şablonları v2.6
- `docs/backtest-bulgular_v26.md` — Backtest bulguları + GSDDE vakası
- `scripts/pipeline_v24.py` — Pipeline scripti
