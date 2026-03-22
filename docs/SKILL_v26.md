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

# BIST Sistematik Tarama Sistemi v2.6b
## (A) Bilanço Sonrası Ucuzlama Tarayıcısı + (B) Haber Bazlı Katalist Avcısı

> **3 DÖNEM BACKTEST DOĞRULAMASI (Q1 2023 + Q1 2025 + Q2 2025)**
> Katalistli hisseler 3 farklı piyasa fazında (Süper Boğa, Boğa, Ayı) ortalama
> **+65.5% alfa** üretirken, katalistsiz hisseler **+5.5% alfa** kaldı.
> **Fark: +59.9pt** — Faz 3 (KAP + broker) ZORUNLU, atlanamaz.

---

## MİMARİ ÖZET

Bu skill iki paralel framework içerir. İkisi de Fintables MCP'den gerçek veri çeker
(demo data kesinlikle YASAK).

### (A) Bilanço Sonrası Ucuzlama Tarayıcısı (Faz 1-2)
3+1 katman + 6 değerleme yöntemi + TCMB dinamik çarpanı ile bilanço sonrası ucuzlayan
hisseleri sistematik tarar. Pipeline deterministik: aynı TSV girdisi → aynı Excel çıktısı.
**Backtest:** Faz 1-2 tek başına BOĞA'da çalışıyor (α+16.4%), AYI'da çalışmıyor (α-1.9%).

**Katmanlar:**
- **1A** — Tarihsel Ortalamaya İskonto (3Y F/K + FD/FAVÖK Mean-Reversion)
- **1B** — Forward F/K (Annualize + Mevsimsel Düzeltme)
- **1C** — PEG Ratio + Kâr Momentum (Büyüme Yakalama)
- **2** — Kâr Sürprizi + 3 Boyutlu Ucuzluk Matrisi
- **NAV** — GYO/Holding/Banka Çift Filtre (ayrı metodoloji)
- **6 Yöntem** — Y1-Y6 değerleme + faiz bazlı ağırlık
- **Yapısal İskonto** — Gerçekleşme oranı + Katalist kontrolü

### (B) Haber Bazlı Katalist Avcısı (Faz 3) — ★ ZORUNLU
KAP haberleri + web'den sipariş/kapasite/yatırım gelişmelerini tarıyarak forward F/K
ile fiyatlanmamışlığı test eder. Turnaround dahil etme kriteri: EBITDA-pozitif + Tier 1
katalist. 3 senaryo forward F/K hesaplaması.
**Backtest:** Katalist 3/3 dönemde belirleyici fark yaratıyor (+59.9pt ort).
**Faz 3 ASLA atlanamaz** — atlanırsa AYI'da negatif alfa, BOĞA'da düşük alfa.

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
    ★ 3 DÖNEM BACKTEST KARARI: Rule 12 OLDUĞU GİBİ KALACAK (değişiklik yok).
      TERA (+122%) ve LIDER (+69%) Rule 12 ile elendi ama yükselişleri kâr kalitesiyle
      değil KATALİST ile ilgiydi. Rule 12 + Faz 3 birlikte doğru çalışıyor.
      Muhafazakâr kalmak doğru: CATES/RTALB gibi gerçek tuzakları yakalıyor.
    
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
    Referans F/K = min(3Y Kendi Ort F/K, Sektör Güncel Ort F/K × 1.5)
    İki değerden küçük olanı referans olur.
    
    ★ "Sektör Adil F/K × 1.5" KULLANILMAZ — faiz tavanı zaten Forward F/K yönteminde
      (25 puanlık ayrı skor) uygulanıyor. Burada tekrar koymak çift cezalandırma yaratır.
      %37 faiz ortamında Adil × 1.5 ≈ 4-6x → neredeyse tüm piyasa "primli" çıkar.
    
    Neden: Kronik zararda olan şirketlerin 3Y F/K ortalaması yapay yüksek olabilir
    (kârlı az sayıda günde düşük kârla yüksek F/K). Bu, sektördeki emsallerle
    uyumsuz bir referans noktası yaratır.
    
    Sektör Güncel Ort F/K: hisse_senedi_tarihsel_carpanlar tablosundan, aynı sektördeki
    tüm hisselerin son haftadaki ort F/K (outlier: <0 ve >40 dışla) ile hesaplanır.
    
    GSDDE vakası:
      3Y Kendi Ort: 31.76x
      Sektör Güncel Ort × 1.5: 16.96 × 1.5 = 25.44x  ← TAVAN
      → Referans = min(31.76, 25.44) = 25.44x
      → İskonto = (1 - 7.79/25.44) = %69.4 → DERİN
      AMA: Rule 13 (fk_veri %38) → Y2 × 0.5 cezası uygulanır
    
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
  referans_fk = min(ort_fk, sektor_ort_fk × 1.5) (Rule 15 — Adil F/K burada KULLANILMAZ)
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

