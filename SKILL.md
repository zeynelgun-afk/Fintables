---
name: bilanco-sonrasi-ucuzlama-tarayicisi
description: >
  BIST hisseleri için entegrik değerleme ve hedef fiyat sistemi. Fintables MCP ile gerçek veri.
  5 Yöntem ağırlıklı hedef fiyat + faiz bazlı dinamik sinyal eşikleri + trend düzeltme +
  kâr sürprizi + PEG + momentum + katalist + makro risk overlay.
  Tetikleyiciler: "bilanço tarama", "BIST tarama", "ucuz hisse", "hedef fiyat hesapla",
  "forward F/K", "değerleme", "katalist tarama", "pipeline tarama", "son bilançoları değerle".
---

# BIST Entegrik Değerleme Sistemi v7
## 5 Yöntem Hedef Fiyat + Faiz Bazlı Sinyal

> **TEMEL İLKE:** Amaç para kazanmak. Puan vermek değil, "olması gereken fiyat" hesaplamak.
> Her hisse için: Son Fiyat → 5 Yöntem Hedef Fiyat → % Potansiyel → Mevduattan iyi mi?
>
> **3 DÖNEM BACKTEST:** Katalistli α+65.5%, Katalistsiz α+5.5%. Fark +59.9pt. ADIM 5 ZORUNLU.

---

## ADIM 0: FAİZ — HER ŞEYİN TEMELİ

Her tarama faizi çekerek başlar. İKİ FARKLI FAİZ kullanılır:

1. **Mevcut TCMB Faizi** → Min AL eşiği (mevduat alternatifi)
2. **Forward Faiz (yılsonu konsensüs)** → Adil F/K hesabı + faiz tavanı

Mantık: Piyasa forward'a bakarak fiyatlıyor, ama mevduat bugünkü faizi veriyor.

```
web_search: "TCMB politika faizi güncel"
web_search: "Türkiye yılsonu faiz beklentisi konsensüs"

Adil F/K = 1 / (Forward Faiz × 0.70 + %5 Risk Primi)
  ★ Forward faiz kullanılır — piyasa yılsonu beklentisiyle fiyatlıyor.
  ★ Faiz eğilimi çarpanı KALDIRILDI (forward zaten eğilimi yansıtıyor).

Sektör Adil F/K = Adil F/K × Sektör Çarpanı:
  Sanayi 1.00 | Teknoloji/Savunma 1.875 | Bankacılık 0.50 (F/DD birincil)
  Enerji 0.75 | İnşaat 0.625 | Telekom 0.875 | Sigorta/Maden 0.75
  Perakende/Turizm/Gıda/Tarım 1.00 | GYO/Holding → NAV (çarpan yok)

Min AL Eşiği = Mevcut TCMB Faizi + %15 Risk Primi
  ★ Mevcut faiz kullanılır — mevduat bugün bu kadar veriyor.

Örnek: TCMB %37 mevcut, konsensüs %30 forward
  → Adil F/K = 1/(0.30×0.70+0.05) = 3.85x
  → Min AL = %37 + %15 = %52
  → Sanayi Adil = 3.85x | Teknoloji Adil = 7.22x
```

---

## ADIM 1: FİNTABLES MCP VERİ ÇEKME

```
1. finansal_beceri_yukle → şema bilgisi (HER OTURUMDA ZORUNLU)
2. veri_sorgula → Sorgu 14 CTE (6 batch × 100 hisse)
   Zorunlu kalemler: NK TTM, NK Q4, FAVÖK, Faaliyet Kârı,
   İştirak Kâr Payı, Yatırım Geliri, Ciro TTM
   + 3Y tarihsel çarpanlar (ort F/K, PD/DD, fk_veri_sayisi)
   + Sektör ort F/K
   + Son fiyat, ödenmiş sermaye, özkaynak
3. 4 çeyrek ciro + NK verisi (trend tespiti için)
4. Geçen yıl aynı çeyrek NK (YoY kâr sürprizi için)
5. İşletme NA (nakit akış tablosu) → Rule 19 nakit dönüşüm kalitesi için
   İşletme NA / FAVÖK oranı hesaplanır
```

→ Çıktı: ~574 hisse ham veri

---

## ADIM 2: ELEME (Geç / Geçme)

Eleme kuralları — geçemezse hedef fiyat HESAPLANMAZ:

