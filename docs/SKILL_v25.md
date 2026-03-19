---
name: bilanco-sonrasi-ucuzlama-tarayicisi
description: >
  BIST hisselerinde sistematik değerleme taraması. Fintables MCP ile gerçek veri.
  (A) Tek CTE sorgu ile 574 hisse çekimi → SQL filtreleme → Python skorlama → GitHub push.
  (B) KAP haber taraması ile katalist tespiti. (C) Yapısal iskonto düzeltmesi (GYO/Holding backtest kalibrasyonu).
  (D) Holding 3 Modül: NAV detay + temettü + içeriden alım.
  Tetikleyiciler: "bilanço tarama", "BIST tarama", "ucuz hisse", "son bilançoları değerle",
  "forward F/K", "kâr sürprizi", "mean reversion", "katalist tarama", "pipeline tarama",
  "GYO NAV iskontosu", "holding iskonto", "banka F/DD", "çift filtre", "yapısal iskonto",
  "haber bazlı fırsat", "fiyatlanmamış haber", "sipariş haberi", "BIST değer yatırımı".
---

# BIST Sistematik Tarama Sistemi v2.5
## Pipeline: MCP CTE → SQL Filtreleme → KAP Katalist → Yapısal İskonto → GitHub

---

## MİMARİ ÖZET

4 entegre modül. Tüm veriler Fintables MCP'den canlı çekilir (demo data YASAK).

### (A) Bilanço Değerleme Pipeline (v2.5 Pratik)
Tek kapsamlı CTE sorgusu ile 574 hisse → SQL filtreleme (NK>0, FAVÖK>0, F/K iskontolu) → ~93 hisse → Python skorlama → CSV → GitHub push.

### (B) KAP Katalist Taraması
Toplu konu bazlı arama: "Yeni İş İlişkisi" + "İhale Süreci/Sonucu" + "sipariş/kapasite/yatırım" ODA haberleri → 93 hisseyle eşleştir → Tier 1/2/3 bonus.

### (C) Yapısal İskonto Düzeltmesi
GYO/Holding skorlarını backtest gerçekleşme oranlarıyla kalibre et. Standart şirket katalistsiz → ×0.85.

### (D) Holding 3 Modül
1. NAV Detay: Borsadaki iştiraklerin PD toplamı vs Holding PD
2. Temettü: Son 2Y temettü geçmişi → Tier 3 katalist
3. İçeriden Alım: KAP pay alım/satım bildirimleri → bonus/ceza

---

## "SON BİLANÇOLARI DEĞERLE" AKIŞI (HIZLI WORKFLOW)

Kullanıcı "son gelen bilançoları değerle" veya benzer dediğinde:

### Adım 1: Yeni bilançoları tespit et
```sql
SELECT hisse_senedi_kodu, yayinlanma_tarihi_utc, finansal_tablo_sablonu
FROM hisse_finansal_tablolari
WHERE yil = {GUNCEL_YIL} AND ay = {GUNCEL_AY}
  AND yayinlanma_tarihi_utc >= '{SON_KONTROL_TARIHI}'
ORDER BY yayinlanma_tarihi_utc DESC
LIMIT 100
```
→ Son kontrolden bu yana açıklanan bilançoları bul.

### Adım 2: Her biri için Kapsamlı CTE çalıştır
`references/sql-sorgulari.md` → Sorgu 14 kullan. Tek hisse veya küçük grup:
```sql
-- Kodlar CTE'sine WHERE ekle:
AND ft.hisse_senedi_kodu = ANY(ARRAY['{YENİ_KODLAR}'])
```

### Adım 3: v2.5 Skorlama
- Forward F/K vs Sektör Adil (25p) + F/K İskontosu 3Y (15p) + PD/DD (25p)
- PD/DD İskontosu bonus (5p) + Q4 NK pozitif (5p)
- GYO/Holding çift filtre bonus (10p)
- Sektör çarpanları uygulanır (Teknoloji 1.875x, Enerji 0.75x, vb.)

### Adım 4: KAP Katalist Kontrolü
```
dokumanlarda_ara: filter='iliskili_semboller = "{KOD}" AND kap_bildirim_konu = "Yeni İş İlişkisi"'
dokumanlarda_ara: filter='iliskili_semboller = "{KOD}" AND kap_bildirim_konu = "İhale Süreci / Sonucu"'
```
T1 → +15p (+5 stacking), T2 → +8p (+5 stacking)

### Adım 5: Yapısal İskonto Düzeltmesi
| Tip | Koşul | Katsayı |
|-----|-------|---------|
| Standart | Katalist var | ×1.00 |
| Standart | Katalistsiz | ×0.85 |
| GYO | Çift ucuz + katalist | ×0.70 |
| GYO | Çift ucuz, katalistsiz | ×0.55 |
| GYO | Tekli ucuz | ×0.30 |
| Holding | Katalist var | ×0.50 |
| Holding | Katalistsiz | ×0.30 |

