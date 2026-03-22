# Backtest Bulguları v2.4

## 11 Dönem Backtest Özeti (Q1 2023 — Q4 2025)

### Genel Sonuçlar
```
Toplam Dönem: 11
Pozitif Alfa Dönem: 8/11 (%73)
Ortalama Alfa: +14.2% (YATAY fazda +14-25pt)
En İyi Dönem: Q2 2024 → +28.7% alfa
En Kötü Dönem: Q3 2023 → -4.1% alfa (AYI piyasası)
```

### Piyasa Fazı Bazlı Performans
```
BOĞA (3 dönem):  Ort alfa +8.3% — filtre gevşetme azaltmış
YATAY (5 dönem): Ort alfa +18.9% — EN İYİ PERFORMANS ★
AYI (3 dönem):   Ort alfa +5.2% — PD/DD < 0.7 stratejisi işe yaramış
```

### Tek Seferlik Filtre Etkisi (Bulgu #7)
```
Filtre VARKEN: Ort alfa +14.2%
Filtre YOKKEN: Ort alfa -10.8%
FARK: +25pt → Zorunlu filtre
```

### Nakit Dönüşüm Kalitesi (Bulgu #15)
```
İşletme NA / FAVÖK > 0.7: Ort getiri +18.4%
İşletme NA / FAVÖK < 0.3: Ort getiri +2.1%
ORGE vakası: Kâr yüksek, nakit dönüşüm 0.22 → gerçek güç yok
```

---

## GYO/Holding 6Q Backtest (Q3 2024 — Q4 2025)

### Çift Ucuz Alfa
```
6Q Ortalama: +7.2%
Pozitif Dönem: 4/6 (%67)
En İyi: HLGYO Q4 2024 → +8.2% bilanço sonrası
En Kötü: SNGYO Q1 2025 → -16.9% (F/K primli, tekli ucuz tuzak)
```

### Çift Filtre vs Tekli Filtre
```
ÇİFT UCUZ (PD/DD isk + F/K isk):
  Ort getiri: +6.6% bilanço sonrası
  Gerçekleşme: %25 → v2.4'te güncellendi
  Örnekler: HLGYO (+8.2%), AKSGY (+5.1%), SRVGY (+3.8%)

TEKLİ UCUZ (PD/DD isk + F/K primli):
  Ort getiri: -10.5% bilanço sonrası
  Gerçekleşme: %15 → v2.4'te güncellendi (v2.3'te %0-15)
  Örnekler: SNGYO (-16.9%), BERA (-12.5%)

SONUÇ: NAV iskontosu TEK BAŞINA yetmez — F/K cross-check ZORUNLU
```

### 1Y Getiri Analizi (27 Hisse)
```
STANDART ŞİRKET:
  Katalist var: Ort +22.3% alfa
  Katalist yok: Ort +3.1% alfa
  1Y alfa < -%10: Ort -8.7% (düşüş devam)

HOLDİNG (7 hisse):
  Ort alfa: -3.6% (XU100 +19.3% iken ort +2.5%)
  En iyi: SAHOL +14.2%
  En kötü: NTHOL -5.9%
  → Holding potansiyeli max %50 sınırı doğru

GYO (10 hisse):
  Ort: +30.5% (ama dağılım çok geniş)
  En iyi: HLGYO +74.5%
  En kötü: SRVGY -6.9%
  → Doğru GYO seçimi kritik — çift filtre zorunlu
```

---

## GYO/Holding/Banka Skorlama (100 puan)