```
HARD ELEN:
  NK TTM ≤ 0 veya FAVÖK ≤ 0
  Rule 9:  Faal.Kâr < 0 + NK > 0 (standart şirket — operasyonel güç yok)
  Rule 10: İştirak Kâr Payı / NK > %80 (kâr tamamen iştirakten)
  F/K primli: mevcut F/K > referans F/K (yükselme potansiyeli yok)

UYARI (elen değil, hedef fiyatta yansır):
  Rule 12: Faal.Kâr / NK < %30 → R17 yoksa Y5 ağırlık artır | R17 varsa kaydırma YOK
  Rule 13: fk_veri_sayisi / 750 < %50 → Y1 ağırlık düşür (fark aktarılmaz, normalize)
  Rule 14: Yatırım Geliri / Ciro > %50 → Y1/Y2'de Forward NK yerine Faal.Kâr bazlı NK kullan
           > %30 → uyarı (raporda belirt, ağırlık kaydırma OPSİYONEL)
  Rule 16: Q4 NK / TTM NK > %70 veya < %10 → TTM NK kullan, forward güvenilmez
  Rule 17: Garantili sözleşme → Y5'e bonus çarpan
  Rule 19: İşletme NA / FAVÖK < 0.3 → gerçekleşme -%15 (nakit dönüşüm kötü)
           İşletme NA / FAVÖK > 0.7 → gerçekleşme +%5 (nakit dönüşüm güçlü)
           ★ Backtest: >0.7 → +18.4% getiri, <0.3 → +2.1% getiri (neredeyse sıfır!)
           ★ ORGE vakası: Kâr yüksek ama nakit dönüşüm 0.22 → gerçek operasyonel güç yok
  Rule 20: Garantili sözleşme > 2Y → sözleşme ömrü ort faiz ile Adil F/K hesapla
           Y1 faiz tavanı + Y2'de Sözleşme Adil F/K kullan (bugünkü forward yerine)
           Y3 değişmez (varlık bazlı). Y5 tavanlı kısmı etkilenir (daha yüksek Adil → daha yüksek tavan).
           CATES vakası: 4Y sözleşme → ort faiz %20 → Adil 5.31x → Enerji 3.98x
```

→ Çıktı: ~60-90 hisse (elemeyi geçen)

---

## ADIM 3: MEVSİMSELLİK + TREND TESPİTİ (Rule 18)

Önce sektörün mevsimsellik kategorisini belirle (aşağıdaki MEVSIMSELLIK KARARI bölümüne bak),
sonra trend tespit et ve Forward NK'yı seç.

Son 4 çeyrekte ciro ve NK trendini tespit et:

```
ARTIŞ:  Son 3Q'da son/ilk > 1.15 → ×1.10
SABİT:  Belirgin yön yok           → ×1.00
DÜŞÜŞ:  Son 3Q'da son/ilk < 0.75  → ×0.70
SPIKE:  Bir Q diğerlerinin 2.5x'i → ×0.75

Trend Çarpanı = ortalama(ciro_trend, nk_trend)

ATATP vakası: Ciro 2620→1331→1140 (düşüş) + NK 1089→503→341 (spike)
→ Trend çarpanı = (0.70 + 0.75) / 2 = 0.72
```

### Forward NK Seçimi (Trend bazlı)

```
ARTIŞ  → Son Q × 4 (büyüme devam edecek)
SABİT  → TTM NK (mevcut seviye sürecek)
DÜŞÜŞ  → Son 2Q Ortalaması × 4 (düşüş yansısın)
SPIKE  → Spike Hariç Medyan × 4 (tek seferlik çıkar)

ATATP: Spike → medyan(121, 503, 341) = 341 → 341×4 = 1364M
       (TTM 2054M yerine — %33 düşüş!)
```

---

## ADIM 4: KÂR SÜRPRİZİ → Forward NK Büyüme Çarpanı

Q4 2025 vs Q4 2024 (YoY) karşılaştır:

```
YoY > +%100  → Forward NK × 1.08 (güçlü büyüme devam beklentisi)
YoY > +%30   → Forward NK × 1.05
YoY < -%30   → Forward NK × 0.95

OPSİYONEL (veri varsa):
  QoQ > +%50   → Forward NK × 1.05 (ek bonus)
  QoQ < -%30   → Forward NK × 0.97
  Çift pozitif (YoY+ ve QoQ+) → en güçlü sinyal
```

---

## ADIM 5: KATALİST + BROKER (★ ZORUNLU, ASLA ATLANMAZ)

> **Backtest kanıtı:** Katalist olmadan AYI'da α=-1.9%. Katalist ile α=+39.6%.
> Katalist farkı 3 dönem ort +59.9pt. Bu adım atlanırsa tarama GEÇERSİZ.

### 5a: Broker Tahminleri (Toplu SQL)

```sql
-- Konsensüs NK + hedef fiyat çek
SELECT hisse_senedi_kodu, yil,
  AVG(net_kar) AS kons_nk, COUNT(DISTINCT araci_kurum_kodu) AS analist
FROM hisse_senedi_araci_kurum_tahminleri
WHERE yil IN (2025, 2026) AND ay = 12
GROUP BY hisse_senedi_kodu, yil

-- Hedef fiyatlar
SELECT hisse_senedi_kodu, AVG(hedef_fiyat) AS ort_hedef, COUNT(*) AS rapor
FROM hisse_senedi_araci_kurum_hedef_fiyatlari
WHERE yayin_tarihi_europe_istanbul >= '{6_AY_ONCE}' AND hedef_fiyat > 0
GROUP BY hisse_senedi_kodu
```

