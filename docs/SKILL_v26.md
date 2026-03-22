---
name: bilanco-sonrasi-ucuzlama-tarayicisi
description: >
  BIST hisselerinde (A) bilanço sonrası 6 yöntem değerleme taraması ve (B) haber bazlı
  fiyatlanmamış katalist avcısı. Fintables MCP ile gerçek veri. TCMB dinamik çarpan,
  mean-reversion, forward F/K, PEG+momentum, yapısal iskonto düzeltmesi. GYO/Holding/Banka
  çift filtre. KAP haberleri + web'den sipariş/kapasite/yatırım tarıyarak fiyatlanmamışlığı
  test eder. Deterministik pipeline: MCP→TSV→Python→Excel.
  Tetikleyiciler: "bilanço tarama", "BIST tarama", "ucuz hisse", "forward F/K",
  "kâr sürprizi", "mean reversion", "turnaround", "PEG düşük", "6 yöntem değerleme",
  "GYO NAV iskontosu", "holding iskonto", "banka F/DD", "çift filtre", "yapısal iskonto",
  "haber bazlı fırsat", "katalist tarama", "fiyatlanmamış haber", "sipariş haberi",
  "pipeline tarama", "BIST değer yatırımı".
  BIST ucuzluk, değerleme, fırsat taraması veya katalist analizinde tetikle.
---

# BIST Sistematik Tarama Sistemi v2.6
## (A) Bilanço Sonrası Ucuzlama Tarayıcısı + (B) Haber Bazlı Katalist Avcısı

---

## MİMARİ ÖZET

Bu skill iki paralel framework içerir. İkisi de Fintables MCP'den gerçek veri çeker
(demo data kesinlikle YASAK).

### (A) Bilanço Sonrası Ucuzlama Tarayıcısı
3+1 katman + 6 değerleme yöntemi + TCMB dinamik çarpanı ile bilanço sonrası ucuzlayan
hisseleri sistematik tarar. Pipeline deterministik: aynı TSV girdisi → aynı Excel çıktısı.

**Katmanlar:**
- **1A** — Tarihsel Ortalamaya İskonto (3Y F/K + FD/FAVÖK Mean-Reversion)
- **1B** — Forward F/K (Annualize + Mevsimsel Düzeltme)
- **1C** — PEG Ratio + Kâr Momentum (Büyüme Yakalama)
- **2** — Kâr Sürprizi + 3 Boyutlu Ucuzluk Matrisi
- **NAV** — GYO/Holding/Banka Çift Filtre (ayrı metodoloji)
- **6 Yöntem** — Y1-Y6 değerleme + faiz bazlı ağırlık
- **Yapısal İskonto** — Gerçekleşme oranı + Katalist kontrolü

### (B) Haber Bazlı Katalist Avcısı
KAP haberleri + web'den sipariş/kapasite/yatırım gelişmelerini tarıyarak forward F/K
ile fiyatlanmamışlığı test eder. Turnaround dahil etme kriteri: EBITDA-pozitif + Tier 1
katalist. 3 senaryo forward F/K hesaplaması.

**→ Detaylı haber avcısı metodolojisi: `references/haber-katalist-avcisi.md` oku.**

---

## FİNTABLES MCP AKIŞI (Her İki Framework İçin Zorunlu Sıra)

### 1. Faiz Verisi
```
web_search: "TCMB politika faizi güncel"
```

### 2. Şema Bilgisi (HER OTURUMDA ZORUNLU)
```
finansal_beceri_yukle: "hisse_finansal_tablolari"
finansal_beceri_yukle: "hisse_senetleri"
```
→ SQL yazmadan ÖNCE şema bilgisini al. Bu adım atlanamaz.

### 3. Detaylı Döküman
```
dokuman_chunk_yukle: [şemadan dönen chunk ID'leri]
```

### 4. Veri Sorguları
```
veri_sorgula: SQL sorguları
```
**Kritik kısıtlar:**
- Hard row limit: max 100 satır → büyük sorgularda `LIMIT 100 OFFSET N` pagination
- Bloke: `LATERAL`, `TRIM/BTRIM`, `AT TIME ZONE`, `CURRENT_DATE/NOW()`, `generate_series()`
- Çalışan: `UNNEST(ARRAY[...])`, CTE, literal tarih stringleri (`'2026-03-19'`)
- `character(50)` kolonlarda join için padding dikkate al

### 5. Sembol & Haber Araması
```
sembol_arama: "ticker"
dokumanlarda_ara: '"sözleşme" "sipariş"' (çift tırnak zorunlu, Meilisearch)
```

**→ Tam SQL şablonları: `references/sql-sorgulari.md` oku.**

---

## ADIM 0: FAİZ VERİSİ VE DİNAMİK ÇARPAN

Her tarama öncesi TCMB politika faizini çek. Sabit eşik ASLA kullanılmaz.

### Dinamik Adil F/K
```
Adil F/K = 1 / (TCMB Faizi × 0.70 + %5 Hisse Risk Primi)

Örnek: %50→2.5x | %40→3.0x | %30→3.8x | %25→4.4x | %20→5.3x | %15→6.5x | %10→8.3x
```

### Faiz Eğilimi Düzeltmesi
```
Son 3 TCMB kararı İNDİRİM → Adil F/K'yı %20 yukarı çek, +3 bonus
Son 3 TCMB kararı ARTIRIM → Adil F/K'yı %10 aşağı çek, -3 ceza
```