| Faktör | Ağırlık | GYO/Holding | Banka |
|--------|---------|-------------|-------|
| PD/DD (NAV) İskontosu | %35 | >%50=35, %30-50=28, %15-30=18, <%15=5 | F/DD >%20=35, %10-20=25, <%10=10 |
| F/K İskontosu (3Y) | %20 | >%30=20, %0-30=12, Primli=0 | >%20=20, %0-20=12, Primli=0 |
| Çift Filtre Bonus | %15 | İkisi isk.=15, Biri=5, İkisi prim=0 | İkisi isk.=15, Biri=5 |
| Kâr Sürprizi (YoY) | %10 | Pozitif=10, Flat=5, Negatif=0 | Aynı |
| PD Büyüklüğü | %10 | >50B=10, 10-50B=7, 1-10B=4, <1B=0 | >100B=10, 10-100B=7 |
| Bilanço Sonrası Getiri | %10 | >%5=10, %0-5=7, -%5-0=3, <-%5=0 | Aynı |

---

## Yapısal İskonto Gerçekleşme Oranları (Doğrulanmış)

| Kategori | Koşul | Gerçekleşme |
|----------|-------|-------------|
| Standart | Katalist var | %70-100 |
| Standart | Katalist yok | %30-50 |
| Standart | 1Y alfa < -%10 | %20-40 |
| GYO | Çift ucuz | %40-60 |
| GYO | Tekli ucuz | %0-15 |
| GYO | + Katalist | +%20 |
| Holding | Katalist var | %25-40 |
| Holding | Katalist yok | %10-20 |
| Holding | Max cap | %50 |
| Banka | Faiz indirimi trendi | %50-70 |
| Banka | Faiz sabit/artış | %20-30 |
| Banka | ROE > %20 | +%10 |

---

## Kritik Uyarılar (Backtest'ten Öğrenilenler)

1. **TTM çarpanlar geçmişi yansıtır** — Yeni sözleşme/kapasite artışı forward modelde yakalanmalı
2. **Nakit dönüşüm kalitesi** — EBITDA-NK farkı finansal gelirden ise (CATES) skor düşür
3. **1Y negatif alfa tuzağı** — "Ucuz görünüyor" ama düşüş yapısal olabilir
4. **Holding yapısal iskontosu kalıcı** — Katalistsiz kapanmaz
5. **GYO kârları gayrimenkul değerlemesinden** — Tekrarlanmaz gelir, F/K dikkatli
6. **Forward F/K N/A cezası** — Hesaplanamıyorsa potansiyel × 0.7 (v2.4)
7. **Pipeline deterministik olmalı** — Elle müdahale sıfır, tekrarlanabilirlik max
8. **İştirak kâr payı tuzağı (v2.5)** — Özkaynak yöntemiyle değerlenen kâr payları nakit getirmez, RTALB vakası
9. **3Y F/K ort yanıltıcı olabilir (v2.6)** — Kronik zarardaki şirketlerde kârlı az günde yapay yüksek F/K → GSDDE vakası
10. **Yatırım geliri tek seferlik (v2.6)** — Gemi/varlık satışı Faal.Kâr/NK'yı bozmaz ama sürdürülebilir değil → GSDDE vakası
11. **Sektör F/K tavanı zorunlu (v2.6)** — 3Y kendi ortalaması sektör ortalamasından çok yüksekse sektör tavanı referans olur
12. **Sektör Adil tavan çift cezalandırma (v2.6b)** — Rule 15'te "Adil × 1.5" kullanma, bu Forward F/K yönteminde zaten var. Yüksek faiz ortamında neredeyse tüm piyasayı cezalandırır.
13. **Q4 kâr yoğunlaşması (v2.6b)** — Son Q NK / TTM NK > %70 veya < %10 ise Forward F/K güvenilmez, TTM F/K kullan. ESCOM (%99), OYYAT (%91), TTKOM (%3) vakaları.

---

## GSDDE Vakası — Yapay F/K İskontosu + Tek Seferlik Yatırım Geliri (v2.6 Bulgusu)

### Olay
GSDDE, Q4 2025 taramasında 83 puanla "ALTIN FIRSAT" sinyali aldı.
F/K iskontosu %75.5 (7.79x vs 3Y ort 31.76x), PD/DD iskontosu %30.7.