### Adım 5b: Holding 3 Modül (Holding ise)
- NAV Detay: `dokumanlarda_ara` → kurumsal bilgi kartı → iştirakler borsada mı?
  Borsadaki PD toplamı > Holding PD → NAV iskontosu bonusu (+10p)
- Temettü: `hisse_senedi_temettuler` sorgusu → temettü varsa +3p
- İçeriden Alım: KAP "Payların Geri Alınması" + "Pay Alım Satım Bildirimi" → +5p / -5p

### Adım 6: GitHub Push
```
data/arsiv/YYYY_NQ.csv → mevcut dosyaya satır ekle (append)
data/son_tarama.csv → overwrite
data/cumulative.csv → güncelle
README.md → TOP 20 tablosunu güncelle
git commit + push
```

### Adım 7: Kullanıcıya rapor
Değerlenen her hisse için:
```
📌 KOD — [Sektör]
💰 NK TTM: XM | FAVÖK: YM | F/K: A.Ax (3Y ort: B.Bx, isk %C)
📊 PD/DD: D.Dx | Skor: E → Düzeltilmiş: F | Sinyal: {emoji}
📰 Katalist: {varsa özet / yoksa "katalist yok"}
```

---

## TCMB FAİZ → DİNAMİK ÇARPAN

```
Adil F/K = 1 / (TCMB Faizi × 0.70 + %5 Hisse Risk Primi)
Faiz İNDİRİM trendi → ×1.20 | ARTIRIM → ×0.90

Sektör Adil F/K = Adil F/K × Sektör Çarpanı:
  Teknoloji/Savunma: 1.875x | Sanayi/Perakende/Turizm/Gıda: 1.00x
  Enerji/Sigorta/Maden/AracıKurum: 0.75x | İnşaat: 0.625x
  Telekom: 0.875x | Kimya: 0.85x | Bankacılık: 0.50x (F/DD birincil)
  GYO/Holding: NAV bazlı (çarpan uygulanmaz)
```

---

## SKORLAMA (100p + bonus/ceza)

| Faktör | Max Puan | Koşullar |
|--------|----------|----------|
| Forward F/K vs Sektör Adil | 25 | <Adil×0.5=25, <Adil=20, <×1.5=15, <×2=8 |
| F/K İskontosu (3Y ort) | 15 | >%50=15, %30-50=11, %15-30=6 |
| PD/DD Değerleme | 25 | <1.0=25, <1.5=20, <2.0=15, <3.0=8 |
| PD/DD İskontosu bonus | 5 | >%50=5, >%30=3 |
| Q4 NK pozitif | 5 | NK Q4 > 0 = 5 |
| GYO/Holding çift filtre | 10 | F/K isk + PD/DD isk ikisi pozitif |

### Katalist Bonus
| Tier | Bonus | Stacking (3+ haber) |
|------|-------|---------------------|
| T1 (Sipariş/İhale/Tesis) | +15 | +5 ek |
| T2 (Kapasite/Patent) | +8 | +5 ek |
| T3 (Temettü/ESG) | +3 | — |

### Sinyal Eşikleri (Düzeltilmiş Skora Göre)
```
≥ 80 → 🟢 ALTIN FIRSAT | ≥ 60 → 🟡 FORWARD UCUZ | ≥ 40 → 🟠 TAVSİYE
≥ 30 → ⚪ İZLEME      | < 30 → 🔴 ELEN
```

---

## ÖN FİLTRELER

```
1. NK TTM > 0 (yıllık kârlı)
2. FAVÖK TTM > 0 (operasyonel sağlık)
3. Son F/K < 3Y Ortalama F/K (iskontolu — mean reversion)
4. NK Q4 ≤ 0 + TTM NK ≤ 0 → ELEN (çift zarar)
5. Skor < 30 → ELEN (kalite eşiği)
6. Banka/GYO/Holding → yapısal iskonto düzeltmesi zorunlu
```

---

## GYO/HOLDİNG/BANKA ÖZEL KURALLARI

### Çift Filtre (Backtest: +6.6% ort çift ucuz vs -10.5% tekli ucuz)
```
PD/DD İSK + F/K İSK → ÇİFT UCUZ 🟢🟢 → düzeltme ×0.55-0.70
PD/DD İSK + F/K PRİM → TEKLİ UCUZ ⚠️  → düzeltme ×0.30
PD/DD PRİM → 🔴 ELEN
```