### Sektör Bazlı Adil Çarpan
```
Sektör Adil F/K = Dinamik Adil F/K × Sektör Çarpanı

Sanayi/Üretim: 1.00x | Bankacılık: 0.50x (birincil: F/DD) | Holding/GYO: NAV
Teknoloji: 1.875x | Savunma: 1.875x | Enerji: 0.75x | Perakende: 1.00x
İnşaat: 0.625x | Turizm: 1.00x | Telekom: 0.875x | Tarım/Gıda: 1.00x
Sigorta: 0.75x | Maden/Metal: 0.75x
```
**→ Detaylı sektör tabloları ve mevsimsellik: `references/sektor-detay.md` oku.**

---

## ÖN FİLTRELER (Zorunlu)

```
1. Piyasa Değeri > 500M TL (pipeline default: PD > 3B)
2. Son çeyrek FAVÖK > 0 (operasyonel sağlık)
3. Faaliyet Kârı: Standart → son Q veya TTM > 0
   Döngüsel (Çimento, Metal, Tekstil, Otomotiv, İnşaat): Q zarar OK ama TTM > 0
4. İşletme NA (TTM): < 0 ve |NA| > PD×%5 → ELEN | ≤ PD×%5 → ⚠️ UYARI
5. Banka/Holding/GYO → KATMAN NAV'a yönlendir (6 yöntem uygulanmaz)
```

### v2.4 Ek Filtreler
```
6. NK Q4 ≤ 0 + TTM NK ≤ 0 → ELEN (hem çeyreklik hem yıllık zarar)
7. Forward F/K hesaplanamıyor (N/A) → potansiyel × 0.7 ceza
8. Minimum skor < 30 → ELEN (kalite eşiği)
```

### v2.5 KÂR KALİTESİ KONTROLÜ (RTALB + CATES Vakaları — Zorunlu)
```
9. Faaliyet Kârı TTM NEGATİF + NK TTM POZİTİF → 🔴 ELEN
   ★ Bu kural SQL'de ve skorlamada ZORUNLU olarak uygulanır.
   RTALB vakası: Faal.Kâr -19M, NK +881M (Özkaynak yöntemi kâr payı 1.1B)
   Piyasa haklı olarak fiyatlamıyor — operasyonel güç yok.

10. Özkaynak Yöntemiyle Değ. Yat. Kâr Payı / NK > %50 → ⚠️ İŞTİRAK TUZAĞI
    > %80 → 🔴 ELEN (kâr tamamen iştirakten, nakit getirmiyor)
    > %50 → ⚠️ Core NK = NK - İştirak Kâr Payı, skor × 0.6 ceza
    RTALB: 1,105M / 881M = %125 → ELEN

11. Faal.Kâr TTM / NK TTM < 0 (farklı işaretler) → Detaylı kontrol zorunlu:
    - Faal.Kâr(-) + NK(+) → Hangi kalem çeviriyor? (iştirak/finansal/yatırım geliri)
    - Faal.Kâr(+) + NK(-) → Kabul edilebilir (finansman gideri, vergi)

12. Faal.Kâr / NK < %30 (ikisi de pozitif) → ⚠️ DÜŞÜK KALİTE KÂR
    NK'nın %70+'si faaliyet dışı kalemlerden (yatırım/finansal/iştirak geliri).
    < %30 → Core NK = Faal.Kâr bazında değerle, skor × 0.5 ceza
    %30-50 → ⚠️ Core NK = Faal.Kâr bazında değerle, skor × 0.7 ceza
    > %50 → ✅ Kabul edilebilir
    
    CATES vakası: Faal.Kâr 368M / NK 1,788M = %21 → skor × 0.5
    Yatırım Faaliyetlerinden Gelir: 2,750M (kâğıt üzerinde dev gelir)
    Q4 Faal.Kâr: -14M → operasyonel iş son çeyrekte zararda
    Core F/K = PD / Faal.Kâr = 8,058M / 368M = 21.9x → adile göre PAHALI
    
    GSDDE: Faal.Kâr 199M / NK 187M = %106 → Rule 12 TEMİZ ama Rule 14'e takılıyor (aşağı bak)
```

### v2.6 EK KONTROLLER (GSDDE Vakasından Öğrenilen — Zorunlu)