★ İKİ KATMANLI TAVAN (v2.6):
Referans F/K = min(3Y Kendi Ort F/K, Sektör Güncel Ort F/K × 1.5)
  - Sektör Güncel Ort F/K: Aynı sektördeki tüm hisselerin son hafta ort F/K (0 < F/K < 40)
  - 3Y Kendi Ort: Şirketin kendi tarihsel ortalaması (mevcut kural)
  - ★ "Sektör Adil × 1.5" burada KULLANILMAZ — Forward F/K yönteminde zaten var

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

### Çeyreklik Kâr Yoğunlaşma Kontrolü (v2.6 — Rule 16)
```
★ Mevsimsellik kuralları ÖNCE uygulanır, ardından bu kontrol çalışır.
  "Son Q × 4" ancak kâr çeyreklere makul dağılmışsa güvenilirdir.

Son Q NK / TTM NK > %70 → ⚠️ FORWARD GÜVENİLMEZ (Tüm kâr tek çeyrekte)
  → Forward F/K yerine TTM F/K kullan
  → Y6 (momentum) skoru = 0 (karşılaştırma anlamsız)
  → Forward F/K vs Adil (25p) → TTM F/K vs Adil ile hesapla

Son Q NK / TTM NK < %10 AND Son Q NK > 0 → ⚠️ FORWARD GÜVENİLMEZ (Q4 çöküş)
  → Forward F/K yerine TTM F/K kullan
  → Sebep araştır: enflasyon muhasebesi, finansman gideri, vergi

Son Q NK ≤ 0 AND TTM NK > 0 → Zaten v2.4 Rule 6/7 ile yakalanır

ESCOM vakası: Q1 5.3M + Q2 2.3M + Q3 -75K + Q4 1,144M = TTM 1,152M
  Q4/TTM = %99.3 → FORWARD GÜVENİLMEZ
  Q1-Q3 ciro toplamı 1.5M (!) vs Q4 ciro 1.67B → proje bazlı şirket
  Son Q × 4 = 4.58B → Forward F/K 0.84x (sahte ucuzluk!)
  Doğru: TTM F/K = 3.32x (bu da ucuz ama 0.84x kadar değil)

OYYAT vakası: Q4 NK / TTM NK = 2.06B / 2.27B = %91
  AMA: Faal.Kâr dağılımı düzgün (Q1-Q4: 1.5B, 1.6B, 1.5B, 3.0B)
  NK Q4 patlaması Faal.Kâr altındaki kalemlerden → ⚠️
  Forward F/K TTM bazlı hesaplanmalı

TTKOM vakası: Q4 NK / TTM NK = 719M / 23B = %3.1
  Q3 NK = 10.7B → Q4'te %93 düşüş (enfl. muh. veya fin. gideri)
  Son Q × 4 = 2.88B → Forward F/K 72x (sahte pahalılık!)
  Doğru: TTM F/K = 9.01x
```