### Gerçek Tablo
```
PD: 1.46B TL | Fiyat: 9.72 TL | Sektör: Ulaştırma (Kuru Yük Denizcilik)

Satış Gelirleri (TTM):                 585M TL
Brüt Kâr:                             192M TL
Faaliyet Kârı (TTM):                  199M TL  ← Pozitif, TEMİZ görünüyor
FAVÖK:                                 261M TL
Yatırım Faaliyetlerinden Gelirler:     302M TL  ← GEMİ SATIŞI (M/V Hako, Kasım 2025)
Net Parasal Pozisyon Kayıpları:       -205M TL  ← Enflasyon muhasebesi (IAS 29)
Finansman Giderleri:                   -88M TL
Ana Ortaklık NK (TTM):                187M TL

Faal.Kâr / NK = 199/187 = %106 → Rule 12 TEMİZ (sorun burada değil!)
Yatırım Geliri / Ciro = 302/585 = %52 → TEK SEFERLİK GELİR TUZAĞI
```

### Sorun 1: 3Y F/K Ortalaması Yapay Yüksek
```
3Y Ort F/K: 31.76x
F/K Hesaplanabilen Gün: 286 / ~750 = %38 ← Zamanın %62'sinde ZARARDA
Sektör Ort F/K: 16.96x ← Kendi ortalaması sektörün 1.87 katı
Sektör Adil F/K: 3.24x (TCMB %37, Ulaştırma 1.0x çarpan)

Sorun: Şirket 3Y'nin büyük kısmında zarardaydı. Kârlı olduğu kısa dönemlerde
düşük kârla yüksek F/K oluştu (ör: F/K 50-80x). Bu ortalamayla hesaplanan
%75.5 iskonto gerçekçi değil — şirket sadece ilk kez düzgün kâr etti.

v2.6 Düzeltme (Rule 13 + Rule 15):
  Rule 13: fk_veri_sayisi %38 < %50 → Y2 skoru × 0.5
  Rule 15: Referans = min(31.76, 16.96×1.5) = min(31.76, 25.44) = 25.44x
           → (1 - 7.79/25.44) = %69.4 iskonto → Y2 ham 15p
           AMA Rule 13 cezası: 15 × 0.5 = 7.5p
```

### Sorun 2: Yatırım Geliri Tek Seferlik
```
Yatırım Geliri (302M) = M/V Hako gemisi satışından
Gemi satışı olmasa:
  VÖK ≈ 199M (Faal.Kâr) - 88M (Fin.Gid) - 205M (Enfl.Muh) = ~-94M → ZARAR

Neden Rule 12 yakalayamadı:
  Faal.Kâr/NK = %106 → temiz görünüyor
  AMA: Yatırım geliri (302M) ve enfl. muhasebesi (-205M) + finansman gideri (-88M)
  birbirini dengeliyor. NK (187M) ≈ Faal.Kâr (199M) eşitliği tesadüfi.

v2.6 Düzeltme (Rule 14):
  Yatırım Geliri / Ciro = 302/585 = %52 > %50 → skor × 0.5
```

### Neden Pipeline'dan Kaçtı (v2.5)
1. Faal.Kâr pozitif (199M) → Rule 9 tetiklenmedi ✓
2. İştirak kâr payı yok → Rule 10 tetiklenmedi ✓
3. Faal.Kâr/NK = %106 → Rule 12 tetiklenmedi ✓ (temiz görünüyor!)
4. **Yatırım Geliri / Ciro kontrolü yoktu → 302M/585M = %52 görünmez kaldı**
5. **fk_veri_sayisi kontrolü yoktu → %38 güvenilirlik görünmez kaldı**
6. **Sektör F/K tavanı yoktu → 31.76x referans sektörden 1.87x sapmış**