```
13. F/K VERİ GÜVENİLİRLİĞİ KONTROLÜ
    3Y'de F/K hesaplanabilen gün sayısı / toplam iş günü (~750) < %50 ise:
    → Y2 (F/K iskonto) skorunu × 0.5 ceza
    
    Neden: Şirket 3Y'nin büyük kısmında zarardaysa, kârlı olduğu kısa dönemlerde
    düşük kârla yapay yüksek F/K oluşur. Bu ortalamayla hesaplanan iskonto sahte olur.
    
    GSDDE vakası: 286 gün / ~750 gün = %38 → 3Y ort F/K 31.76x (yapay yüksek)
    Güncel F/K 7.79x → %75.5 iskonto hesaplandı ama aslında şirket ilk kez düzgün kâr etti.
    → Y2 skoru: 15 × 0.5 = 7.5p (15 yerine)
    
    Sorgu 14'e fk_veri_sayisi kolonu EKLENMELİ.

14. YATIRIM GELİRİ / CİRO KONTROLÜ (Gemi Satışı, Varlık Satışı Tuzağı)
    Yatırım Faaliyetlerinden Gelirler / Ciro oranını kontrol et.
    ★ Bu kalem gelir tablosunda Faaliyet Kârı'ndan SONRA gelir — Rule 12 (Faal.Kâr/NK)
      yakalayamayabilir çünkü yatırım geliri finansman gideri + enfl. muh. ile dengelenebilir.
    
    Yatırım Geliri / Ciro > %50 → skor × 0.5 ceza
    Yatırım Geliri / Ciro > %30 → skor × 0.7 ceza
    Yatırım Geliri / Ciro > %10 → ⚠️ bilgilendirme (tek seferlik olup olmadığını kontrol et)
    
    GSDDE vakası: 302M / 585M = %52 → skor × 0.5 ceza
    302M'nin tamamı M/V Hako gemisi satışından — tek seferlik, tekrarlanmaz.
    Gemi satışı olmasa yıl ZARARDA kapanırdı.
    
    ★ DİKKAT: Bu kural mevcut "Diğer Faal.Gel./Ciro" kuralından FARKLIDIR.
    Diğer Faaliyet Gelirleri (satır 9) ≠ Yatırım Faaliyetlerinden Gelirler (satır 12).
    İkisi de ayrı ayrı kontrol edilmeli.
    
    Sorgu 14'te yatirim_geliri zaten çekiliyor (CATES için eklenmişti).

15. SEKTÖR ORT. F/K TAVANI (3Y Kendi Ortalaması Sınırlaması)
    Referans F/K = min(3Y Kendi Ort F/K, Sektör Güncel Ort F/K × 1.5, Sektör Adil F/K × 1.5)
    Üç değerden en küçüğü referans olur.
    
    Neden: Kronik zararda olan şirketlerin 3Y F/K ortalaması yapay yüksek olabilir
    (kârlı az sayıda günde düşük kârla yüksek F/K). Bu, sektördeki emsallerle
    uyumsuz bir referans noktası yaratır.
    
    Sektör Güncel Ort F/K: hisse_senedi_tarihsel_carpanlar tablosundan, aynı sektördeki
    tüm hisselerin son haftadaki ort F/K (outlier: <0 ve >40 dışla) ile hesaplanır.
    
    GSDDE vakası:
      3Y Kendi Ort: 31.76x
      Sektör Güncel Ort × 1.5: 16.96 × 1.5 = 25.44x
      Sektör Adil × 1.5: 3.24 × 1.5 = 4.86x  ← TAVAN
      → Referans = min(31.76, 25.44, 4.86) = 4.86x
      → İskonto = (1 - 7.79/4.86) = NEGATİF → sektör adiline göre PRİMLİ → Y2 = 0p
    
    Sorgu 14'e sektor_ort_fk kolonu EKLENMELİ.
```

### Sorgu 14'te Zorunlu Ek Kalemler (v2.5 + v2.6)
```
gelir CTE'sine şu kalemler EKLENMELİ:
  - 'Faaliyet Karı (Zararı)' → faal_kar_ttm
  - 'Özkaynak Yöntemiyle Değerlenen Yatırımların Karlarından (Zararlarından) Paylar' → istirak_kar_payi
  - 'Yatırım Faaliyetlerinden Gelirler' → yatirim_geliri (CATES + GSDDE kontrolü için)
  - 'Satış Gelirleri' → ciro_ttm (Rule 14: yatirim_geliri / ciro oranı için)
  
ort CTE'sine şu kolonlar EKLENMELİ:
  - fk_veri_sayisi: COUNT(CASE WHEN fk > 0 AND fk < 80 THEN 1 END) (Rule 13 için)
  - sektor_ort_fk: Aynı sektördeki hisselerin son hafta ort F/K (Rule 15 için)
  
Filtreleme mantığı (SQL veya Python):
  faal_kar_ttm < 0 AND nk_ttm > 0 → ELEN
  istirak_kar_payi > nk_ttm * 0.8 → ELEN (kâr tamamen iştirakten)
  istirak_kar_payi > nk_ttm * 0.5 → skor × 0.6 ceza
  faal_kar_ttm > 0 AND nk_ttm > 0 AND faal_kar_ttm / nk_ttm < 0.3 → skor × 0.5 ceza
  faal_kar_ttm > 0 AND nk_ttm > 0 AND faal_kar_ttm / nk_ttm < 0.5 → skor × 0.7 ceza
  yatirim_geliri / ciro_ttm > 0.5 → skor × 0.5 ceza (Rule 14)
  yatirim_geliri / ciro_ttm > 0.3 → skor × 0.7 ceza (Rule 14)
  fk_veri_sayisi / 750 < 0.5 → Y2 skoru × 0.5 (Rule 13)
  referans_fk = min(ort_fk, sektor_ort_fk × 1.5, sektor_adil_fk × 1.5) (Rule 15)
```

### Piyasa Fazı (5 dönem doğrulanmış)
```
XU100 son 2 ay > +10%  → BOĞA  → filtre gevşet (marj < %3 kabul)
XU100 son 2 ay -5%/+10% → YATAY → filtre TAM UYGULA (+14-25pt alfa)
XU100 son 2 ay < -%5    → AYI   → döngüsel muafiyet, PD/DD < 0.7 öncelikli
```

