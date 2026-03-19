# 📊 BIST Bilanço Sonrası Değerleme Tarayıcısı

> Fintables MCP + KAP Katalist + Yapısal İskonto Düzeltmesi ile sistematik değerleme.

## ⚙️ Parametreler

| Parametre | Değer |
|-----------|-------|
| TCMB Politika Faizi | %37 (indirim trendi) |
| Baz Adil F/K | 3.89x |
| Dönem | Q4 2025 (2025/12) |
| Taranan | 574 hisse → 93 filtre geçen |
| KAP Katalist | 19/93 hissede (10 T1 + 9 T2) |
| Son Güncelleme | 2026-03-19 |

## 📋 TOP 15 (Yapısal İskonto Düzeltilmiş)

> GYO/Holding'lere backtest gerçekleşme oranları uygulandı (GYO çift ucuz ×0.55, Holding katalistsiz ×0.30)

| # | Kod | Düz.Skor | Sektör | Kat | F/K İsk% | PD/DD | Sinyal |
|---|-----|----------|--------|-----|----------|-------|--------|
| 1 | **ESCOM** | 60 | Bilişim | - | 57.5 | 1.13 | 🟡 FORWARD UCUZ |
| 2 | RTALB | 58 | İlaç/Sağlık | - | 81.1 | 0.64 | 🟠 TAVSİYE |
| 3 | FORTE | 58 | Bilişim | ★T1 | 8.5 | 2.64 | 🟠 TAVSİYE |
| 4 | AKFIS | 56 | İnşaat | ★T1 | 38.3 | 0.78 | 🟠 TAVSİYE |
| 5 | ORGE | 56 | Enerji Tek | ★T1 | 20.4 | 1.36 | 🟠 TAVSİYE |
| 6 | FONET | 53 | Bilişim | ★T1 | 59.9 | 2.60 | 🟠 TAVSİYE |
| 7 | A1CAP | 51 | Aracı Kurum | - | 78.6 | 1.17 | 🟠 TAVSİYE |
| 8 | CATES | 51 | Enerji | - | 67.7 | 0.58 | 🟠 TAVSİYE |
| 9 | ELITE | 51 | Gıda | ★T1 | 28.9 | 1.63 | 🟠 TAVSİYE |
| 10 | MERIT | 49 | Turizm | - | 77.6 | 0.32 | 🟠 TAVSİYE |
| 11 | KRSTL | 49 | Gıda | - | 64.9 | 0.97 | 🟠 TAVSİYE |
| 12 | PLTUR | 49 | Araç Kiralama | ★T2 | 21.3 | 0.68 | 🟠 TAVSİYE |
| 13 | CGCAM | 48 | Cam/Seramik | ★T2 | 51.3 | 1.31 | 🟠 TAVSİYE |
| 14 | HLGYO | 46 | GYO | - | 71.8 | 0.36 | 🟠 TAVSİYE |
| 15 | AYES | 45 | İmalat | - | 78.7 | 1.60 | 🟠 TAVSİYE |

## 📊 Sinyal Dağılımı (Düzeltilmiş)

| Sinyal | Eski | Yeni |
|--------|------|------|
| 🟢 ALTIN FIRSAT | 4 | **0** |
| 🟡 FORWARD UCUZ | 6 | **1** |
| 🟠 TAVSİYE | 33 | **24** |
| ⚪ İZLEME | 18 | **25** |
| 🔴 ELEN | 32 | **43** |

## 🏗️ Yapısal İskonto Düzeltme Katsayıları

| Tip | Koşul | Katsayı | Backtest Gerçekleşme |
|-----|-------|---------|---------------------|
| GYO | Çift ucuz + katalist | ×0.70 | %60-80 |
| GYO | Çift ucuz, katalistsiz | ×0.55 | %40-60 |
| GYO | Tekli ucuz | ×0.30 | %0-15 |
| Holding | Katalist var | ×0.50 | %25-40 |
| Holding | Katalistsiz | ×0.30 | %10-20 |
| Standart | Katalist var | ×1.00 | %70-100 |
| Standart | Katalistsiz | ×0.85 | %30-50 |

## 🏷️ KAP Katalist Özeti

### Tier 1 — Yüksek Etki (10)
ORGE(3), FONET(5), GESAN(8), EUPWR(7), FORTE(2), HTTBT(1), YEOTK(2), GLRMK(3), AKFIS(1), ELITE(3)

### Tier 2 — Orta Etki (9)
PLTUR(1), KBORU(1), TCKRC(2), MEGMT(2), CGCAM(1), BESTE(2), NTGAZ(1), SAYAS(2), AHSGY(2)

## ⚠️ Sorumluluk Reddi
Bu repo yatırım tavsiyesi değildir.
