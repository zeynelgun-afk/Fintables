# 📊 BIST Bilanço Sonrası Değerleme Tarayıcısı

> Fintables MCP + KAP Haber Taraması ile sistematik değerleme.
> Pipeline: **MCP CTE → SQL Filtreleme → KAP Katalist → Python Skorlama → GitHub**

## ⚙️ Parametreler

| Parametre | Değer |
|-----------|-------|
| TCMB Politika Faizi | %37 (indirim trendi) |
| Baz Adil F/K | 3.89x |
| Dönem | Q4 2025 (2025/12) |
| Taranan | 574 hisse → 93 filtre geçen |
| KAP Katalist | 19/93 hissede bulundu (10 T1 + 9 T2) |
| Son Güncelleme | 2026-03-19 |

## 📋 TOP 20 (Katalist Entegre)

| # | Kod | Skor | Sektör | PD (B₺) | F/K İsk% | PD/DD | Kat | Sinyal |
|---|-----|------|--------|---------|----------|-------|-----|--------|
| 1 | **EUHOL** | 85 | Holding | 1.9 | 96.5 | 0.44 | - | 🟢 ALTIN |
| 2 | **HLGYO** | 83 | Gayrimenkul | 20.0 | 71.8 | 0.36 | - | 🟢 ALTIN |
| 3 | **GLRYH** | 80 | Holding | 2.6 | 83.6 | 0.50 | - | 🟢 ALTIN |
| 4 | **RGYAS** | 80 | Gayrimenkul | 53.2 | 79.0 | 0.40 | - | 🟢 ALTIN |
| 5 | **ESCOM** | 70 | Bilişim | 3.8 | 57.5 | 1.13 | - | 🟡 FWD UCUZ |
| 6 | **RTALB** | 68 | İlaç | 1.9 | 81.1 | 0.64 | - | 🟡 FWD UCUZ |
| 7 | **SRVGY** | 65 | GYO | 10.8 | 11.4 | 0.38 | - | 🟡 FWD UCUZ |
| 8 | **AKFGY** | 64 | GYO | 11.3 | 18.9 | 0.34 | - | 🟡 FWD UCUZ |
| 9 | **A1CAP** | 60 | Aracı Kurum | 10.6 | 78.6 | 1.17 | - | 🟡 FWD UCUZ |
| 10 | **CATES** | 60 | Enerji | 8.1 | 67.7 | 0.58 | - | 🟡 FWD UCUZ |
| 11 | MERIT | 58 | Turizm | 5.4 | 77.6 | 0.32 | - | 🟠 TAVSİYE |
| 12 | MHRGY | 58 | GYO | 4.3 | 73.2 | 0.52 | - | 🟠 TAVSİYE |
| 13 | KRSTL | 58 | Gıda | 1.7 | 64.9 | 0.97 | - | 🟠 TAVSİYE |
| 14 | AHSGY | 58 | GYO | 14.8 | 51.2 | 1.62 | ★T2 | 🟠 TAVSİYE |
| 15 | FORTE | 58 | Bilişim | 7.1 | 8.5 | 2.64 | ★T1 | 🟠 TAVSİYE |
| 16 | KZBGY | 56 | GYO | 12.5 | 37.2 | 0.57 | - | 🟠 TAVSİYE |
| 17 | AKFIS | 56 | İnşaat | 25.3 | 38.3 | 0.78 | ★T1 | 🟠 TAVSİYE |
| 18 | ORGE | 56 | Enerji Tek | 5.4 | 20.4 | 1.36 | ★T1 | 🟠 TAVSİYE |
| 19 | AYES | 53 | İmalat | 4.8 | 78.7 | 1.60 | - | 🟠 TAVSİYE |
| 20 | THYAO | 53 | Ulaştırma | 399.5 | 9.4 | 0.44 | - | 🟠 TAVSİYE |

## 📊 Sinyal Dağılımı

| Sinyal | Sayı |
|--------|------|
| 🟢 ALTIN FIRSAT | 4 |
| 🟡 FORWARD UCUZ | 6 |
| 🟠 TAVSİYE | 33 |
| ⚪ İZLEME | 18 |
| 🔴 ELEN | 32 |

## 🏷️ KAP Katalist Özeti (19 Hisse)

### Tier 1 — Yüksek Etki (10 hisse)
| Kod | Haber Sayısı | Katalist |
|-----|-------------|----------|
| ORGE | 3 | Bayburt Havalimanı + Altunizade Metro + THY Hub |
| FONET | 5 | Şanlıurfa+Sivas Sağlık ihaleleri + ABD sözleşmesi |
| GESAN | 8 | Çok sayıda ihale (EUPWR ortak) |
| EUPWR | 7 | Yeni sipariş + çok sayıda ihale |
| FORTE | 2 | 2 yeni iş ilişkisi |
| HTTBT | 1 | Basra Airlines havacılık yazılımı |
| YEOTK | 2 | 2 yeni iş ilişkisi |
| GLRMK | 3 | Polonya Varşova Metrosu + demiryolu |
| AKFIS | 1 | Haydarpaşa Sağlık Kampüsü |
| ELITE | 3 | KeHE Distributors ABD ihracat |

### Tier 2 — Orta Etki (9 hisse)
| Kod | Haber Sayısı | Katalist |
|-----|-------------|----------|
| PLTUR | 1 | Yeni iş ilişkisi |
| KBORU | 1 | Yeni iş sözleşmesi |
| TCKRC | 2 | Aydınlatma direği + Karayolları ihale |
| MEGMT | 2 | 2 yeni iş ilişkisi |
| CGCAM | 1 | Sipariş alınması |
| BESTE | 2 | Enerji yatırım + araç muayene |
| NTGAZ | 1 | ÇAYKUR ihalesi |
| SAYAS | 2 | Rüzgar enerji 2 ihale |
| AHSGY | 2 | Başakşehir + Prime Tower arsa ihaleleri |

## ⚠️ Sorumluluk Reddi
Bu repo yatırım tavsiyesi değildir.