### v2.6 Düzeltme Sonucu
```
ESKI (v2.5): 83p → 🟢 ALTIN FIRSAT
YENİ (v2.6):
  Y2 (F/K İskonto): 15p → 7.5p (Rule 15: sektör tavanı 25.44x, Rule 13: × 0.5)
  Yatırım geliri cezası: × 0.5 (Rule 14: %52)
  Ham skor: 83 - 7.5 = 75.5 → × 0.5 = ~38p
  → 🟠 TAVSİYE (ALTIN'dan 3 kademe düşüş)

GSDDE'nin gerçek hikayesi: Varlık iskontosu (PD ≈ Nakit), operasyonel nakit
akışı güçlü (%27 cash yield), ama kârlılık enfl. muhasebesi ve tek seferlik
gelirlerle yapay şişirilmiş. Potansiyel sınırlı (~%10-13).
```

### İyi Taraflar (Neden Tamamen ELEN Değil)
```
- PD (1.46B) ≈ Nakit (1.32B) → Downside koruması çok güçlü
- İşletme NA / FAVÖK = 1.50x → Mükemmel nakit dönüşüm
- Cash yield %27 → Operasyonel para makinesi
- 2 yeni gemi siparişi (2028, 2029) → Filo genişleme Tier 2 katalist
- BDI yükselişte (Hürmüz etkisi) → Kısa vadeli pozitif
```

---

## Rule 15 Düzeltmesi — Sektör Adil × 1.5 Kaldırıldı (v2.6b)

### Sorun
Rule 15'in orijinal formülü `min(3Y ort, sektör ort × 1.5, sektör adil × 1.5)` idi.
%37 faiz ortamında "Sektör Adil × 1.5" çok düşük tavan oluşturuyor:
```
Aracı Kurum: Adil 2.91 × 1.5 = 4.37x ama sektör gerçekte 7.60x'de!
Sigorta:     Adil 2.91 × 1.5 = 4.37x ama sektör gerçekte 6.29x'de!
Haberleşme:  Adil 3.40 × 1.5 = 5.10x ama sektör gerçekte 15.68x'de!
```
TOP 10'daki 6/10 hisse gereksiz yere "primli" çıkıyordu.

### Düzeltme
```
ESKİ: Referans = min(3Y Kendi Ort, Sektör Ort × 1.5, Sektör Adil × 1.5)
YENİ: Referans = min(3Y Kendi Ort, Sektör Ort × 1.5)
```
"Sektör Adil" karşılaştırması zaten Forward F/K yönteminde (25p ayrı skor) yapılıyor.
Rule 15'te tekrar koymak çift cezalandırma.

---

## Rule 16 — Çeyreklik Kâr Yoğunlaşma Bulguları (v2.6b)

### ESCOM Vakası — Proje Bazlı Kâr Yoğunlaşması
```
Q1 Ciro:  506K   | NK:  5.3M     Q4/TTM = %99.3
Q2 Ciro:  512K   | NK:  2.3M     3 çeyrek boyunca neredeyse SIFIR ciro
Q3 Ciro:  446K   | NK: -75K
Q4 Ciro:  1.67B  | NK:  1.14B    ← TÜM GELİR VE KÂR TEK ÇEYREKTE

Son Q × 4 = 4.58B → Forward F/K = 0.84x (sahte ucuzluk!)
TTM F/K = 3.32x → Bu da ucuz ama 0.84x kadar abartılı değil.

Sorun: "Bilişim ve Yazılım" sektörü DÜŞÜK mevsimsellik kategorisinde
ama ESCOM proje bazlı çalışıyor → mevsimsellik kuralı yetersiz.
Rule 16: Q4/TTM = %99 > %70 → Forward güvenilmez, TTM kullan.
```

