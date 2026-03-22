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
> **3 DÖNEM BACKTEST:** Katalistli α+65.5%, Katalistsiz α+5.5%. Fark +59.9pt. Faz 3 ZORUNLU.

---

## ADIM 0: FAİZ — HER ŞEYİN TEMELİ

Her tarama faizi çekerek başlar. Faiz 3 yerde kullanılır:
1. **Adil F/K hesabı** → Y2 ve Y5 hedef fiyat
2. **Faiz tavanı** → Y1 ve Y3'te 3Y çarpanları sınırlar
3. **Sinyal eşikleri** → mevduattan iyi mi testi

```
web_search: "TCMB politika faizi güncel"

Adil F/K = 1 / (TCMB Faizi × 0.70 + %5 Risk Primi)
Faiz Eğilimi: İNDİRİM → Adil × 1.20 | ARTIRIM → Adil × 0.90

Sektör Adil F/K = Adil F/K × Sektör Çarpanı:
  Sanayi 1.00 | Teknoloji/Savunma 1.875 | Bankacılık 0.50 (F/DD birincil)
  Enerji 0.75 | İnşaat 0.625 | Telekom 0.875 | Sigorta/Maden 0.75
  Perakende/Turizm/Gıda/Tarım 1.00 | GYO/Holding → NAV (çarpan yok)

Risksiz Getiri = TCMB Faizi (mevduat yaklaşık bu kadar verir)
Hisse Risk Primi = +%15
Min AL Eşiği = Risksiz + Risk Primi

Örnek: %37 faiz → Adil 3.88x → Sanayi Adil 3.88x → Min AL %52
        %25 faiz → Adil 5.00x → Sanayi Adil 5.00x → Min AL %40
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
  Rule 12: Faal.Kâr / NK < %30 → Y5 ağırlık artır (core earning power önemli)
  Rule 13: fk_veri_sayisi / 750 < %50 → Y1 ağırlık düşür (3Y ort güvenilmez)
  Rule 14: Yatırım Geliri / Ciro > %50 → Y1/Y2'de Forward NK yerine Faal.Kâr bazlı NK kullan
           > %30 → uyarı (Y1/Y2 ağırlık -%5, Y5 ağırlık +%5)
  Rule 16: Q4 NK / TTM NK > %70 veya < %10 → TTM NK kullan, forward güvenilmez
  Rule 17: Garantili sözleşme → Y5'e bonus çarpan
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

Q4 2025 vs Q4 2024 (YoY) ve Q4 vs Q3 (QoQ) karşılaştır:

```
YoY > +%100  → Forward NK × 1.08 (güçlü büyüme devam beklentisi)
YoY > +%30   → Forward NK × 1.05
YoY < -%30   → Forward NK × 0.95

QoQ > +%50   → Forward NK × 1.05 (ek bonus)
QoQ < -%30   → Forward NK × 0.97

Çift pozitif (YoY+ ve QoQ+) → en güçlü sinyal
```

---

## ADIM 5: 5 YÖNTEM HEDEF FİYAT

Her yöntem bağımsız bir hedef fiyat üretir. Ağırlıklı ortalaması alınır.

### Y1: Mean Reversion F/K

```
Hedef PD = Referans F/K × Forward NK (trend+sürpriz düzeltilmiş)
Hedef Fiyat = Hedef PD / Hisse Adedi

Referans F/K = min(3Y Kendi Ort, Sektör Ort × 1.5)  ← Rule 15

★ FAİZ TAVANI (v6): Referans F/K = min(Referans, Sektör Adil F/K × 2.0)
  %37 faiz → Sanayi max 7.76x, Teknoloji max 14.55x
  Bu tavan düşük faiz dönemindeki 30-50x çarpanların referans alınmasını engeller

★ Rule 13: fk_veri_sayisi / 750 < %50 → Y1 ağırlığı %25 → %10
```

### Y2: Forward F/K (Sektör Adil Bazlı)

```
Hedef PD = Sektör Adil F/K × Forward NK
Hedef Fiyat = Hedef PD / Hisse Adedi

Sektör Adil F/K doğrudan TCMB faizine bağlı:
  %37 faiz → Sanayi 3.88x | Teknoloji 7.28x | Banka 1.94x
  Faiz düşerse adil F/K yükselir → hedef fiyat otomatik artar