### 5b: KAP Haberleri (Her hisse için dokumanlarda_ara)

```
Top 20-25 hisse için:
  dokumanlarda_ara(
    query="sözleşme sipariş yatırım kapasite ihale tesis satın alma",
    filter='dokuman_tipi = "kap_haberi" AND kap_bildirim_tipi = "ODA"
      AND iliskili_semboller = "{KOD}"
      AND yayinlanma_tarihi_utc > {6_AY_ONCE_UTC}',
    sirala="yayinlanma_tarihi_utc:desc", sayfa_basi=5
  )
  İlginç haber → dokuman_chunk_yukle ile detay oku

Katalist sınıflandırma:
  Tier 1: Yeni sipariş/ihale kazanma/tesis devreye/satın alma → ger %85
  Tier 2: Kapasite artışı yatırımı/patent/lisans → ger %70
  Tier 3: Temettü/geri alım/ESG → düşük etki
  Stacking: 2+ farklı katalist → ek güç (FONET: 5 ihale = T1+Stack)
```

### 5c: Katalist → Forward NK Çarpanı + Gerçekleşme (ADIM 8'de kullanılır)

```
★ YENİ (v7.4): Katalist Forward NK'yı DEĞİŞTİRİR.
  Backtest kanıtı: Katalist farkı +59.9pt ama eski sistemde sadece gerçekleşmeye giriyordu.
  Artık katalist HEM Forward NK'yı HEM gerçekleşmeyi etkiler.

FORWARD NK ÇARPANI (Y1 ve Y2'deki fwd_nk'ya uygulanır — Y5'e GİRMEZ):
  T1 Katalist → Forward NK × 1.50 (varsayılan %50 kâr artışı beklentisi)
  T2 Katalist → Forward NK × 1.10 (varsayılan %10)
  Katalist yok → Forward NK × 1.00 (değişmez)

  Özel durumlar (sipariş/ciro oranı biliniyorsa):
    Sipariş/Ciro > %50 → Forward NK × 1.50 (TRANSFORMATÖR — varsayılanla aynı)
    Sipariş/Ciro %20-50 → Forward NK × 1.40
    Sipariş/Ciro %10-20 → Forward NK × 1.30
    Sipariş/Ciro < %10  → Forward NK × 1.20

  R17 (garantili sözleşme) ile ÇAKIŞMAZ:
    R17 zaten Y5'e ×2.5 veriyor — Forward NK çarpanı Y1/Y2'ye girer, Y5'e girmez.

GERÇEKLEŞMEYİ de belirler (ADIM 8'de):
  T1 bulundu → baz gerçekleşme %85
  T2 bulundu → baz gerçekleşme %70
  Hiçbiri    → baz gerçekleşme %40
```

---

## ADIM 6: 5 YÖNTEM HEDEF FİYAT

Her yöntem bağımsız bir hedef fiyat üretir. Ağırlıklı ortalaması alınır.

### Y1: Mean Reversion F/K

```
Hedef PD = Referans F/K × Forward NK (trend+sürpriz düzeltilmiş)
Hedef Fiyat = Hedef PD / Hisse Adedi

Referans F/K = min(3Y Kendi Ort, Sektör Ort × 1.5)  ← Rule 15

★ FAİZ TAVANI (v6): Referans F/K = min(Referans, Sektör Adil F/K × 2.0)
  Forward %30 → Sanayi max 7.70x, Teknoloji max 14.44x
  Bu tavan düşük faiz dönemindeki 30-50x çarpanların referans alınmasını engeller

★ Rule 13: fk_veri_sayisi / 750 < %50 → Y1 ağırlık %10'a düşür (fark aktarılmaz)
```

### Y2: Forward F/K (Sektör Adil Bazlı)

```
Hedef PD = Sektör Adil F/K × Forward NK
Hedef Fiyat = Hedef PD / Hisse Adedi

Sektör Adil F/K doğrudan forward faize bağlı:
  Forward %30 → Sanayi 3.85x | Teknoloji 7.22x | Banka 1.93x
  Faiz beklentisi düşerse adil F/K yükselir → hedef fiyat otomatik artar
```

### Y3: PD/DD Reversion