### Tek Seferlik Gelir Kontrolü (Backtest: +25pt fark)
```
Diğer Faal.Gel. / Ciro > %50 → 🔴 ELEN
Diğer Faal.Gel. / Ciro > %20 → ⚠️ Core Kâr = Faaliyet Kârı × 0.8
Faaliyet Kârı NEGATİF + Net Kâr POZİTİF → 🔴 ELEN (döngüsellerde TTM kontrol)
Tüm 6 yöntem Core Kâr bazında hesaplanır.
```

### İştirak Kâr Payı Tuzağı (v2.5 — RTALB Vakasından Öğrenilen)
```
★ Özkaynak Yöntemiyle Değerlenen Yatırımların Kâr Payları:
  Bu kalem muhasebe kaydıdır — nakit olarak realize olmaz.
  İştirak şirketinin kârından pay alma = kâğıt üzerinde kâr.
  
  İştirak Kâr Payı / NK > %80 → 🔴 ELEN (RTALB vakası)
  İştirak Kâr Payı / NK > %50 → ⚠️ Core NK hesapla, skor × 0.6
  
  RTALB: Ciro 240M, Faal.Kâr -19M, FAVÖK 14M, İştirak Kâr Payı 1,105M, NK 881M
  → Kâr tamamen iştirakten, operasyonel iş zarar ediyor
  → 83 puandan ELEN'e düşürüldü (Q4 2025 taraması)
```

### Faaliyet Dışı Gelir Tuzağı (v2.5 — CATES Vakasından Öğrenilen)
```
★ Yatırım Faaliyetlerinden Gelirler + Finansal Gelirler:
  Faal.Kâr pozitif ama NK >> Faal.Kâr → fark nereden geliyor?
  Yatırım geliri / varlık satışı / finansal gelir = sürdürülebilir değil.
  
  Faal.Kâr / NK < %30 → skor × 0.5, Core F/K = PD / Faal.Kâr ile değerle
  Faal.Kâr / NK  %30-50 → skor × 0.7
  
  CATES: Ciro 6.5B, Faal.Kâr 368M, Yatırım Geliri 2,750M, NK 1,788M
  → Faal.Kâr/NK = %21. Kârın %79'u yatırım gelirinden.
  → Q4 Faal.Kâr: -14M (çeyreklik operasyonel zarar!)
  → Core F/K = PD/Faal.Kâr = 8,058/368 = 21.9x → Sektör adile (2.91x) göre 7.5x pahalı
  → 83p → skor × 0.5 = ~42p → TAVSİYE'ye düşer (ALTIN'dan)
  
  GSDDE: Faal.Kâr 199M / NK 187M = %106 → Rule 12 TEMİZ ama Rule 14'e takılıyor
  Yatırım Geliri 302M / Ciro 585M = %52 → skor × 0.5 (gemi satışı tek seferlik)
```

---

## KATMAN 1A — Tarihsel Ortalamaya İskonto (Mean-Reversion)

```
12Q (3Y) Ort. F/K (outlier: F/K > 80 veya < 0 dışla, min 6Q veri)

★ ÜÇ KATMANLI TAVAN (v2.6):
Referans F/K = min(3Y Kendi Ort F/K, Sektör Güncel Ort F/K × 1.5, Sektör Adil F/K × 1.5)
  - Sektör Adil F/K: TCMB faizi bazlı dinamik hesaplama × sektör çarpanı
  - Sektör Güncel Ort F/K: Aynı sektördeki tüm hisselerin son hafta ort F/K (0 < F/K < 40)
  - 3Y Kendi Ort: Şirketin kendi tarihsel ortalaması (mevcut kural)

★ VERİ GÜVENİLİRLİĞİ (v2.6):
fk_veri_sayisi / ~750 < %50 → Y2 iskonto skoru × 0.5
  - 3Y'nin yarısından fazlasında zararda olan şirketlerin F/K ortalaması güvenilmez

F/K İskontosu = 1 - (Mevcut TTM F/K / Referans F/K)
> %50 → ÇOK DERİN 🟢🟢 | %30-50 → DERİN 🟢 | %15-30 → ORTA 🟡 | < %15 → Elen
Negatif iskonto (primli) → Y2 = 0p

Aynı mantık FD/FAVÖK için de uygulanır.
```

---

## KATMAN 1B — Forward F/K

```
Forward F/K = PD / (Son Çeyrek Core Kâr × 4)
Forward FD/FAVÖK = FD / (Son Çeyrek FAVÖK × 4)
FD = PD + Finansal Borçlar − Nakit
```

### Mevsimsellik Karar Ağacı
```
DÜŞÜK (Sanayi, Banka, Telekom, Yazılım, Savunma, Gıda): Son Q × 4 ✅
ORTA (Sigorta, Maden, İnşaat, Otomotiv): Son Q × 4 + YoY cross-check
YÜKSEK (Turizm, Enerji, Perakende giyim, Tarım): YoY BAZLI ZORUNLU
ÖZEL (Holding, GYO): Kâr annualize etme → NAV İskontosu kullan
```

---

## KATMAN 1C — PEG Ratio + Kâr Momentum