```

### Y3: PD/DD Reversion

```
Hedef PD = Referans PD/DD × Ana Ortaklık Özkaynağı
Hedef Fiyat = Hedef PD / Hisse Adedi

★ FAİZ TAVANI (v6): Referans PD/DD = min(3Y Ort, max(Sektör Adil × 0.4, 2.0))
  Örnek: Sanayi 3.88 × 0.4 = 1.55 → max(1.55, 2.0) = 2.0 → min(3Y Ort, 2.0)
  Düşük faiz dönemindeki 5-15x PD/DD çarpanları referans alınmaz

GYO/Holding'de ağırlık %30 (NAV birincil metrik)
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
Hedef PD = (Faaliyet Kârı TTM × Trend Çarpanı) × Sektör Adil F/K
Hedef Fiyat = Hedef PD / Hisse Adedi

★ Yatırım/finansal gelir DAHİL DEĞİL — saf operasyonel güç
★ Trend çarpanı burada uygulanır (artış → kâr artacak, düşüş → azalacak)
★ Rule 17 sözleşme bonusu varsa: × 2.5 çarpan (CATES EÜAŞ gibi)
★ Rule 12 aktif → Y5 ağırlığı artar (core önemli demek)
```

### Ağırlık Tablosu

```
                    Broker VAR (≥3)    Broker AZ (1-2)    Broker YOK
Y1 Mean Rev.            %20               %25              %25
Y2 Forward              %20               %25              %25
Y3 PD/DD                %15               %20              %20
Y4 Broker               %30               %15               -
Y5 Core                 %15               %15              %15

Ek düzeltmeler:
  GYO/Holding → Y3 ağırlık +%10, Y1/Y2 -%5 (NAV birincil)
  R13 aktif   → Y1 ağırlık %10'a düşür, farkı Y5'e aktar
  R12 aktif   → Y1 -%5, Y5 +%5 (core earning power önemli)

★ Ağırlıklar normalize edilir: Hedef = Σ(Yöntem×Ağırlık) / Σ(Ağırlıklar)
  Broker yoksa toplam %85 olur, otomatik %100'e normalize edilir.
```

---

## ADIM 6: KATALİST + BROKER (★ ZORUNLU, ASLA ATLANMAZ)

> **Backtest kanıtı:** Katalist olmadan AYI'da α=-1.9%. Katalist ile α=+39.6%.
> Katalist farkı 3 dönem ort +59.9pt. Bu adım atlanırsa tarama GEÇERSİZ.

### 6a: Broker Tahminleri (Toplu SQL)

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

### 6b: KAP Haberleri (Her hisse için dokumanlarda_ara)

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

### 6c: Katalist → Gerçekleşme oranını belirler (ADIM 8'de kullanılır)

```
T1 bulundu → baz gerçekleşme %85 (backtest: 21/22 isabet)
T2 bulundu → baz gerçekleşme %70
Hiçbiri    → baz gerçekleşme %40 (çoğu zaman mevduat daha iyi)
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

## ADIM 8: GERÇEKLEŞME ORANI (Katalist bilgisi ADIM 6'dan gelir)

Backtest'ten öğrenilen: hedef fiyata ulaşma olasılığı.
Upside'a uygulanır (tüm değere DEĞİL).

```
Final Hedef = Son Fiyat + (Makro Düz. Hedef - Son Fiyat) × Gerçekleşme

BAZ ORANLAR (katalist durumuna göre — ADIM 6'da tespit edilmiş):
  T1 Katalist:    %85 (3 dönem ort — en güvenilir)
  T2 Katalist:    %70
  Broker (kat yok): %60
  Katalistsiz:    %40 (mevduata yatır daha iyi olabilir)
  GYO çift ucuz:  %55 | GYO tekli: %35
  Holding katalist: %35 | Holding yok: %20

MOMENTUM DÜZELTMESİ (4 çeyrek NK trendi):
  4Q ardışık artış  → ger +%10 (büyüyen şirket hedefe ulaşır)
  3Q ardışık düşüş → ger -%10 (küçülen şirket ulaşamaz)

PEG DÜZELTMESİ:
  PEG < 0.5 → ger +%8 (çok ucuz büyüme — gerçekleşme yüksek)
  PEG < 1.0 → ger +%5
  PEG > 2.0 → ger -%3 (pahalı büyüme)

TURNAROUND BONUSU:
  GY Q4 zarar + Bu yıl Q4 kâr → ger +%5

GÜVENLİK MARJI:
  PD/DD < 1.0 → ger +%5 + taban fiyat = defter değeri
  (Düşse bile defter değerinin altına inmez)

MAX POTANSİYEL SINIRI (gerçekçilik):
  Standart: max %200 | GYO: max %150 | Holding: max %100
```