```
Hedef PD = Referans PD/DD × Ana Ortaklık Özkaynağı
Hedef Fiyat = Hedef PD / Hisse Adedi

STANDART ŞİRKET:
  ★ FAİZ TAVANI: Referans PD/DD = min(3Y Ort, max(Sektör Adil × 0.4, 2.0))
    Örnek: Sanayi 3.85 × 0.4 = 1.54 → max(1.54, 2.0) = 2.0 → min(3Y Ort, 2.0)

GYO (FAİZ BAZLI PD/DD TAVANI):
  ★ Referans PD/DD = min(3Y Ort, 1 / (Forward Faiz × 3))
    @%30 fwd: 1/(0.30×3) = 1.11x | @%15: 2.22x | @%8: 4.17x
    Faiz yüksek → tavan düşer | Faiz düşük → tavan kalkar (OTOMATİK)
    
    Etki:
    KZBGY: min(9.07, 1.11) = 1.11x ← düşük faiz dönemi şişirmesi engellendi
    SRVGY: min(1.13, 1.11) = 1.11x ← faiz tavanı aktif
    HLGYO: min(0.53, 1.11) = 0.53x ← 3Y ort düşük, tavan etkilemez
    AKFGY: min(0.58, 1.11) = 0.58x ← aynı

HOLDİNG (FAİZ BAZLI + KONGLOMERA İSKONTOSU):
  ★ Referans PD/DD = min(3Y Ort, 1 / (Forward Faiz × 3) × 0.85)
    Konglomera iskontosu %15 (global ortalama — yönetim karmaşıklığı, şeffaflık)
    @%30 fwd: 1.11 × 0.85 = 0.94x | @%15: 2.22 × 0.85 = 1.89x
    
    Etki:
    EUHOL: min(2.45, 0.94) = 0.94x ← tavan aktif
    GLRYH: min(2.79, 0.94) = 0.94x ← tavan aktif
    RALYH: min(9.63, 0.94) = 0.94x ← düşük faiz şişirmesi engellendi
  
  ★ Max potansiyel sınırı YOKTUR — faiz bazlı PD/DD tavanı + gerçekleşme yeterli.

GYO/Holding'de Y3 ağırlık +%10 (broker ≥3: %25, broker az/yok: %30)
Trend bağımsız — varlık bazlı değerleme
```

### Y4: Broker Hedef Fiyat

```
Son 6 ay aracı kurum hedef fiyatlarının ortalaması
≥ 3 analist → ağırlık %30 (güvenilir konsensüs)
1-2 analist → ağırlık %15
0 analist   → atlanır, diğerleri yeniden ağırlıklanır
```

### Y5: Core Earning Power

```
Hedef PD = (Faaliyet Kârı TTM × Trend Çarpanı) × Y5 Ref F/K
Hedef Fiyat = Hedef PD / Hisse Adedi

Y5 Ref F/K = (Sektör Ort F/K + min(Sektör Ort F/K, Sektör Adil F/K × 2.0)) / 2
  → "Piyasa ne diyor" + "Faiz ne diyor" ortası
  Faiz düşünce → tavan yükselir → ortalama sektör ortalamasına yaklaşır (OTOMATİK)
  Faiz yükselince → tavan düşer → ortalama daha muhafazakâr olur (OTOMATİK)
  Örnek @%30 forward: Enerji → (18.48 + min(18.48, 5.78)) / 2 = (18.48 + 5.78) / 2 = 12.13x

★ Y5 Ref F/K = (Sektör Ort + Faiz Tavanlı) / 2 — piyasa ile faiz dengesini yansıtır.
  Y2 zaten Adil F/K (teorik minimum) veriyor.
  Y5'in amacı: "Piyasa bu operasyonel güce ne değer veriyor?" + "Faiz ne diyor?"
  → İkisinin ortası: ne piyasa kadar iyimser ne faiz kadar kötümser.
★ Faal.Kâr < NK → sektör ort (NK bazlı) × Faal.Kâr = doğal muhafazakârlık.
★ Yatırım/finansal gelir DAHİL DEĞİL — saf operasyonel güç.
★ Trend çarpanı burada uygulanır (artış → kâr artacak, düşüş → azalacak).
★ Rule 17 sözleşme bonusu varsa: × 2.5 çarpan (CATES EÜAŞ gibi).
```

### Ağırlık Tablosu

```
                    Broker VAR (≥3)    Broker AZ (1-2)    Broker YOK
Y1 Mean Rev.            %25               %30              %30
Y2 Forward              %10               %10              %10
Y3 PD/DD                %15               %20              %20
Y4 Broker               %30               %15               -
Y5 Core                 %20               %25              %25

★ Y2 düşük ağırlıklı: Adil F/K tamamen teorik, piyasa gerçeğiyle uyuşmuyor.
  Piyasa hiçbir zaman Adil F/K'da (3-4x) işlem görmüyor.
  Y1 (tarihsel mean reversion) + Y5 (operasyonel kâr gücü) daha güvenilir.

Ek düzeltmeler:
  GYO/Holding → Y3 ağırlık +%10, Y1/Y2 -%5 (NAV birincil)
  GYO + PD/DD < 1 → Y3 ağırlık %50 (Y3 baskın — taban YOK)
  R13 aktif   → Y1 ağırlık %10'a düşür. Fark AKTARILMAZ — normalize yeterli.
                 (Güvenilmez Y1'den çıkan ağırlığı düşük Y5'e koymak paradoks yaratır.
                  Normalize ile Y3 ve Y5 otomatik oransal güçlenir.)
  R12 aktif   → SADECE R17 yoksa: Y1 -%5, Y5 +%5 (core'a daha çok bak).
                 R17 + R12 birlikte aktifse: R12 ağırlık kaydırma YAPMA.
                 (R17 zaten Faal.Kâr'ın artacağını söylüyor — eski düşük core'a
                  daha çok ağırlık vermek anlamsız. CATES vakası.)

★ Ağırlıklar normalize edilir: Hedef = Σ(Yöntem×Ağırlık) / Σ(Ağırlıklar)
  Broker yoksa toplam düşer, otomatik %100'e normalize edilir.

★ ROL DAĞILIMI (her yöntem farklı soruya cevap verir):
  Y1: Tarihsel ortalamaya dönüş (faiz tavanlı)  → "Geçmişte neredeydi?"
  Y2: Teorik adil değer (forward faiz bazlı)     → "Olması gereken minimum"
  Y3: Varlık değeri (PD/DD)                      → "Tasfiye edilse ne eder?"
  Y4: Broker konsensüsü                          → "Analistler ne diyor?"
  Y5: Piyasa çarpanı × operasyonel güç           → "Piyasa ne diyor?"
```