### Holding 3 Modül
1. **NAV Detay**: `dokumanlarda_ara` → kurumsal bilgi kartı → "İştirakler ve Bağlı Ortaklıklar" bölümü → borsadaki iştiraklerin PD'si → NAV iskontosu hesapla
   - Borsadaki iştirak değeri > Holding PD → +10 bonus
   - Örnek: GLRYH (PD 2.6B) → A1CAP %32 (3.41B) + PRDGS %29 (0.37B) + RTALB %5 (0.10B) = 3.88B > 2.6B → %33 NAV iskontosu
2. **Temettü**: `hisse_senedi_temettuler` → son 2Y temettü varsa Tier 3 (+3p)
3. **İçeriden Alım**: KAP "Payların Geri Alınması" + "Pay Alım Satım Bildirimi" haberleri
   - Aktif geri alım programı → +5p
   - Geri alım sona erdi/paylar elden çıkarıldı → 0 veya -3p

### Banka
```
Birincil: F/DD (PD/DD) | İkincil: F/K 3Y ort
ROE > %20 → kalite bonus +%10
Faiz indirimi trendi → gerçekleşme %50-70
```

---

## TARAMA PIPELINE (TAM AKIŞ)

### Tam Tarama (574 hisse)
1. TCMB faizi çek (web_search)
2. Kapsamlı CTE Sorgu × 6 batch (OFFSET 0/100/200/300/400/500) → 574 hisse verisi
3. SQL filtreleme (NK>0, FAVÖK>0, F/K iskontolu) → ~93 hisse
4. Python skorlama → ham skor
5. KAP toplu katalist taraması (konu bazlı):
   - "Yeni İş İlişkisi" (son 6 ay)
   - "İhale Süreci / Sonucu" (son 6 ay)
   - 93 hisseyle eşleştir → T1/T2 bonus
6. Yapısal iskonto düzeltmesi → düzeltilmiş skor
7. Holding 3 Modül (varsa)
8. CSV + README güncelle → GitHub push

### Tekil Bilanço Değerleme ("son bilançoları değerle")
1. Yeni açıklanan bilançoları tespit et
2. Kapsamlı CTE Sorgu (sadece o hisseler)
3. Skorlama + KAP katalist kontrolü
4. Yapısal iskonto düzeltmesi
5. Mevcut 2025_4Q.csv'ye satır ekle (append)
6. GitHub push

---

## GITHUB REPO YAPISI

```
zeynelgun-afk/Fintables/
├── README.md              ← TOP 20 + sinyal dağılımı
├── config.json            ← TCMB faiz, adil F/K, filtre parametreleri
├── data/
│   ├── son_tarama.csv     ← En güncel (overwrite)
│   ├── cumulative.csv     ← Tüm zamanlar
│   └── arsiv/2025_4Q.csv  ← Çeyrek bazlı (aynı çeyrekte append)
├── reports/2025_4Q.xlsx
└── scripts/pipeline_v24.py
```

CSV Kolonları:
```
tarama_tarihi, kod, sektor, pd_b_tl, nk_ttm_m, nk_q4_m, favok_m,
son_fk, ort_fk_3y, fk_iskonto_pct, son_pddd, ort_pddd_3y, pddd_iskonto_pct,
skor, sinyal, katalist_tier, katalist_sayi, katalist_ozet,
duzeltilmis_skor, duzeltme_notu, nav_notu
```

---

## REFERANS DOSYALARI

| Dosya | İçerik | Ne Zaman Oku |
|-------|--------|--------------|
| `references/sql-sorgulari.md` | Sorgu 14 (ana) + tek hisse detay + arşiv | Veri çekmeden önce |
| `references/backtest-bulgular.md` | 11 dönem + GYO/Holding 6Q backtest | Sonuçları yorumlarken |
| `references/sektor-detay.md` | Sektör çarpanları, mevsimsellik | Sektör bazlı hesaplama |
| `references/haber-katalist-avcisi.md` | Katalist Avcısı v2 tam metodoloji | Haber taraması yaparken |
| `references/prompt-kullanim.md` | Kullanım örnekleri, opsiyonel modlar | Kullanıcı talimatlarında |

---

## KRİTİK KURALLAR

1. **Demo data YASAK** — tüm veriler Fintables MCP'den canlı çekilir
2. **GYO/Holding asla standart şirket gibi değerlendirilmez** — yapısal iskonto düzeltmesi zorunlu
3. **Katalistsiz ucuzluk tek başına yetmez** — backtest: katalist var %70-100, yok %30-50
4. **Pipeline deterministik** — aynı veri = aynı çıktı, elle müdahale sıfır
5. **GitHub her değerlemede güncellenir** — CSV append, README güncelle, push
6. **NAV iskontosu sadece PD/DD ile ölçülmez** — holding iştirakleri borsadaysa gerçek NAV hesapla