```
PEG = Forward F/K / YoY Kâr Büyüme (%)
< 0.5 → ÇOK UCUZ 🟢🟢 (+3) | 0.5-1.0 → UCUZ | 1.0-2.0 → MAKUL | > 2.0 → PAHALI
Sadece büyüme > %20'de hesapla | Büyüme > %500 → üst sınır %300
Holding/GYO'da PEG HESAPLANMAZ

Turnaround Ayrımı: YoY > %500 ama baz kâr düşük → TURNAROUND (PEG güvenilmez)
Baz eşik: Önceki yıl aynı Q NK > PD × %0.5 olmalı

Ardışık Momentum: 4/4 QoQ pozitif → +5 | 3/4 → +3
Hiper Büyüme: 4Q ardışık YoY > %50 → +3 ek bonus
Forward F/K Daralma: > %50 → +3 | %25-50 → 🟢
```

---

## KATMAN 2 — Kâr Sürprizi + Göreceli Ucuzluk

### 3 Boyutlu Ucuzluk Matrisi
```
1️⃣ Kendine ucuz:  Mevcut F/K < 12Q Ort. F/K
2️⃣ Sektöre ucuz:  Mevcut F/K < Sektör Medyan F/K
3️⃣ Forward ucuz:  Forward F/K < Sektör Adil F/K
✅✅✅ Üçü → ALTIN FIRSAT | ✅✅ İkisi → GÜÇLÜ | ✅ Biri → TAKİP | ❌ → Elen
```

---

## 6 DEĞERLEME YÖNTEMİ (hepsi faize bağlı dinamik çarpanla)

**Y1 FD/FAVÖK:** Önceki dönem vs mevcut → potansiyel
**Y2 Ort. F/K (ANA):** 12Q ort. F/K (faiz tavanlı) / Forward F/K → potansiyel
**Y3 Net Kâr Kapitalizasyonu:** TTM Core Kâr × Sektör Adil F/K + Özsermaye/2 = Hedef PD
**Y4 PD/DD (Banka/Sigorta birincil):** ROE × Dinamik PBV Çarpan = Adil PD/DD
**Y5 Özkaynak Karlılık:** TTM Faaliyet Kârı / Ödenmiş Sermaye × Dinamik Çarpan
**Y6 Likiditasyon:** Kazanç Gücü + Tasfiye Değeri → Downside koruması

### Faiz Bazlı Ağırlık
```
TCMB ≥ %40: Y2=1.5x, Y6=1.5x, diğerleri=0.7x (çarpan bazlılar güvenilmez)
TCMB %20-40: Tümü eşit 1.0x
TCMB ≤ %20: Y1/Y3/Y5=1.3x, Y6=0.8x, Y2=1.0x
```

---

## KATMAN NAV — GYO/Holding/Banka Çift Filtre

> **Backtest:** NAV derin + F/K ucuz = +6.6% ort | NAV derin + F/K primli = -10.5%

```
Veri: hisse_senedi_tarihsel_carpanlar (günlük, ~750 nokta, 3Y)
GYO:     PD/DD %70 + F/K %30 → Çift ucuz en güçlü
Holding: PD/DD %70 + F/K %30 → Potansiyel max %50
Banka:   F/DD %60 + F/K %40 → ROE > %20 bonus +%10
```

### Çift Filtre Karar Matrisi (Q4 2025 Doğrulanmış)
```
PD/DD İSK + F/K İSK → ÇİFT UCUZ 🟢🟢 → portföye al
PD/DD İSK + F/K PRİM → TEKLİ UCUZ ⚠️  → düşük skor, uyarı ekle
PD/DD İSK + F/K MAKUL → ORTA 🟡        → detaylı analiz
PD/DD PRİM → 🔴 ELEN
```

### KATMAN NAV SQL Şablonu
```sql
WITH ort AS (
  SELECT hisse_senedi_kodu,
    ROUND(AVG(CASE WHEN fk > 0 AND fk < 80 THEN fk END)::numeric, 2) AS ort_fk_3y,
    ROUND(AVG(CASE WHEN pddd > 0 THEN pddd END)::numeric, 2) AS ort_pddd_3y
  FROM hisse_senedi_tarihsel_carpanlar
  WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
    AND tarih_europe_istanbul >= '{3Y_ONCE}'
  GROUP BY hisse_senedi_kodu
),
son AS (
  SELECT DISTINCT ON (hisse_senedi_kodu) hisse_senedi_kodu,
    ROUND(fk::numeric, 2) AS son_fk,
    ROUND(pddd::numeric, 2) AS son_pddd
  FROM hisse_senedi_tarihsel_carpanlar
  WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
    AND tarih_europe_istanbul >= '{SON_5_GUN}'
  ORDER BY hisse_senedi_kodu, tarih_europe_istanbul DESC
)
SELECT o.hisse_senedi_kodu,
  o.ort_fk_3y, s.son_fk,
  CASE WHEN s.son_fk > 0 AND o.ort_fk_3y > 0
    THEN ROUND((1 - s.son_fk / o.ort_fk_3y) * 100, 0) END AS fk_iskonto,
  o.ort_pddd_3y, s.son_pddd,
  CASE WHEN s.son_pddd > 0 AND o.ort_pddd_3y > 0
    THEN ROUND((1 - s.son_pddd / o.ort_pddd_3y) * 100, 0) END AS pddd_iskonto
FROM ort o JOIN son s ON s.hisse_senedi_kodu = o.hisse_senedi_kodu
ORDER BY pddd_iskonto DESC NULLS LAST
```

**→ GYO/Holding/Banka skorlama tablosu: `references/backtest-bulgular.md` oku.**