---

## ADIM 7: MAKRO RİSK OVERLAY

```
web_search: "BIST risk bu hafta"
web_search: "Türkiye ekonomi gündem"

Tespit edilen risk → sektörel etki çarpanı:
┌─────────────────────┬──────────────────────────────────────────────┐
│ Savaş / Jeopolitik  │ Havacılık ×0.6, Turizm ×0.7, Savunma ×1.3 │
│ Petrol/Enerji Krizi │ Enerji tüketici ×0.8, Üretici ×1.3         │
│ Kur Krizi           │ İhracatçı ×1.2, İthalatçı ×0.7             │
│ Faiz Şoku           │ Tüm ×0.9, GYO ×0.7, Banka ×1.1            │
│ Risk yok / Stabil   │ Tüm ×1.0 (çarpan uygulanmaz)              │
└─────────────────────┴──────────────────────────────────────────────┘

Şiddet: Düşük → çarpanı %50 | Orta → %100 | Yüksek → %150
Makro Düzeltilmiş Hedef = Ham Hedef × Makro Çarpanı
```

---

## ADIM 8: GERÇEKLEŞME ORANI (Katalist bilgisi ADIM 5'ten gelir)

Backtest'ten öğrenilen: hedef fiyata ulaşma olasılığı.
Upside'a uygulanır (tüm değere DEĞİL).

```
Final Hedef = Son Fiyat + (Makro Düz. Hedef - Son Fiyat) × Gerçekleşme

BAZ ORANLAR (katalist durumuna göre — ADIM 5'te tespit edilmiş):
  T1 Katalist:    %85 (3 dönem ort — en güvenilir)
  T2 Katalist:    %70
  Broker ≥2 analist (kat yok): %60 (analist güvencesi)
  Katalistsiz (broker da yok): %40 (mevduata yatır daha iyi olabilir)
  GYO çift ucuz:  %55 | GYO tekli: %15 (backtest: tekli ucuz ort -10.5% getiri!)
  Holding T1 katalist: %50 | Holding T2: %35 | Holding yok: %20

MOMENTUM DÜZELTMESİ (4 çeyrek NK trendi):
  4Q ardışık artış  → ger +%10 (büyüyen şirket hedefe ulaşır)
  3Q ardışık düşüş → ger -%10 (küçülen şirket ulaşamaz)

PEG DÜZELTMESİ (OPSİYONEL — broker büyüme tahmini varsa):
  PEG < 0.5 → ger +%8 (çok ucuz büyüme — gerçekleşme yüksek)
  PEG < 1.0 → ger +%5
  PEG > 2.0 → ger -%3 (pahalı büyüme)

TURNAROUND BONUSU:
  GY Q4 zarar + Bu yıl Q4 kâr → ger +%5

NAKİT DÖNÜŞÜM KALİTESİ (Rule 19 — Backtest Bulgu #15):
  İşletme NA / FAVÖK > 0.7 → ger +%5 (nakit makinesi — kâr gerçek)
  İşletme NA / FAVÖK < 0.3 → ger -%15 (kâğıt üstünde kâr — nakit yok)
  ★ Backtest: >0.7 grubun ort getirisi +18.4%, <0.3 grubun ort +2.1%
  ★ ORGE vakası: 0.22 → kâr yüksek ama gerçek operasyonel güç yok

GÜVENLİK MARJI:
  PD/DD < 1.0 → ger +%5 (downside koruması var)
  ★ Taban fiyat YOKTUR — ne standart ne GYO ne Holding'de.
    GYO'lar yapısal NAV iskontosunda işlem görür (HLGYO 3Y ort 0.53x, hiç 1.0'a ulaşmamış).
    Defter değerine taban koymak gerçekçi değil.
    Y3 zaten 3Y ort PD/DD referans alıyor — bu gerçekçi hedef.

MAX POTANSİYEL SINIRI:
  Standart: max %200 (güvenlik önlemi — aşırı iyimser hedef engeli)
  GYO/Holding: MAX CAP YOK — faiz bazlı PD/DD tavanı (1/(FF×3)) otomatik sınırlama yapar.
    GYO: 1/(Forward Faiz × 3) | Holding: aynı × 0.85 (konglomera iskontosu)
    + düşük gerçekleşme oranları (%15-55) zaten potansiyeli doğal sınırlar.
```