---

## ADIM 9: FİNAL HESAPLAMA + SİNYAL

```
1. Ham Hedef = Σ(Yöntem × Ağırlık) / Σ(Ağırlıklar)
2. Makro Hedef = Ham Hedef × Makro Çarpanı
3. Upside = Makro Hedef - Son Fiyat
4. Final Hedef = Son Fiyat + Upside × Gerçekleşme
5. Taban: PD/DD < 1 ise hedef en az = defter değeri
6. Max: Standart %200, GYO %150, Holding %100
7. Potansiyel % = (Final Hedef / Son Fiyat - 1) × 100
```

### Sinyal Sistemi (FAİZ BAZLI — Dinamik Eşikler)

```
Min AL = TCMB Faizi + %15 Risk Primi
Mevduattan iyi performans gösteremeyen hisseye AL DENMEZ.

%37 faiz → Min AL = %52 | %25 faiz → Min AL = %40 | %15 faiz → Min AL = %30

🏆 ALTIN FIRSAT  → Pot > Min AL×1.5 + T1/T2 Katalist
                   Hem çok ucuz hem somut haber — HEMEN AL
                   Gerçekleşme %85+, backtest 3/3 dönem pozitif

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
   Y5 Core:     ₺E (trend ×T)
🔍 Kalite: {✅/⚠️} | Trend: {C:artış N:düşüş ×0.85}
📰 Katalist: {T1/T2/Yok} | Gerçekleşme: %G
⚠️ Makro: {risk} ×M | PEG: P | Turnaround: {✅/—}
═══════════════════════════════════════════════════════════════
```

### Özet Tablo
```
# Kod    Son₺   Hedef₺   POT%  vsMevd  Ger  Sinyal     Katalist
1 XXXXX  XX.XX  YY.YY   +ZZ%  +NNpt   85%  🏆 ALTIN    T1 sipariş
```

---

## KÂR KALİTESİ KURALLARI (Tam Liste)

```
Rule 9:  Faal.Kâr(-) + NK(+) → ELEN (standart). RTALB vakası.
Rule 10: İştirak/NK > %80 → ELEN | > %50 → uyarı. RTALB vakası.
Rule 12: Faal.Kâr/NK < %30 → Y5 ağırlık artır | < %50 → uyarı. CATES vakası.
         3 dönem backtest: DEĞİŞMEDİ — Rule 12 + Faz 3 birlikte doğru çalışıyor.
Rule 13: fk_veri_sayisi/750 < %50 → Y1 ağırlık düşür. GSDDE vakası.
Rule 14: Yat.Geliri/Ciro > %50 → hedef düşür | > %30 → uyarı. GSDDE vakası.
Rule 15: Ref F/K = min(3Y ort, sektör ort × 1.5). GSDDE vakası.
         "Adil × 1.5" KULLANILMAZ — Forward F/K yönteminde (Y2) zaten var.
Rule 16: Q4 NK/TTM NK > %70 veya < %10 → TTM NK kullan.
         ESCOM (%99), OYYAT (%91), TTKOM (%3) vakaları.
Rule 17: Garantili sözleşme → Y5'e × 2.5 çarpan. CATES EÜAŞ vakası.
Rule 18: Trend düzeltme → Forward NK seçimi + Y5 trend çarpanı. ATATP vakası.
```

---

## KATMAN NAV — GYO/Holding/Banka

GYO/Holding/Banka için 5 Yöntem AYNI uygulanır ama:
- Y3 (PD/DD) ağırlığı %30'a çıkar (NAV birincil)
- Çift filtre kontrolü yapılır (PD/DD isk + F/K isk = çift ucuz)
- Max potansiyel: GYO %150, Holding %100
- Kâr annualize etme (PEG hesaplanmaz)