---

## YAPISAL İSKONTO DÜZELTMESİ

```
Düzeltilmiş Potansiyel = Ham Potansiyel × Gerçekleşme Oranı

STANDART: Katalist var → %70-100 | Katalist yok → %30-50 | 1Y alfa < 0 → %20-40
GYO:      Çift ucuz → %40-60 | Tekli ucuz → %0-15 | Katalist → +%20
HOLDİNG:  Katalist var → %25-40 | Yok → %10-20 | Max cap %50
BANKA:    Faiz indirimi trendi → %50-70 | Sabit → %20-30 | ROE>%20 → +%10
```

### 1Y Alfa Uyarı
```
> +%10 → Momentum güçlü ✅ | -10/+10 → Nötr
< -10% → ⚠️ Gerçekleşme -%20 | < -30% → 🔴 Max pot %20, katalistsiz "izle"
```

---

## SKORLAMA (100 + max 31 bonus - ceza)

| Faktör | Ağırlık | Puanlama |
|--------|---------|----------|
| Forward F/K vs Sektör Adil | %25 | <Adil×0.5=25, <Adil=20, <×1.5=15, <×2=8, >×2=0 |
| F/K İskontosu vs 12Q Ort (Y2) | %15 | >%50=15, %30-50=11, %15-30=6, <%15=0 |
| PEG Ratio (1C) | %10 | <0.5=10, 0.5-1.0=7, 1.0-2.0=3, >2.0=0 |
| FD/FAVÖK İskontosu (Y1) | %10 | >%50=10, %30-50=7, %15-30=4, <%15=0 |
| Kâr Sürprizi (YoY+QoQ) | %15 | Çift pozitif=15, Tek=10, Flat=3, Negatif=0 |
| Sektöre Göre Ucuzluk | %10 | <Med.×0.6=10, <Med.=7, ≈Med.=4, >Med.=0 |
| Hedef Fiyat (Y3) | %5 | >%50=5, %25-50=3, %10-25=2, <%10=0 |
| Güvenlik Marjı (Y6) | %5 | Kitap altı=5, Güçlü taban=3, Düşük=0 |
| Turnaround | %5 | Zardan kâra=5, Kâr×2=3, Normal=1 |

### Bonus/Ceza
```
VALUE:  PD/DD<1.0 +3 | 1-1.5 +2 | Faal.Marjı>%15 +2 | Çift isk. +3
        Üçlü ucuzluk +3 | Faiz indirimi +3 | Kitap altı+sürpriz +3
GROWTH: PEG<0.5 +3 | 4Q momentum +5 | 3Q +3 | F/K daralma>%50 +3
        Hiper büyüme +3 | Turnaround+ucuz +2
CEZA:   Tek seferlik>%20 -10 | Faal.zarar+NK+ -15 | PD/DD>4+PEG>2 -5 | Marj<%5 -5
```

---

## ÇIKTI FORMATLARI

### Standart Şirket
```
═══════════════════════════════════════
📌 {KOD} — {ŞİRKET}  [{Sektör}]
{🏆 ALTIN} {🟢 DERİN İSK.} {🚀 HİPER} {🔄 TURNAROUND}
═══════════════════════════════════════
🔍 Tek Seferlik {✅/⚠️/🔴} | PD/DD: X.XX | Marj: %X
📊 Son Q: Ciro|Faal.K|NK | QoQ +%A | YoY +%B
💰 TTM F/K: Ax → Fwd: Bx → Daralma %C
   PEG: D.DD | Y1-Y6 Ham: %X → Düzeltilmiş: %Y
   Katalist: {✅/❌} | 1Y Alfa: %W
⭐ SKOR: XX/100 {+bonus/-ceza}
═══════════════════════════════════════
```

### GYO/Holding/Banka
```
═══════════════════════════════════════
📌 {KOD} [{GYO/Holding/Banka}]
{🟢🟢 ÇİFT UCUZ} {⚠️ F/K PRİMLİ}
═══════════════════════════════════════
🏢 PD/DD: X.XX | 3Y: Y.YY | İsk: %Z
💰 F/K: Ax | 3Y: Bx | İsk: %C
📊 Birleşik Pot: %D | Gerçekleşme: %E
⭐ SKOR: XX/100
═══════════════════════════════════════
```

---

## TARAMA AKIŞI — ENTEGRİK PİPELINE (4 Faz)

> ★ Framework A (finansal) ve Framework B (katalist) artık TEK BİR pipeline'da.
> Her taramada katalist kontrolü otomatik yapılır.

### FAZ 1: FİNANSAL TARAMA (Adım 1-5)
```
1. web_search → TCMB faizi + faiz trendi (son 3 karar)
2. finansal_beceri_yukle → "finansal_tablolar" şema
3. veri_sorgula → Sorgu 14 CTE (6 batch × 100 hisse)
   ★ Zorunlu kalemler: NK TTM, NK Q4, FAVÖK, Faaliyet Kârı, İştirak Kâr Payı, Yatırım Geliri
4. Kategori ayır: Standart / GYO / Holding / Banka
5. Tarihsel iskonto hesapla (3Y ort F/K, PD/DD)
```
→ Çıktı: ~90-100 hisse ham listesi (NK>0, FAVÖK>0, F/K iskontolu)