---

## ADIM 9: FİNAL HESAPLAMA + SİNYAL

```
1. Ham Hedef = Σ(Yöntem × Ağırlık) / Σ(Ağırlıklar)
2. Makro Hedef = Ham Hedef × Makro Çarpanı
3. Upside = Makro Hedef - Son Fiyat
4. if Upside ≥ 0: Final Hedef = Son Fiyat + Upside × Gerçekleşme
   if Upside < 0: Final Hedef = Makro Hedef (gerçekleşme UYGULANMAZ)
   ★ Negatif upside = hisse pahalı. Gerçekleşme artınca düşüş artmamalı.
5. Taban: YOK (hiçbir kategoride defter değeri taban uygulanmaz)
   GYO yapısal iskontoda işlem görür — PD/DD 1.0'a dönme varsayımı yanlış.
6. Max: Standart %200 | GYO/Holding: max cap YOK (faiz bazlı PD/DD tavanı yeterli)
7. Potansiyel % = (Final Hedef / Son Fiyat - 1) × 100
```

### Sinyal Sistemi (FAİZ BAZLI — Dinamik Eşikler)

```
Min AL = TCMB Faizi + %15 Risk Primi
Mevduattan iyi performans gösteremeyen hisseye AL DENMEZ.

%37 faiz → Min AL = %52 | %25 faiz → Min AL = %40 | %15 faiz → Min AL = %30

🏆 ALTIN FIRSAT  → Pot > Min AL×1.5 + T1/T2 Katalist
                   Hem çok ucuz hem somut haber — HEMEN AL
                   T1 ger %85+, T2 ger %60-70. Backtest 3/3 dönem pozitif

🟢 GÜÇLÜ AL      → Pot > Min AL + Katalist VEYA Pot > Min AL×1.5
                   Mevduattan çok iyi — AL
                   Katalistli: güvenilir | Katalistsiz: çok ucuz ama risk var

🟡 AL            → Pot > Min AL
                   Mevduattan iyi (%52+ @%37 faiz) — riske değer

🟠 TUT           → Pot %30 — Min AL
                   Mevduata yakın — mevcut varsa tut, yeni alma

⚪ İZLE          → Pot %0-%30
                   Mevduat daha iyi — hisse almaya değmez

🔴 SAT           → Pot < %0

Faiz düşünce Min AL düşer → daha çok hisse AL sinyali alır (otomatik)

★ GERÇEKLEŞME FİLTRESİ (sinyal sonrası — son kontrol):
  Ger < %40 → LİSTEDEN TAMAMEN ELEN (gösterilmez)
    Backtest: %20 (holding katalistsiz), %15 (GYO tekli ucuz) → neredeyse hiç çalışmadı.
    Para kaybetme riski yüksek — mevduata yatır.
  Ger %40-%59 → max sinyal 🟠 TUT (AL/GÜÇLÜ/ALTIN veremezsin)
    Backtest: %40-55 bazen sürpriz yapıyor ama güvenilir değil.
    "İlginç ama risk yüksek" — mevcut varsa tut, yeni pozisyon açma.
  Ger ≥ %60 → sinyal kısıtlaması yok (normal akış)
```

---

## ÇIKTI FORMATI

### Her Hisse
```
═══════════════════════════════════════════════════════════════
📌 {KOD} — {ŞİRKET}  [{Sektör}]
{🏆 ALTIN / 🟢 GÜÇLÜ AL / 🟡 AL / 🟠 TUT / ⚪ İZLE / 🔴 SAT}
═══════════════════════════════════════════════════════════════
💰 Son: ₺X → Hedef: ₺Y → POTANSİYEL: +%Z (vs mevduat: +Npt)
   Y1 Mean Rev: ₺A (ref F/K Wx, tavan Vx)
   Y2 Forward:  ₺B (adil F/K Sx)
   Y3 PD/DD:    ₺C (ref Px)
   Y4 Broker:   ₺D (N analist)
   Y5 Core:     ₺E (sektör ort F/K: Qx, trend ×T)  ← piyasa çarpanı
🔍 Kalite: {✅/⚠️} | Trend: {C:artış N:düşüş ×0.85}
📰 Katalist: {T1/T2/Yok} | Gerçekleşme: %G
⚠️ Makro: {risk} ×M | PEG: P | Turnaround: {✅/—}
═══════════════════════════════════════════════════════════════
```