### Gelecek Sözleşme Değerleme Bonusu (v2.6b — Rule 17, CATES Vakasından)
```
★ Rule 12/14 geçmiş çeyreğin kâr kalitesini cezalandırır — DOĞRU.
  AMA: Gelecek gelir görünürlüğü sağlayan büyük sözleşmeler varsa,
  geçmiş operasyonel zayıflık gelecekte düzelebilir.
  Bu kural Faz 3'te KAP haberi taranırken uygulanır.

KOŞUL: KAP'ta veya web'de tespit edilen GARANTİLİ GELİR SÖZLEŞMESİ varsa:
  (alım garantisi, off-take, uzun vadeli satış anlaşması, EÜAŞ sözleşme vb.)

SÖZLEŞME BÜYÜKLÜK PUANI (max 20p):
  Yıllık Garanti Gelir / Ciro oranına göre:
    > %50 → +20p (TRANSFORMATÖR — cironun yarısından fazlası garanti)
    %30-50 → +15p
    %10-30 → +10p
    < %10 → +5p

SÜRE ÇARPANI:
  > 3 yıl → puan × 1.5 (uzun vadeli görünürlük)
  1-3 yıl → puan × 1.0
  < 1 yıl → puan × 0.7 (kısa vadeli, sınırlı etki)

DÖVİZ BONUSU:
  USD/EUR bazlı sözleşme → +5p ek (kur koruması + TL zayıflamasında upside)
  TL bazlı → +0p

UPSIDE BONUSU:
  Taban fiyat + piyasa fiyatı üstü açık → +3p (PTF yükselirse ekstra kâr)
  Sabit fiyat (upside yok) → +0p

RULE 12/14 CEZA HAFİFLETME:
  ★ Garantili sözleşme tespit edildiyse VE sözleşme bonusu ≥ 15p ise:
    Rule 12 cezası ×0.5 → ×0.7'ye hafiflet (gelecek kâr kalitesi farklı olabilir)
    Rule 14 cezası ×0.7 → ×0.85'e hafiflet (tek seferlik gelir + gelecek garanti)
  Gerekçe: Geçmiş çeyrek operasyonel zayıflık gösterse bile, garantili gelecek
  sözleşme hisse değerini korur. Piyasa bunu fiyatlıyor (CATES +45% kanıt).

CATES EÜAŞ vakası (29 Ekim 2025):
  Sözleşme: 4 yıl, yıllık 1.65M MWh, min 75 USD/MWh
  Yıllık garanti gelir: ~4.46B TL = ciro %69 → +20p (TRANSFORMATÖR)
  Süre: 4 yıl → × 1.5 = 30p
  Döviz: USD bazlı → +5p
  Upside: PTF > 75 USD ise piyasa fiyatı → +3p
  TOPLAM SÖZLEŞME BONUSU: 38p
  
  Rule 12 hafifletme: ×0.5 → ×0.7 (sözleşme bonusu 38p ≥ 15p)
  
  Düzeltilmiş skor:
    ESKİ: ~50p × 0.5 (R12) × 0.7 (R14) = ~18p → ELEN
    YENİ: ~50p × 0.7 (R12 hafif) × 0.85 (R14 hafif) + 38p bonus
         = ~30p + 38p = ~68p → 🟡 FWD
    Piyasa: CATES sözleşme sonrası +45% → framework artık piyasayla uyumlu

GOKNR Kazakistan vakası (Ekim 2025):
  Sözleşme: Fabrika kurulumu + off-take (alım garantisi), 18M USD
  Garanti gelir: ~650M TL/yıl, ciro %9 → +5p
  Süre: ~3 yıl → × 1.0 = 5p
  Döviz: USD → +5p
  TOPLAM: 10p (sözleşme bonusu < 15p → Rule 12 hafifletme YOK)

★ DİKKAT: Sözleşme bonusu sadece GARANTİLİ gelir için geçerli.
  "Görüşmelere başlandı" veya "MoU imzalandı" → bonus verilmez (henüz garanti değil)
  "Sözleşme imzalandı" + tutarı belli → bonus verilir
  "İhale kazanıldı" + resmi onay → bonus verilir
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

## 5 DEĞERLEME YÖNTEMİ — HEDEF FİYAT (hepsi faize bağlı dinamik çarpanla)

> ★ Aşağıdaki yöntemler artık PUAN değil, HEDEF FİYAT üretir.
> Her yöntem = "Bu hissenin olması gereken fiyatı şu kadardır" der.
> Ağırlıklı ortalaması alınarak tek bir hedef fiyat oluşturulur.

**Y1 Mean Reversion F/K:** Referans F/K × TTM NK / Hisse Adedi → Hedef Fiyat₺
**Y2 Forward F/K:** Sektör Adil F/K × Forward NK / Hisse Adedi → Hedef Fiyat₺
**Y3 PD/DD Reversion:** 3Y Ort PD/DD × Özkaynak / Hisse Adedi → Hedef Fiyat₺
**Y4 Broker Hedef:** Analist konsensüs ortalaması → Hedef Fiyat₺ (varsa)
**Y5 Core Earning Power:** Faal.Kâr × Sektör Adil F/K / Hisse Adedi → Hedef Fiyat₺

### Faiz Bazlı Çarpan Etkisi
```
TCMB yüksek (≥%35): Sektör Adil F/K düşük → Y2/Y5 düşük hedef verir → ağırlık azalt
TCMB orta (%20-35): Dengeli
TCMB düşük (<%20): Sektör Adil F/K yüksek → Y2/Y5 yüksek hedef verir → güvenilir
→ Faiz düşerken tüm hedef fiyatlar otomatik yükselir (çarpan genişlemesi)
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

### 3 Dönem Backtest Kanıtı (★ DOĞRULANMIŞ)
```
                          Q1 2023         Q1 2025         Q2 2025         ORT
  Piyasa Fazı              SÜPER BOĞA      BOĞA            AYI             —
  XU100                    +70.9%          +13.9%          -2.8%           +27.3%
  Katalistli Alfa          +68.4%          +88.4%          +39.6%          +65.5%
  Katalistsiz Alfa         +17.6%          +5.8%           -6.8%           +5.5%
  FARK (Kat - KatYok)      +50.8pt         +82.6pt         +46.4pt         +59.9pt
  Katalistli İsabet        5/5 (%100)      7/7 (%100)      9/10 (%90)     21/22 (%95)
```

### Gerçekleşme Oranları (Backtest ile doğrulanmış)
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

## HEDEF FİYAT HESAPLAMA (5 Yöntem Ağırlıklı)