### FAZ 2: KÂR KALİTESİ + SKORLAMA (Adım 6-9)
```
6. Kâr kalitesi kuralları uygula (Rule 9/10/11/12):
   - Faal.Kâr(-) + NK(+) → ELEN (standart)
   - İştirak/NK > %80 → ELEN | > %50 → skor × 0.6
   - Faal.Kâr/NK < %30 → skor × 0.5 | < %50 → skor × 0.7
7. 6 Yöntem skorlama (Y1-Y6 + faiz ağırlık)
8. GYO/Holding/Banka → KATMAN NAV çift filtre
9. Ön sıralama (skor ≥ 30 geçer)
```
→ Çıktı: ~60 hisse (ön skorlu, henüz katalistsiz)

### FAZ 3: KATALİST + FORWARD F/K (Adım 10-15) ★ YENİ
> Bu faz sadece skor ≥ 30 olan hisseler için çalışır.
> Amacı: "Bu hisse gerçekten ucuz mu, yoksa haklı mı ucuz?" sorusunu cevaplamak.

```
10. BROKER TAHMİNLERİ ÇEK (Toplu SQL):
    SELECT hisse_senedi_kodu, yil, ay,
      AVG(net_kar) AS konsensus_nk,
      AVG(satislar) AS konsensus_ciro,
      AVG(favok) AS konsensus_favok,
      COUNT(DISTINCT araci_kurum_kodu) AS analist_sayisi
    FROM hisse_senedi_araci_kurum_tahminleri
    WHERE hisse_senedi_kodu = ANY(ARRAY[{GEÇEN_HİSSELER}])
      AND yil IN (2025, 2026) AND ay = 12
    GROUP BY hisse_senedi_kodu, yil, ay
    
    + Hedef fiyatlar:
    SELECT hisse_senedi_kodu, hedef_fiyat, tavsiye,
      yayin_tarihi_europe_istanbul
    FROM hisse_senedi_araci_kurum_hedef_fiyatlari
    WHERE hisse_senedi_kodu = ANY(ARRAY[{GEÇEN_HİSSELER}])
      AND yayin_tarihi_europe_istanbul >= '{6_AY_ONCE}'
    ORDER BY hisse_senedi_kodu, yayin_tarihi_europe_istanbul DESC

11. KAP HABERLERİ TARA (Top 20 hisse için dokumanlarda_ara):
    Her hisse için:
      dokumanlarda_ara(
        query="sözleşme sipariş yatırım kapasite ihale",
        filter='dokuman_tipi = "kap_haberi" AND kap_bildirim_tipi = "ODA"
          AND iliskili_semboller = "{KOD}"
          AND yayinlanma_tarihi_utc > {6_AY_ONCE_UTC}',
        sirala="yayinlanma_tarihi_utc:desc",
        sayfa_basi=5
      )
    
    İlginç haber bulunursa → dokuman_chunk_yukle ile detay oku
    Katalist sınıflandır:
      Tier 1: Yeni sipariş/ihale kazanma/tesis devreye alma/satın alma
      Tier 2: Kapasite artışı yatırımı/patent/lisans/kredi notu artışı
      Tier 3: Temettü artışı/geri alım/ESG

12. FORWARD F/K HESAPLA (3 senaryo):
    Öncelik sırası:
    a) Broker konsensüs NK varsa (≥ 2 analist):
       Forward F/K = PD / Konsensüs NK (2026E)
    b) Broker yoksa + katalist varsa:
       Konservatif: PD / (TTM Faal.Kâr)  ← Yatırım geliri dahil değil
       Baz:         PD / (TTM NK × (1 + Katalist Etkisi × 0.5))
       İyimser:     PD / (TTM NK × (1 + Katalist Etkisi))
    c) Broker yok + katalist yok:
       Forward F/K = PD / (Son Q Faal.Kâr × 4)  ← Mevsimsellik kuralı uygula
    
    ★ CATES dersi: Forward hesabında NK DEĞİL, Faaliyet Kârı bazlı hesap her zaman gösterilir.
    ★ Core Forward F/K = PD / (Faal.Kâr TTM) — gerçek operasyonel gücü yansıtır.

13. KATALIST SKORU HESAPLA (max 30 bonus puan):
    Katalist Tier puanı:  Tier 1 = +15 | Tier 2 = +8 | Tier 3 = +3
    Broker desteği:       ≥3 analist AL = +8 | ≥2 analist = +5 | hedef > fiyat×%30 = +3
    Forward F/K fırsatı:  Core Fwd < Sektör Adil = +7 | < Adil×1.5 = +4
    İçeriden alım sinyali: KAP pay alım bildirimi = +3
    Katalist stacking:    2+ farklı Tier 1/2 = +5

14. FIYATLANMAMIŞ MI TESTİ:
    Son 6 ay hisse getirisi vs XU100 getirisi = Alfa
    Alfa < -%10 → FIYATLANMAMIŞ (piyasa haberi görmezden geldi) → +5 bonus
    Alfa -%10/+5 → NÖTR
    Alfa > +%5 → FIYATLANMIŞ (fırsat geçmiş) → katalist bonusu × 0.5

15. YAPISAL İSKONTO DÜZELTMESİ (katalist bilgisiyle):
    Standart + Katalist Tier 1/2 → Gerçekleşme %70-100
    Standart + Katalist yok      → Gerçekleşme %30-50 (düşük!)
    Standart + Sadece broker      → Gerçekleşme %50-70
    GYO/Holding katalist kontrolü → Gerçekleşme +%20 bonus
```