### Özet Tablo
```
# Kod    Son₺   Hedef₺   POT%  vsMevd  Y5₺    SekOrt  Ger  Sinyal     Katalist
1 XXXXX  XX.XX  YY.YY   +ZZ%  +NNpt   EE.EE  QQ.Qx   85%  🏆 ALTIN    T1 sipariş
```
★ Y5₺ ve SekOrt (Sektör Ort F/K) ayrıca gösterilir — piyasanın operasyonel
  güce verdiği değer ile teorik Adil F/K arasındaki farkı görünür kılar.

---

## KÂR KALİTESİ KURALLARI (Tam Liste)

```
Rule 9:  Faal.Kâr(-) + NK(+) → ELEN (standart). RTALB vakası.
Rule 10: İştirak/NK > %80 → ELEN | > %50 → uyarı. RTALB vakası.
Rule 12: Faal.Kâr/NK < %30 → R17 yoksa Y5 ağırlık artır | R17 varsa kaydırma YOK.
         R17 + R12 çakışma: sözleşme zaten core'u değiştirecek, eski Faal.Kâr'a
         daha çok ağırlık vermek anlamsız. CATES vakası.
Rule 13: fk_veri_sayisi/750 < %50 → Y1 ağırlık düşür. Fark aktarılmaz — normalize.
         Güvenilmez Y1'den çıkan ağırlığı düşük Y5'e koymak paradoks yaratır. GSDDE vakası.
Rule 14: Yat.Geliri/Ciro > %50 → hedef düşür | > %30 → uyarı. GSDDE vakası.
Rule 15: Ref F/K = min(3Y ort, sektör ort × 1.5). GSDDE vakası.
         "Adil × 1.5" KULLANILMAZ — Forward F/K yönteminde (Y2) zaten var.
Rule 16: Q4 NK/TTM NK > %70 veya < %10 → TTM NK kullan.
         ESCOM (%99), OYYAT (%91), TTKOM (%3) vakaları.
Rule 17: Garantili sözleşme → Y5'e × 2.5 çarpan. CATES EÜAŞ vakası.
Rule 18: Trend düzeltme → Forward NK seçimi + Y5 trend çarpanı. ATATP vakası.
Rule 19: İşletme NA/FAVÖK < 0.3 → ger -%15 | > 0.7 → ger +%5. ORGE vakası (0.22).
         Backtest: >0.7 → +18.4% getiri, <0.3 → +2.1%. Nakit dönüşüm kritik.
Rule 20: Garantili sözleşme > 2Y → sözleşme ömrü ortalama faiz ile Adil F/K hesapla.
         Y1 faiz tavanı + Y2'de Sözleşme Adil kullan. Y3 etkilenmez. Y5 tavanlı kısmı etkilenir.
         CATES: 4Y EÜAŞ → ort faiz %20 → Adil 5.31x → Enerji 3.98x (vs bugün 2.89x).
```

---

## KATMAN NAV — GYO/Holding/Banka

GYO/Holding/Banka için 5 Yöntem AYNI uygulanır ama:
- Y3 (PD/DD) ağırlığı %30'a çıkar (NAV birincil)
- GYO + PD/DD < 1 → Y3 ağırlık %50 (Y3 baskın — taban YOK)
- GYO Y3 Referans PD/DD = min(3Y Ort, 1 / (Forward Faiz × 3))
  Faiz bazlı tavan: @%30→1.11x, @%15→2.22x. Otomatik — faiz düşünce gevşer.
  KZBGY min(9.07, 1.11) = 1.11x | HLGYO min(0.53, 1.11) = 0.53x (değişmez)
- Holding Y3 Referans PD/DD = min(3Y Ort, 1 / (Forward Faiz × 3) × 0.85)
  Konglomera iskontosu %15. @%30→0.94x. Yapısal iskonto kalıcı.
- Çift filtre kontrolü yapılır (PD/DD isk + F/K isk = çift ucuz)
- Max potansiyel sınırı: GYO/Holding YOK — faiz PD/DD tavanı + gerçekleşme yeterli
- Kâr annualize etme (PEG hesaplanmaz)

```
ÇİFT UCUZ (PD/DD isk + F/K isk) → gerçekleşme %55 (GYO) / %50 (Holding T1) / %35 (Holding T2)
TEKLİ UCUZ (PD/DD isk + F/K primli) → gerçekleşme %15 (GYO) / %20 (Holding)
Backtest: Çift ucuz +6.6% ort | Tekli ucuz -10.5% ort → TEKLİ ÇOK RİSKLİ
Holding katalistsiz: %20 → Ger filtresiyle ELEN (backtest: ort alfa -3.6%)

Banka: F/DD %60 + F/K %40 | ROE > %20 → ger +%10
       Faiz indirimi trendi → %50-70 gerçekleşme
```

---

## MEVSIMSELLIK KARARI