### OYYAT Vakası — Finansman Etkisi Q4 Kâr Patlaması
```
Q1-Q4 Ciro: 4.8B → 7.4B → 8.9B → 9.6B (düzgün artış ✅)
Q1-Q4 Faal.K: 1.5B → 1.6B → 1.5B → 3.0B (Q4 yüksek ama makul)
Q1-Q4 NK: -191M → 254M → 147M → 2,058M (Q4 = %91!)

NK Q4 patlaması Faal.Kâr'dan değil, Faal.Kâr altındaki kalemlerden.
Faal.Kâr TTM 7.68B / NK TTM 2.27B → Finansman giderleri 5.4B yiyor.
Q4'te finansman giderleri azaldığında NK patladı.

Rule 16: Q4/TTM = %91 > %70 → Forward güvenilmez, TTM kullan.
```

### TTKOM Vakası — Q4 NK Çöküşü
```
Q1-Q4 Ciro: 54B → 57B → 62B → 69B (düzgün ✅)
Q1-Q4 Faal.K: 8.8B → 11.5B → 15.8B → 12.6B (düzgün ✅)
Q1-Q4 NK: 6.1B → 5.5B → 10.7B → 719M (Q4 = %3.1!)

Q3→Q4 NK düşüşü -%93. Faal.Kâr düzgün, sorun altında:
Muhtemelen enflasyon muhasebesi (IAS 29) veya finansman gideri patlaması.

Son Q × 4 = 2.88B → Forward F/K = 72x (sahte pahalılık!)
TTM F/K = 9.01x → Gerçek durum bu.

Rule 16: Q4/TTM = %3.1 < %10 → Forward güvenilmez, TTM kullan.
```

---

## Q2 2025 Backtest — v2.6b Kuralları ile Geriye Dönük Test

### Parametreler
```
Dönem: 15 Ağustos → 14 Kasım 2025 (3 ay, Q3 bilançosuna kadar)
TCMB: %43 (indirim trendi) | Adil F/K: 3.42x
XU100: -2.8% (hafif AYI)
Taranan: 597 hisse → 267 (NK+FAVÖK>0) → 71 (F/K iskontolu) → 42 geçen
```

### Faz 1-2 Sonuçları (Sadece Finansal)
```
Tüm hisseler (ELEN hariç 42): Ort alfa -1.9% ❌
TOP 5:  Ort alfa -1.5% ❌
TOP 10: Ort alfa -1.6% ❌
```

### Faz 3 Katalist Etkisi (KAP + Broker)
```
🟢 KATALİSTLİ (10 hisse):
   Ort getiri: +36.8% | Ort alfa: +39.6% | Pozitif: 9/10 (%90)
   TERA     T1 +122.2% (holding devralma)
   LIDER    T2  +69.2% (filo genişleme)
   BLCYT    T2  +46.6% (maddi varlık alımı)
   CVKMD    T1  +39.9% (Sarıalan Altın Madeni)
   ATATP    T1  +38.0% (EEX + yazılım lisans)
   GLYHO    T1  +25.8% (pay alım teklifi)
   ARTMS    T2  +20.0% (Hall Halı sözleşmesi)
   ISGSY    T1  +16.4% (Tatilbudur satın alma)
   KATMR    T1  +13.0% (MSB savunma sözleşmesi)
   PLTUR    T1  -23.2% (tek başarısız katalistli)

🔴 KATALİSTSİZ (28 hisse):
   Ort getiri: -9.6% | Ort alfa: -6.8% | Pozitif: 9/28 (%32)

FARK: +46.4pt alfa → Katalist olmadan ucuzluk yetmiyor (DOĞRULANDI)
```

### Rule 12 Kararı
```
KARAR: DEĞİŞMEDİ — Rule 12 (Faal/NK < %30 → ×0.5) OLDUĞU GİBİ KALACAK.
Gerekçe: TERA ve LIDER'in yükselmesi kâr kalitesiyle değil katalistle ilgili.
Rule 12 + Faz 3 birlikte doğru sonuç veriyor. Muhafazakâr olmak doğru.
```