```
ÇİFT UCUZ (PD/DD isk + F/K isk) → gerçekleşme %55 (GYO) / %35 (Holding)
TEKLİ UCUZ (PD/DD isk + F/K primli) → gerçekleşme %35 (GYO) / %20 (Holding)
Backtest: Çift ucuz +6.6% ort | Tekli ucuz -10.5% ort

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
ADIM 0: web_search → TCMB faizi + trendi
ADIM 1: MCP SQL → finansal ham data (6 batch Sorgu 14 CTE)
         + 4Q ciro/NK trendi + GY Q4 NK (YoY)
         + son fiyat + sermaye + özkaynak
ADIM 2: ELEME → Rule 9/10 + F/K primli → ~60-90 hisse geçer
ADIM 3: Mevsimsellik → Trend tespiti → Forward NK seçimi (Rule 18)
ADIM 4: Kâr sürprizi → Forward NK büyüme çarpanı
ADIM 5: 5 Yöntem Hedef Fiyat (Y1-Y5 + faiz tavanı + ağırlıklar)
ADIM 6: Katalist + Broker (SQL + her hisse KAP taraması)
         ★ ZORUNLU — ASLA ATLANMAZ
ADIM 7: Makro risk (web_search) → sektörel çarpan
ADIM 8: Gerçekleşme oranı (baz + momentum + PEG + turnaround + güvenlik)
         ★ Katalist bilgisi ADIM 6'dan gelir → T1=%85, yok=%40
ADIM 9: Final hesaplama → Makro × Gerçekleşme → Potansiyel %
         → Faiz bazlı sinyal → CSV + GitHub push

"Son bilançoları değerle" = İncremental:
  Önceki tarama tarihinden sonra yayınlanan bilançoları tespit et,
  SADECE yeni hisseleri tam pipeline'dan geçir, mevcut CSV'ye ekle.
```

### MCP Çağrı Bütçesi
```
ADIM 1:  6 SQL (Sorgu 14 batch) + 2 SQL (trend + YoY) + 1 SQL (fiyat/sermaye)
ADIM 6a: 2 SQL (broker tahmin + hedef fiyat)
ADIM 6b: ~20-25 dokumanlarda_ara (top hisseler KAP)
ADIM 7:  2-3 web_search (makro risk)
Toplam: ~35-40 MCP/tool çağrısı
```

---

## PİYASA FAZI BAZLI STRATEJİ (3 Dönem Doğrulanmış)

```
SÜPER BOĞA (XU100 > +30%):
  ADIM 1-5 tek başına güçlü (α+37.1%)
  Katalist ekstra bonus (α+68.4%)
  Strateji: Geniş tut, ADIM 1-5 yeterli

BOĞA (XU100 +5% → +30%):
  ADIM 1-5 orta (TOP15 α+21.6%)
  ADIM 6 katalist kritik fark (katalistli α+88.4%)
  Strateji: Katalistli hisselere odaklan

AYI (XU100 < +5%):
  ADIM 1-5 TEK BAŞINA ÇALIŞMIYOR (α-1.9%) ❌
  ADIM 6 ZORUNLU (katalistli α+39.6%)
  Strateji: SADECE katalistli hisseler al, katalistsiz → mevduat
```

---

## REFERANS DOSYALARI

| Dosya | İçerik |
|-------|--------|
| `sql-sorgulari_v26.md` | Sorgu 14 CTE + 15/16 broker + KAP şablonu |
| `backtest-bulgular_v26.md` | 3 dönem backtest + GSDDE/CATES/RTALB vakaları |
| `sektor-detay.md` | Sektör çarpanları, mevsimsellik kuralları |
| `haber-katalist-avcisi.md` | Katalist Avcısı v2 tam metodoloji |
| `prompt-kullanim.md` | Kullanım örnekleri |

---

## TEMBELLİK YASAK

Tarama/analiz sırasında:
- Adım atlama, kısaltma, varsayımla geçiştirme YASAK
- Demo/sahte veri üretme YASAK
- Faz 3 (katalist) atlamak YASAK — backtest kanıtı: +59.9pt fark
- Faiz kontrolü atlamak YASAK — mevduattan kötü hisseye AL demek YASAK
- Hesaplamayı yaklaşık yapma YASAK
- Her hisse tek tek taranır, her kural kontrol edilir
- Eksik veri varsa MCP'den çek — uydurma