> ★ Puanlama sistemi SADECE eleme içindir (Faz 1-2'de geç/geçme kararı).
> Yatırım kararı = HEDEF FİYAT + % POTANSİYEL ile verilir.
> Her geçen hisse için 5 farklı yöntemle "olması gereken fiyat" hesaplanır.

### ELEME KRİTERLERİ (Skor sadece bunun için kullanılır)
```
ELEN: NK < 0 veya FAVÖK < 0 veya Faal.Kâr < 0 (standart)
ELEN: Rule 9 (Faal.Kâr(-) + NK(+))
ELEN: Rule 10 (İştirak/NK > %80)
ELEN: F/K primli (mevcut > referans) — yükselme potansiyeli yok
GEÇER: Yukarıdakilerin hiçbirine takılmayan → Hedef Fiyat hesapla
```

### 5 YÖNTEM

```
★ FORWARD NK SEÇİMİ (Rule 18 — Tüm yöntemlerin temeli):
  Son 4 çeyrekte ciro ve NK trendini tespit et:
    ARTIŞ:  Son 3Q'da son/ilk > 1.15           → Forward NK = Son Q × 4
    SABİT:  Son 3Q'da belirgin yön yok          → Forward NK = TTM NK
    DÜŞÜŞ:  Son 3Q'da son/ilk < 0.75            → Forward NK = Son 2Q Ort × 4
    SPIKE:  Bir Q diğerlerinin 2.5x'i (medyan)  → Forward NK = Spike Hariç Medyan × 4
  
  ATATP vakası: Q2=1089, Q3=503, Q4=341 → SPIKE → medyan(121,503,341)=341 → 341×4=1364M
  (TTM 2054M yerine — %33 düşüş!)
  
  TREND ÇARPANI = ort(ciro_trend_çarpanı, nk_trend_çarpanı)
    Artış → ×1.10 | Sabit → ×1.00 | Düşüş → ×0.70 | Spike → ×0.75
    Y5 (Core Earning Power)'da Faaliyet Kârına uygulanır.

Y1: MEAN REVERSION F/K (Ağırlık: %25 veya R13'te %10)
    Hedef PD = Referans F/K × Forward NK (TTM değil!)
    Referans F/K = min(3Y Kendi Ort, Sektör Ort × 1.5) — Rule 15
    R13 (fk_cnt/750 < %50) → ağırlık %25 → %10'a düşür
    Hedef Fiyat = Hedef PD / Hisse Adedi

Y2: FORWARD F/K (Ağırlık: %25)
    Hedef PD = Sektör Adil F/K × Forward NK (trend bazlı seçilmiş!)
    Broker konsensüs NK varsa (≥2 analist) → onu tercih et
    Hedef Fiyat = Hedef PD / Hisse Adedi

Y3: PD/DD REVERSION (Ağırlık: %20 — trend bağımsız)
    Hedef PD = 3Y Ort PD/DD × Ana Ortaklık Özkaynağı
    GYO/Holding'de ağırlık %30'a çık (NAV birincil)
    ★ Bu yöntem trende bağlı değil — varlık bazlı değerleme
    Hedef Fiyat = Hedef PD / Hisse Adedi

Y4: BROKER HEDEF FİYAT (Ağırlık: %30 varsa, %0 yoksa)
    Son 6 ay aracı kurum hedef fiyatların ortalaması
    ≥ 3 analist → ağırlık %30 (güvenilir konsensüs)
    1-2 analist → ağırlık %15
    0 analist → bu yöntem atlanır, diğerleri yeniden ağırlıklanır

Y5: CORE EARNING POWER (Ağırlık: %15)
    Hedef PD = (Faaliyet Kârı TTM × Trend Çarpanı) × Sektör Adil F/K
    ★ Yatırım/finansal gelir dahil değil — saf operasyonel güç
    ★ Trend çarpanı burada uygulanır (artış → kâr artacak, düşüş → azalacak)
    Rule 17 sözleşme bonusu varsa: ×2.5 çarpan
    Hedef Fiyat = Hedef PD / Hisse Adedi
```

### AĞIRLIK TABLOSU
```
                    Broker VAR (≥3)    Broker AZ (1-2)    Broker YOK
Y1 Mean Rev.            %20               %25              %25
Y2 Forward              %20               %25              %25
Y3 PD/DD                %15               %20              %20
Y4 Broker               %30               %15               -
Y5 Core                 %15               %15              %15
Ek: GYO/Holding         -                  -                -
    → Y3 ağırlık +%10, Y1/Y2 ağırlık -%5 (NAV birincil)

R13 aktif (düşük F/K verisi) → Y1 ağırlık %10'a düşür, Y5'e aktar
```

### HEDEF FİYAT → POTANSİYEL
```
Ham Hedef Fiyat = Σ(Yöntem Hedef × Ağırlık) / Σ(Ağırlıklar)
Makro Düzeltilmiş Hedef = Ham Hedef × Makro Çarpan (Faz 3.5)
Upside = Makro Hedef - Son Fiyat
Final Hedef = Son Fiyat + Upside × Gerçekleşme Oranı

Potansiyel % = (Final Hedef / Son Fiyat - 1) × 100
```

### GERÇEKLEŞME ORANLARI (Backtest doğrulanmış + Momentum düzeltmeli)
```
BAZ ORANLAR:
  Standart + T1 Katalist: %85
  Standart + T2 Katalist: %70
  Standart + Broker (katalist yok): %60
  Standart + Katalist yok + Broker yok: %40
  GYO Çift Ucuz + Katalist: %55 | Katalistsiz: %35
  Holding (katalist var): %35 | Katalist yok: %20

MOMENTUM DÜZELTMESİ (4 çeyrek NK trendi):
  4Q ardışık NK artışı → gerçekleşme +%10 (büyüyen şirket hedefe ulaşır)
  3Q ardışık NK düşüşü → gerçekleşme -%10 (küçülen şirket hedefe ulaşamaz)
  Aksi → değişiklik yok

GÜVENLİK MARJI (downside koruması):
  PD/DD < 1.0 → gerçekleşme +%5 (varlık desteği var, düşüş sınırlı)
  Ayrıca: Hedef fiyat en az = defter değeri (taban fiyat)
```

### SİNYAL SİSTEMİ (FAİZ BAZLI — Dinamik Eşikler)
```
★ Sinyal eşikleri TCMB faizine bağlıdır. Mevduattan iyi performans gösteremeyen hisseye AL DENMEZ.

Minimum AL Eşiği = Risksiz Getiri + Hisse Risk Primi
Risksiz Getiri = TCMB Politika Faizi (mevduat yaklaşık bu kadar verir)
Hisse Risk Primi = +%15 (BIST tarihsel risk primi)

Örnek: TCMB %37 → Min AL = %37 + %15 = %52
        TCMB %25 → Min AL = %25 + %15 = %40
        TCMB %15 → Min AL = %15 + %15 = %30

🏆 ALTIN FIRSAT  → Potansiyel > Min AL×1.5 + T1/T2 Katalist (~%80 @%37 faiz)
🟢 GÜÇLÜ AL      → Potansiyel > Min AL + Katalist VEYA > Min AL×1.5 (~%80 katalistsiz)
🟡 AL            → Potansiyel > Min AL (~%52 @%37 faiz — mevduattan iyi)
🟠 TUT           → Potansiyel %30 - Min AL (mevduata yakın ama potansiyel var)
⚪ İZLE          → Potansiyel %0-%30 (mevduat daha iyi — hisse almaya değmez)
🔴 SAT           → Potansiyel < %0

Neden: %37 faizle mevduat yılda ~%40 veriyor. %20 potansiyelli hisseye AL demek
       yatırımcıya zarar verir — risksiz alternatif daha iyi. Faiz düştükçe eşik düşer,
       daha çok hisse AL sinyali alır. Bu otomatik çalışır.
```

---

## ÇIKTI FORMATI

### Her Hisse İçin (Tek Format — Standart + GYO/Holding/Banka)
```
═══════════════════════════════════════════════════════════════
📌 {KOD} — {ŞİRKET}  [{Sektör}]
{🏆 ALTIN FIRSAT / 🟢 GÜÇLÜ AL / 🟡 AL / 🟠 TUT / ⚪ İZLE / 🔴 SAT}
═══════════════════════════════════════════════════════════════
💰 Son Fiyat: ₺X.XX → Hedef Fiyat: ₺Y.YY → POTANSİYEL: +%ZZ

📊 5 YÖNTEM DETAY:
   Y1 Mean Rev (3Y F/K):    ₺A.AA  [ağırlık %W1]
   Y2 Forward (Sektör Adil): ₺B.BB  [ağırlık %W2]
   Y3 PD/DD Reversion:       ₺C.CC  [ağırlık %W3]
   Y4 Broker Konsensüs:      ₺D.DD  [ağırlık %W4] — N analist
   Y5 Core Earning Power:    ₺E.EE  [ağırlık %W5]
   Ham Hedef: ₺F.FF × Makro ×G.G × Gerçekleşme %H = ₺Y.YY

🔍 KALİTE:
   Kâr Kalitesi: {✅ Temiz / ⚠️ Düşük / 🔴 Tuzak}
   Faal.Kâr/NK: %X | PD/DD: Y.Yx | R12/R14/R16/R17: {varsa}

📰 KATALİST: {T1 Sipariş / T2 Kapasite / R17 Sözleşme / Yok}
   {Haber özeti} | Gerçekleşme: %H

⚠️ MAKRO: {Risk Tipi} → Sektör çarpanı ×G.G
═══════════════════════════════════════════════════════════════
```

### Özet Tablo (Tüm Hisseler)
```
# Kod      Son₺    Hedef₺    POT%   Y1     Y2     Y3     Y4     Y5    Makro  Sinyal
─────────────────────────────────────────────────────────────────────────────────────
1 XXXXX    XX.XX   YY.YY    +ZZ%   AA.AA  BB.BB  CC.CC  DD.DD  EE.EE  ×G.G  🏆 ALTIN
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

### FAZ 2: KÂR KALİTESİ + ELEME (Adım 6-9)
```
6. Kâr kalitesi kuralları uygula (Rule 9/10/11/12):
   - Faal.Kâr(-) + NK(+) → ELEN (standart)
   - İştirak/NK > %80 → ELEN | > %50 → ⚠️ işaretle
   - Faal.Kâr/NK < %30 → ⚠️ işaretle (Faz 4'te hedef fiyatta yansır)
7. Rule 13/14/15/16 kontrolleri → ⚠️ işaretle (Faz 4'te ağırlıklarda yansır)
8. GYO/Holding/Banka → KATMAN NAV çift filtre (tek ucuz ELEN)
9. F/K primli (mevcut > referans) → ELEN
```
→ Çıktı: ~60 hisse (elemeyi geçen, henüz hedef fiyatsız)

### FAZ 3: KATALİST + FORWARD F/K (Adım 10-15) — ★★★ ZORUNLU, ASLA ATLANMAZ
> **3 Dönem Backtest Kanıtı:** Faz 3 olmadan AYI'da α=-1.9%, Faz 3 ile α=+39.6%.
> Katalist farkı 3 dönem ortalaması +59.9pt. Faz 3 atlanırsa tarama GEÇERSİZ sayılır.
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

### FAZ 3.5: MAKRO RİSK OVERLAY (Adım 16-17) — DİNAMİK
> Her taramada güncel makro/jeopolitik riskleri tespit et, sektörel etkiyi skorlara yansıt.
> Sabit anahtar kelime KULLANILMAZ — risk her çeyrekte farklı olabilir.

```
16. RİSK TESPİTİ (web_search — her taramada zorunlu):
    web_search: "BIST risk bu hafta"
    web_search: "Türkiye ekonomi gündem"
    
    Amaç: Şu an piyasayı etkileyen #1 risk faktörünü TANI.
    Örnekler (çeyreğe göre değişir):
      2026-Q1: İran savaşı → petrol+havacılık+turizm etkisi
      2025-Q3: Kur krizi → ihracatçı/ithalatçı etkisi
      2024-Q2: Seçim → politik belirsizlik
      2023-Q1: Deprem → inşaat/sigorta etkisi
      Başka dönem: Pandemi, ticaret savaşı, faiz şoku, düzenleme...

17. SEKTÖREL ETKİ ÇARPANI UYGULA:
    Tespit edilen risk → aşağıdaki tablodan eşleşen satırı bul → çarpanı uygula.
    Tabloda olmayan yeni bir risk tipi → mantıksal çıkarımla etki belirle.

    RİSK → SEKTÖR ETKİ MATRİSİ (framework'te kalır, risk tipi dinamik):
    ┌─────────────────────┬──────────────────────────────────────────────┐
    │ Savaş / Jeopolitik  │ Havacılık ×0.6, Turizm ×0.7, Savunma ×1.3 │
    │                     │ Denizcilik ±, Enerji üretici ×1.2          │
    │                     │ İç pazar sanayi ×1.0 (nötr)                │
    ├─────────────────────┼──────────────────────────────────────────────┤
    │ Petrol/Enerji Krizi │ Enerji tüketici ×0.8, Ulaştırma ×0.7      │
    │                     │ Enerji üretici ×1.3, Defansif ×1.0         │
    ├─────────────────────┼──────────────────────────────────────────────┤
    │ Kur Krizi           │ İhracatçı ×1.2, İthalatçı ×0.7            │
    │                     │ Döviz borçlu ×0.7, TL gelirli ×0.9        │
    ├─────────────────────┼──────────────────────────────────────────────┤
    │ Faiz Şoku           │ Tüm çarpanlar ×0.9, GYO ×0.7              │
    │                     │ Banka (marj) ×1.1, Borçlu ×0.8             │
    ├─────────────────────┼──────────────────────────────────────────────┤
    │ Doğal Afet          │ İnşaat ×1.2, Sigorta ×0.7                  │
    │                     │ Yerel sanayi ×0.8, Çimento ×1.2            │
    ├─────────────────────┼──────────────────────────────────────────────┤
    │ Pandemi / Salgın    │ Sağlık ×1.3, Turizm ×0.5, Perakende ×0.7  │
    │                     │ E-ticaret/Bilişim ×1.2, Ulaştırma ×0.6     │
    ├─────────────────────┼──────────────────────────────────────────────┤
    │ Seçim / Politik     │ Tüm sektör volatilite ↑, çarpan ×0.95     │
    │                     │ Kamu ihaleci (inşaat/savunma) ×0.9         │
    ├─────────────────────┼──────────────────────────────────────────────┤
    │ Küresel Resesyon    │ Döngüsel ×0.7, Defansif ×1.1               │
    │                     │ İhracatçı ×0.8, İç talep ×0.9             │
    ├─────────────────────┼──────────────────────────────────────────────┤
    │ Düzenleme Değişikl. │ Hedef sektör ×0.7 veya ×1.3 (yöne göre)   │
    ├─────────────────────┼──────────────────────────────────────────────┤
    │ Risk yok / Stabil   │ Tüm sektör ×1.0 (çarpan uygulanmaz)       │
    └─────────────────────┴──────────────────────────────────────────────┘

    ŞİDDET KADEMESİ (tablo çarpanlarını ölçekle):
    Düşük (haberlerde var ama piyasa sakin) → çarpanı %50 uygula
    Orta (piyasa etkileniyor)              → çarpanı %100 uygula
    Yüksek (kriz/savaş aktif)              → çarpanı %150 uygula
    
    Örnek: İran savaşı AKTİF (yüksek) → Havacılık çarpanı ×0.6
           Havacılık skor = 78p × 0.6 = 47p (🏆 ALTIN → 🟠 TAVSİYE)
    
    Örnek: Kur krizi ORTA → İhracatçı çarpanı ×1.2, İthalatçı ×0.7
    
    ★ Birden fazla risk aynı anda aktif olabilir → çarpanlar ÇARPILIR
      İran savaşı + petrol krizi → Havacılık: ×0.6 × ×0.7 = ×0.42
    
    ★ Risk "stabil" ise Faz 3.5 atlanır, çarpan ×1.0

    Makro düzeltilmiş skor = Faz 3 final skoru × Sektörel etki çarpanı
```

### FAZ 4: HEDEF FİYAT HESAPLAMA (Adım 18-22) — ★ ASIL ÇIKTI
```
18. Her geçen hisse için 5 YÖNTEM hedef fiyat hesapla:
    - Y1: Referans F/K × TTM NK / Hisse Adedi
    - Y2: Sektör Adil F/K × Forward NK / Hisse Adedi
    - Y3: 3Y Ort PD/DD × Özkaynak / Hisse Adedi
    - Y4: Broker hedef fiyat ortalaması (varsa)
    - Y5: Faal.Kâr × Sektör Adil F/K / Hisse Adedi
    
19. Ağırlıklı Hedef Fiyat = Σ(Yöntem × Ağırlık) / Σ(Ağırlıklar)
    - R13 aktif → Y1 ağırlığı %25 → %10'a düşür
    - Broker ≥3 → Y4 ağırlığı %30 (güvenilir)
    - GYO/Holding → Y3 ağırlığı +%10 (NAV birincil)
    - R17 sözleşme → Y5'e bonus ekle
    
20. Makro Düzeltme = Ağırlıklı Hedef × Faz 3.5 Makro Çarpanı
21. Gerçekleşme Düzeltme = Makro Hedef × Gerçekleşme Oranı
    (katalist durumuna göre: T1 %85, T2 %70, yok %40)
22. Potansiyel % = (Final Hedef / Son Fiyat - 1) × 100
    → Sırala, sinyal ata, CSV + GitHub push
```

### HER HİSSE ÇIKTI FORMATI (Hedef Fiyat Bazlı)
```
═══════════════════════════════════════════════════════════════
📌 {KOD} — {ŞİRKET}  [{Sektör}]
{🏆 ALTIN FIRSAT / 🟢 GÜÇLÜ AL / 🟡 AL / 🟠 TUT}
═══════════════════════════════════════════════════════════════
💰 Son Fiyat: ₺X → HEDEF: ₺Y → POTANSİYEL: +%Z
   Y1 Mean Rev: ₺A | Y2 Forward: ₺B | Y3 PD/DD: ₺C
   Y4 Broker: ₺D (N analist) | Y5 Core: ₺E
🔍 Kalite: {✅/⚠️} | Makro: ×M.M | Gerçekleşme: %G
📰 Katalist: {T1/T2/R17/Yok}
═══════════════════════════════════════════════════════════════
```

### SİNYAL SİSTEMİ (FAİZ BAZLI — Yukarıdaki ile aynı)
```
Min AL = TCMB Faizi + %15 Risk Primi
🏆 ALTIN FIRSAT  → Pot > Min AL×1.5 + T1/T2 Katalist
🟢 GÜÇLÜ AL      → Pot > Min AL + Katalist VEYA > Min AL×1.5
🟡 AL            → Pot > Min AL (mevduattan iyi)
🟠 TUT           → Pot %30 - Min AL
⚪ İZLE          → Pot %0-%30 (mevduat daha iyi)
🔴 SAT           → Pot < %0
```

### BATCH OPTİMİZASYONU
```
Faz 1: 6 MCP sorgusu (Sorgu 14, 100'erli batch)
Faz 2: Hesaplama (MCP çağrısı yok)
Faz 3: 
  - 2 SQL sorgusu (broker tahmin + hedef fiyat, toplu)
  - ~15-20 dokumanlarda_ara çağrısı (top 20 hisse KAP haberleri)
  - ~5-10 web_search (sektör bazlı haber taraması)
Faz 3.5:
  - 2-3 web_search (güncel makro risk tespiti)
  - Hesaplama: sektörel etki çarpanı uygula
Faz 4: 5 Yöntem Hedef Fiyat + Potansiyel % → CSV + GitHub push
Toplam: ~30-35 MCP/tool çağrısı
```

---

## REFERANS DOSYALARI (Progressive Disclosure)

Bu skill'in detaylı alt dokümanları:

| Dosya | İçerik | Ne Zaman Oku |
|-------|--------|--------------|
| `references/sql-sorgulari.md` | 13+ SQL şablonu (1-13 + 11b/11c) | Veri çekmeden önce |
| `references/backtest-bulgular.md` | 3 dönem backtest + GYO/Holding 6Q + vakalar | Sonuçları yorumlarken |
| `references/sektor-detay.md` | Sektör çarpanları, mevsimsellik | Sektör bazlı hesaplama |
| `references/haber-katalist-avcisi.md` | Katalist Avcısı v2 tam metodoloji | Haber taraması yaparken |
| `references/prompt-kullanim.md` | Kullanım örnekleri, opsiyonel modlar | Kullanıcı talimatlarında |
| `scripts/pipeline_v24.py` | Deterministik Python pipeline | Tam tarama çalıştırırken |

---

## DETERMİNİSTİK PİPELİNE (v2.6 Entegre — Hedef Fiyat Bazlı)

```
Faz 1: MCP SQL → finansal ham data (6 batch)
Faz 2: Python → kâr kalitesi eleme (~60 hisse geçer)
Faz 3: MCP → broker tahmin + KAP haber + katalist (~25 çağrı)
Faz 3.5: web_search → makro risk tespiti + sektörel çarpan
Faz 4: Python → 5 yöntem hedef fiyat + potansiyel % + CSV → GitHub push
```

### "Son bilançoları değerle" akışı (İncremental):
1. Son tarama tarihinden sonra yayınlanan bilançoları tespit et
2. Sadece yeni hisseleri Faz 1-4 tam pipeline'dan geçir
3. Mevcut CSV'ye ekle/güncelle → GitHub push

### Tam tarama akışı:
1. Sorgu 14 CTE (6 batch) → ~574 hisse
2. Ön filtre (NK>0, FAVÖK>0, F/K iskontolu) → ~93 hisse
3. Kâr kalitesi eleme (Rule 9/10) → ~60 hisse
4. Broker tahminleri (toplu SQL) → broker hedef fiyat + konsensüs NK
5. KAP haberleri (top 20-30 hisse) → katalist sınıflandırma + R17 sözleşme
6. Makro risk taraması (web_search) → güncel risk tespiti
7. **5 Yöntem Hedef Fiyat Hesaplama (Y1-Y5)**
8. Makro çarpan uygula → makro düzeltilmiş hedef
9. Gerçekleşme oranı uygula → final hedef fiyat
10. Potansiyel % hesapla → sırala → sinyal ata → CSV + GitHub push

---

## PİYASA FAZI BAZLI STRATEJİ (3 Dönem Doğrulanmış)

```
SÜPER BOĞA (XU100 > +30%):
  Faz 1-2 tek başına güçlü (α+37.1%)
  Faz 3 katalist ekstra bonus verir (α+68.4%)
  Evren dar olabilir (düşük faiz → çoğu hisse primli)
  Strateji: Geniş tutarak Faz 1-2 yeterli

BOĞA (XU100 +5% → +30%):
  Faz 1-2 orta düzey (TOP15 α+21.6%)
  Faz 3 kritik fark yaratır (katalistli α+88.4%)
  Strateji: Faz 3 ile katalistli hisselere odaklan

AYI (XU100 < +5%):
  Faz 1-2 TEK BAŞINA ÇALIŞMIYOR (α-1.9%) ❌
  Faz 3 ZORUNLU (katalistli α+39.6%, katalistsiz α-6.8%)
  Strateji: SADECE katalistli hisseler alınır, katalistsiz→izle

★ FAZ 3 HER ZAMAN YAPILIR — piyasa fazı ne olursa olsun.
  AYI'da Faz 3 olmadan tarama geçersizdir.
```