### FAZ 4: FİNAL ÇIKTI (Adım 16-18)
```
16. Final Skor = Faz 2 Skoru + Faz 3 Katalist Bonusu (max 30p)
    → skor × yapısal düzeltme katsayısı
17. Sırala, sinyal ata, CSV oluştur → GitHub push
18. Rapor: Her hisse için finansal + katalist + forward F/K birlikte
```

### HER HİSSE ÇIKTI FORMATI (Entegre)
```
═══════════════════════════════════════════════════════════════
📌 {KOD} — {ŞİRKET}  [{Sektör}]
{🏆 ALTIN} {🟢 DERİN İSK.} {🚀 KATALİSTLİ}
═══════════════════════════════════════════════════════════════
🔍 Kâr Kalitesi: {✅ Temiz / ⚠️ Düşük / 🔴 Tuzak}
   Faal.Kâr/NK: %X | İştirak Payı: %Y
📊 TTM: Ciro|Faal.K|NK | QoQ +%A | YoY +%B
💰 DEĞERLEME:
   TTM F/K: Ax → Core Fwd F/K: Bx → Sektör Adil: Cx
   PD/DD: Dx vs 3Y: Ex (isk %F)
📰 KATALİST: {T1 Sipariş / T2 Kapasite / Yok}
   {Haber özeti, tarih} | Etki: ~%G ciro büyüme
   Broker: N analist, ort hedef ₺H → potansiyel %I
   Fiyatlanmamışlık: alfa %J (son 6 ay)
⭐ FİNANSAL SKOR: XX/100
   + KATALİST BONUS: +YY (Tier/Broker/Forward/Fiyatlanmamışlık)
   = FİNAL SKOR: ZZ | Gerçekleşme: %W
═══════════════════════════════════════════════════════════════
```

### SİNYAL SİSTEMİ (Entegre)
```
🏆 ALTIN KATALİSTLİ → Fin ≥ 60 + Katalist T1/T2 + Fwd < Adil
🟢 DERİN İSKONTO    → Fin ≥ 70, katalist bağımsız
🟡 FORWARD UCUZ      → Fin ≥ 50 + (Broker veya Katalist T1/T2)
🟠 TAVSİYE          → Fin ≥ 40 veya (Fin ≥ 30 + Katalist T1)
⚪ İZLEME           → Fin ≥ 30, katalist yok
🔴 ELEN             → Fin < 30 veya kâr kalitesi başarısız
```

### BATCH OPTİMİZASYONU
```
Faz 1: 6 MCP sorgusu (Sorgu 14, 100'erli batch)
Faz 2: Hesaplama (MCP çağrısı yok)
Faz 3: 
  - 2 SQL sorgusu (broker tahmin + hedef fiyat, toplu)
  - ~15-20 dokumanlarda_ara çağrısı (top 20 hisse KAP haberleri)
  - ~5-10 web_search (sektör bazlı haber taraması)
Faz 4: Hesaplama + CSV + GitHub push
Toplam: ~25-30 MCP/tool çağrısı
```

---

## REFERANS DOSYALARI (Progressive Disclosure)

Bu skill'in detaylı alt dokümanları:

| Dosya | İçerik | Ne Zaman Oku |
|-------|--------|--------------|
| `references/sql-sorgulari.md` | 13+ SQL şablonu (1-13 + 11b/11c) | Veri çekmeden önce |
| `references/backtest-bulgular.md` | 11 dönem + GYO/Holding 6Q backtest | Sonuçları yorumlarken |
| `references/sektor-detay.md` | Sektör çarpanları, mevsimsellik | Sektör bazlı hesaplama |
| `references/haber-katalist-avcisi.md` | Katalist Avcısı v2 tam metodoloji | Haber taraması yaparken |
| `references/prompt-kullanim.md` | Kullanım örnekleri, opsiyonel modlar | Kullanıcı talimatlarında |
| `scripts/pipeline_v24.py` | Deterministik Python pipeline | Tam tarama çalıştırırken |

---

## DETERMİNİSTİK PİPELİNE (v2.6 Entegre)

```
Faz 1: MCP SQL → finansal ham data (6 batch)
Faz 2: Python → kâr kalitesi + skorlama (~60 hisse)
Faz 3: MCP → broker tahmin + KAP haber + forward F/K (~25 çağrı)
Faz 4: Python → final skor + CSV → GitHub push
```

### "Son bilançoları değerle" akışı (İncremental):
1. Son tarama tarihinden sonra yayınlanan bilançoları tespit et
2. Sadece yeni hisseleri Faz 1-4 tam pipeline'dan geçir
3. Mevcut CSV'ye ekle/güncelle → GitHub push

### Tam tarama akışı:
1. Sorgu 14 CTE (6 batch) → ~574 hisse
2. Ön filtre (NK>0, FAVÖK>0, F/K iskontolu) → ~93 hisse
3. Kâr kalitesi (Rule 9/10/12) → ~61 hisse
4. Broker tahminleri (toplu SQL) → forward NK
5. KAP haberleri (top 20-30 hisse) → katalist sınıflandırma
6. Forward F/K 3 senaryo hesapla
7. Katalist bonus + yapısal düzeltme → final skor
8. CSV + GitHub push