```
DÜŞÜK (Sanayi, Banka, Telekom, Yazılım, Savunma, Gıda İşleme):
  Son Q × 4 güvenilir → doğrudan Forward NK olarak kullan

ORTA (Sigorta, Maden, İnşaat, Otomotiv):
  Son Q × 4 + YoY cross-check gerekli

YÜKSEK (Turizm, Enerji, Perakende giyim, Tarım):
  YoY BAZLI ZORUNLU: Geçen Yıl Aynı Q × (1 + YoY Büyüme) × 4

ÖZEL (Holding, GYO):
  Kâr annualize etme → NAV İskontosu birincil

★ Rule 16 (Q4 yoğunlaşma) mevsimsellikten SONRA çalışır.
  Mevsimsellik kuralı geçse bile Q4/TTM > %70 ise forward güvenilmez.
```

---

## TAM TARAMA AKIŞI (Pipeline)

```
ADIM 0: web_search → TCMB mevcut faizi + yılsonu konsensüs
ADIM 1: MCP SQL → finansal ham data (6 batch Sorgu 14 CTE)
         + 4Q ciro/NK trendi + GY Q4 NK (YoY)
         + son fiyat + sermaye + özkaynak + İşletme NA
ADIM 2: ELEME → Rule 9/10 + F/K primli → ~60-90 hisse geçer
ADIM 3: Mevsimsellik → Trend tespiti → Forward NK seçimi (Rule 18)
ADIM 4: Kâr sürprizi → Forward NK büyüme çarpanı
ADIM 5: Katalist + Broker (SQL + her hisse KAP taraması)
         ★ ZORUNLU — ASLA ATLANMAZ
         ★ Katalist Forward NK çarpanını belirler (T1=×1.50, T2=×1.10)
         ★ Hedef fiyat hesaplamasından ÖNCE yapılmalı
ADIM 6: 5 Yöntem Hedef Fiyat (Y1-Y5 + faiz tavanı + ağırlıklar)
         ★ Katalist çarpanlı Forward NK burada kullanılır
ADIM 7: Makro risk (web_search) → sektörel çarpan
ADIM 8: Gerçekleşme oranı (baz + momentum + PEG + nakit dönüşüm)
         ★ Katalist bilgisi ADIM 5'ten gelir → T1=%85, yok=%40
ADIM 9: Final hesaplama → Makro × Gerçekleşme → Potansiyel %
         → Faiz bazlı sinyal → CSV + GitHub push

"Son bilançoları değerle" = İncremental:
  Önceki tarama tarihinden sonra yayınlanan bilançoları tespit et,
  SADECE yeni hisseleri tam pipeline'dan geçir, mevcut CSV'ye ekle.
```

### MCP Çağrı Bütçesi
```
ADIM 1:  6 SQL (Sorgu 14 batch) + 2 SQL (trend + YoY) + 1 SQL (fiyat/sermaye/NA)
ADIM 5a: 2 SQL (broker tahmin + hedef fiyat)
ADIM 5b: ~20-25 dokumanlarda_ara (top hisseler KAP)
ADIM 7:  2-3 web_search (makro risk)
Toplam: ~35-40 MCP/tool çağrısı
```

---

## PİYASA FAZI BAZLI STRATEJİ (3 Dönem Doğrulanmış)

```
SÜPER BOĞA (XU100 > +30%):
  Finansal değerleme tek başına güçlü (α+37.1%)
  Katalist (ADIM 5) ekstra bonus (α+68.4%)
  Strateji: Geniş tut, finansal değerleme yeterli

BOĞA (XU100 +5% → +30%):
  Finansal değerleme orta (TOP15 α+21.6%)
  ADIM 5 katalist kritik fark (katalistli α+88.4%)
  Strateji: Katalistli hisselere odaklan

AYI (XU100 < +5%):
  Finansal değerleme TEK BAŞINA ÇALIŞMIYOR (α-1.9%) ❌
  ADIM 5 ZORUNLU (katalistli α+39.6%)
  Strateji: SADECE katalistli hisseler al, katalistsiz → mevduat
```

---

## REFERANS DOSYALARI

| Dosya | İçerik |
|-------|--------|
| `sql-sorgulari.md` | Sorgu 14 CTE + 15/16 broker + KAP şablonu |
| `backtest-bulgular.md` | 3 dönem backtest + GSDDE/CATES/RTALB vakaları |
| `sektor-detay.md` | Sektör çarpanları, mevsimsellik kuralları |
| `haber-katalist-avcisi.md` | Katalist Avcısı v2 tam metodoloji |
| `prompt-kullanim.md` | Kullanım örnekleri |

---

## TEMBELLİK YASAK

Tarama/analiz sırasında:
- Adım atlama, kısaltma, varsayımla geçiştirme YASAK
- Demo/sahte veri üretme YASAK
- ADIM 5 (katalist) atlamak YASAK — backtest kanıtı: +59.9pt fark
- Faiz kontrolü atlamak YASAK — mevduattan kötü hisseye AL demek YASAK
- Hesaplamayı yaklaşık yapma YASAK
- Her hisse tek tek taranır, her kural kontrol edilir
- Eksik veri varsa MCP'den çek — uydurma
