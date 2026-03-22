# SQL Şablonları v2.5 — Fintables MCP

## Önemli Kısıtlar
- Hard row limit: max 100 satır → LIMIT 100 OFFSET N pagination
- Bloke: LATERAL, TRIM/BTRIM, AT TIME ZONE, CURRENT_DATE/NOW(), generate_series()
- Çalışan: UNNEST(ARRAY[...]), CTE, literal tarih ('2026-03-19')
- character(50) kolonlarda join → padding dikkate al
- Her oturumda `finansal_beceri_yukle` ile şema yükle

---

## SORGU 1: Ön Filtreli Hisse Listesi (Batch 1/2)

```sql
SELECT
  hs.kod,
  hs.baslik AS sirket_adi,
  s.baslik AS sektor,
  hs.finansal_tablo_sablonu AS sablon,
  hs.piyasa_degeri,
  hs.son_fiyat
FROM hisse_senetleri hs
LEFT JOIN sektorler s ON s.id = hs.sektor_id
WHERE hs.piyasa_degeri > 3000000000
  AND hs.finansal_tablo_sablonu = 'default'
ORDER BY hs.piyasa_degeri DESC
LIMIT 100 OFFSET 0
```
→ Batch 2: `OFFSET 100`
→ Banka: `finansal_tablo_sablonu = 'bank'`
→ GYO: `s.baslik = 'Gayrimenkul'`
→ Holding: `s.baslik = 'Holding'`

---

## SORGU 2: TTM Gelir Tablosu (Batch)

```sql
SELECT
  ft.hisse_senedi_kodu AS kod,
  ft.donem,
  MAX(CASE WHEN fk.baslik = 'Satış Gelirleri' THEN ft.deger END) AS ciro,
  MAX(CASE WHEN fk.baslik = 'Brüt Kar (Zarar)' THEN ft.deger END) AS brut_kar,
  MAX(CASE WHEN fk.baslik = 'Esas Faaliyet Karı (Zararı)' THEN ft.deger END) AS faal_kar,
  MAX(CASE WHEN fk.baslik = 'Sürdürülen Faaliyetler Vergi Öncesi Karı (Zararı)' THEN ft.deger END) AS vok,
  MAX(CASE WHEN fk.baslik = 'Ana Ortaklık Payları' THEN ft.deger END) AS net_kar,
  MAX(CASE WHEN fk.baslik = 'Amortisman ve İtfa Giderleri (-)' THEN ft.deger END) AS amortisman,
  MAX(CASE WHEN fk.baslik = 'Diğer Faaliyet Gelirleri' THEN ft.deger END) AS diger_faal_gelir
FROM hisse_finansal_tablolari ft
JOIN hisse_finansal_tablolari_finansal_kalemleri fk ON fk.id = ft.finansal_kalem_id
WHERE ft.hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
  AND ft.donem IN ('{SON_DONEM}', '{ONCEKI_DONEM}', '{GY_AYNI_DONEM}')
  AND ft.tablo_tipi = 'gelir_tablosu'
GROUP BY ft.hisse_senedi_kodu, ft.donem
ORDER BY ft.hisse_senedi_kodu, ft.donem DESC
```

---

## SORGU 3: Bilanço Kalemleri

```sql
SELECT
  ft.hisse_senedi_kodu AS kod,
  ft.donem,
  MAX(CASE WHEN fk.baslik = 'Nakit ve Nakit Benzerleri' THEN ft.deger END) AS nakit,
  MAX(CASE WHEN fk.baslik = 'Finansal Borçlar' AND fk.ust_baslik_id IS NOT NULL THEN ft.deger END) AS fin_borc_kisa,
  MAX(CASE WHEN fk.baslik = 'Uzun Vadeli Borçlanmalar' THEN ft.deger END) AS fin_borc_uzun,
  MAX(CASE WHEN fk.baslik = 'Özkaynaklar' THEN ft.deger END) AS ozkaynak,
  MAX(CASE WHEN fk.baslik = 'Ana Ortaklığa Ait Özkaynaklar' THEN ft.deger END) AS ana_ozkaynak,
  MAX(CASE WHEN fk.baslik = 'Ödenmiş Sermaye' THEN ft.deger END) AS odenmis_sermaye,
  MAX(CASE WHEN fk.baslik = 'Ticari Alacaklar' AND fk.ust_baslik_id IS NOT NULL THEN ft.deger END) AS ticari_alacak,
  MAX(CASE WHEN fk.baslik = 'Stoklar' THEN ft.deger END) AS stoklar,
  MAX(CASE WHEN fk.baslik = 'Maddi Duran Varlıklar' THEN ft.deger END) AS maddi_duran,
  MAX(CASE WHEN fk.baslik = 'Toplam Yükümlülükler' THEN ft.deger END) AS toplam_yukumluluk
FROM hisse_finansal_tablolari ft
JOIN hisse_finansal_tablolari_finansal_kalemleri fk ON fk.id = ft.finansal_kalem_id
WHERE ft.hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
  AND ft.donem = '{SON_DONEM}'
  AND ft.tablo_tipi = 'bilanco'
GROUP BY ft.hisse_senedi_kodu, ft.donem
```

---

## SORGU 4: Nakit Akış Tablosu (İşletme NA)

```sql
SELECT
  ft.hisse_senedi_kodu AS kod,
  ft.donem,
  MAX(CASE WHEN fk.baslik = 'İşletme Faaliyetlerinden Nakit Akışları' THEN ft.deger END) AS isletme_na
FROM hisse_finansal_tablolari ft
JOIN hisse_finansal_tablolari_finansal_kalemleri fk ON fk.id = ft.finansal_kalem_id
WHERE ft.hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
  AND ft.donem = '{SON_DONEM}'
  AND ft.tablo_tipi = 'nakit_akis'
GROUP BY ft.hisse_senedi_kodu, ft.donem
```

---

## SORGU 5: TTM Finansal Oranlar

```sql
SELECT
  hisse_senedi_kodu AS kod,
  donem,
  MAX(CASE WHEN baslik = 'F/K' THEN deger END) AS fk,
  MAX(CASE WHEN baslik = 'PD/DD' THEN deger END) AS pddd,
  MAX(CASE WHEN baslik = 'FD/FAVÖK' THEN deger END) AS fd_favok,
  MAX(CASE WHEN baslik = 'Net Kar Marjı' THEN deger END) AS nk_marj,
  MAX(CASE WHEN baslik = 'Özsermaye Karlılığı (ROE)' THEN deger END) AS roe
FROM hisse_finansal_tablolari_finansal_oranlari
WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
  AND donem = '{SON_DONEM}'
GROUP BY hisse_senedi_kodu, donem
```
⚠️ 2025/12 için F/K ve FD/FAVÖK boş dönebilir → Sorgu 11'i kullan.

---

## SORGU 6-10: Tarihsel Karşılaştırma (Önceki 3Q + Geçen Yıl)

Sorgu 2'nin aynısını farklı dönemlerle çalıştır:
- Önceki Q: `'{ONCEKI_Q}'`
- 2 önceki Q: `'{2_ONCEKI_Q}'`
- 3 önceki Q: `'{3_ONCEKI_Q}'`
- Geçen yıl aynı Q: `'{GY_AYNI_Q}'`
- Geçen yıl önceki Q: `'{GY_ONCEKI_Q}'`

YoY ve QoQ hesaplamaları bu dönemlerden yapılır.

---

## SORGU 11: Tarihsel Çarpanlar (3Y Ortalama — ANA SORGU)

```sql
WITH ort AS (
  SELECT hisse_senedi_kodu,
    ROUND(AVG(CASE WHEN fk > 0 AND fk < 80 THEN fk END)::numeric, 2) AS ort_fk_3y,
    ROUND(AVG(CASE WHEN pddd > 0 THEN pddd END)::numeric, 2) AS ort_pddd_3y,
    ROUND(AVG(CASE WHEN fd_favok > 0 AND fd_favok < 50 THEN fd_favok END)::numeric, 2) AS ort_fd_favok_3y,
    COUNT(CASE WHEN fk > 0 AND fk < 80 THEN 1 END) AS fk_veri_sayisi
  FROM hisse_senedi_tarihsel_carpanlar
  WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
    AND tarih_europe_istanbul >= '{3Y_ONCE}'
  GROUP BY hisse_senedi_kodu
),
son AS (
  SELECT DISTINCT ON (hisse_senedi_kodu) hisse_senedi_kodu,
    ROUND(fk::numeric, 2) AS son_fk,
    ROUND(pddd::numeric, 2) AS son_pddd,
    ROUND(fd_favok::numeric, 2) AS son_fd_favok,
    tarih_europe_istanbul AS son_tarih
  FROM hisse_senedi_tarihsel_carpanlar
  WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
    AND tarih_europe_istanbul >= '{SON_5_GUN}'
  ORDER BY hisse_senedi_kodu, tarih_europe_istanbul DESC
)
SELECT o.hisse_senedi_kodu,
  o.ort_fk_3y, s.son_fk,
  CASE WHEN s.son_fk > 0 AND o.ort_fk_3y > 0
    THEN ROUND((1 - s.son_fk / o.ort_fk_3y) * 100, 1) END AS fk_iskonto_pct,
  o.ort_pddd_3y, s.son_pddd,
  CASE WHEN s.son_pddd > 0 AND o.ort_pddd_3y > 0
    THEN ROUND((1 - s.son_pddd / o.ort_pddd_3y) * 100, 1) END AS pddd_iskonto_pct,
  o.ort_fd_favok_3y, s.son_fd_favok,
  o.fk_veri_sayisi
FROM ort o JOIN son s ON s.hisse_senedi_kodu = o.hisse_senedi_kodu
ORDER BY fk_iskonto_pct DESC NULLS LAST
```

---

## SORGU 11b: Sektör Medyan Çarpanları

```sql
SELECT
  s.baslik AS sektor,
  COUNT(DISTINCT tc.hisse_senedi_kodu) AS hisse_sayisi,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tc.fk) FILTER (WHERE tc.fk > 0 AND tc.fk < 80)::numeric, 2) AS medyan_fk,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tc.pddd) FILTER (WHERE tc.pddd > 0)::numeric, 2) AS medyan_pddd,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tc.fd_favok) FILTER (WHERE tc.fd_favok > 0 AND tc.fd_favok < 50)::numeric, 2) AS medyan_fd_favok
FROM hisse_senedi_tarihsel_carpanlar tc
JOIN hisse_senetleri hs ON hs.kod = tc.hisse_senedi_kodu
JOIN sektorler s ON s.id = hs.sektor_id
WHERE tc.tarih_europe_istanbul >= '{SON_5_GUN}'
GROUP BY s.baslik
HAVING COUNT(DISTINCT tc.hisse_senedi_kodu) >= 3
ORDER BY s.baslik
```

---

## SORGU 11c: Son Günün Çarpanları (Sorgu 5 boş dönerse yedek)

```sql
SELECT DISTINCT ON (hisse_senedi_kodu)
  hisse_senedi_kodu AS kod,
  tarih_europe_istanbul AS tarih,
  ROUND(fk::numeric, 2) AS fk,
  ROUND(pddd::numeric, 2) AS pddd,
  ROUND(fd_favok::numeric, 2) AS fd_favok
FROM hisse_senedi_tarihsel_carpanlar
WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
ORDER BY hisse_senedi_kodu, tarih_europe_istanbul DESC
```

---

## SORGU 12: Broker Tahminleri ve Hedef Fiyatlar

```sql
SELECT
  hisse_senedi_kodu AS kod,
  araci_kurum,
  tavsiye,
  hedef_fiyat,
  tarih
FROM hisse_senedi_araci_kurum_hedef_fiyatlari
WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
ORDER BY hisse_senedi_kodu, tarih DESC
LIMIT 100
```

```sql
SELECT
  hisse_senedi_kodu AS kod,
  yil,
  araci_kurum,
  net_kar_tahmini,
  ciro_tahmini
FROM hisse_senedi_araci_kurum_tahminleri
WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
  AND yil >= 2025
ORDER BY hisse_senedi_kodu, yil, araci_kurum
LIMIT 100
```

---

## SORGU 13: Fiyat Verisi (1Y Alfa Hesaplama)

```sql
SELECT
  hisse_senedi_kodu AS kod,
  tarih_europe_istanbul AS tarih,
  kapanis_fiyati
FROM hisse_senedi_ohlcv
WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}', 'XU100'])
  AND tarih_europe_istanbul >= '{1Y_ONCE}'
  AND periyot = 'gunluk'
ORDER BY hisse_senedi_kodu, tarih_europe_istanbul DESC
LIMIT 100
```
⚠️ XU100 endeks kodu ayrı sorgulanabilir — kontrol et.

---

## SORGU 14: KAPSAMLİ BİRLEŞİK CTE (v2.6 — ÖNERİLEN)

Tüm verileri TEK SORGUDA çeker: hisse listesi + gelir tablosu + 3Y tarihsel çarpanlar + sektör ort F/K.
574 hisse = 6 batch (OFFSET 0/100/200/300/400/500).

```sql
WITH kodlar AS (
  SELECT ft.hisse_senedi_kodu, ft.finansal_tablo_sablonu, hs.piyasa_degeri, s.baslik AS sektor
  FROM hisse_finansal_tablolari ft
  JOIN hisse_senetleri hs ON hs.hisse_senedi_kodu = ft.hisse_senedi_kodu
  LEFT JOIN sektorler s ON s.id = hs.sektor_id
  WHERE ft.yil = {YIL} AND ft.ay = {AY} AND ft.yayinlanma_tarihi_utc IS NOT NULL
  ORDER BY ft.hisse_senedi_kodu LIMIT 100 OFFSET {N}
),
gelir AS (
  SELECT g.hisse_senedi_kodu AS kod,
    MAX(CASE WHEN g.kalem = 'Ana Ortaklık Payları' THEN g.try_ttm END) AS nk_ttm,
    MAX(CASE WHEN g.kalem = 'Ana Ortaklık Payları' THEN g.try_ceyreklik END) AS nk_q4,
    MAX(CASE WHEN g.kalem = 'FAVÖK' THEN g.try_ttm END) AS favok_ttm,
    MAX(CASE WHEN g.kalem = 'Faaliyet Karı (Zararı)' THEN g.try_ttm END) AS faal_kar_ttm,
    MAX(CASE WHEN g.kalem = 'Özkaynak Yöntemiyle Değerlenen Yatırımların Karlarından (Zararlarından) Paylar' THEN g.try_ttm END) AS istirak_kar_payi,
    MAX(CASE WHEN g.kalem = 'Yatırım Faaliyetlerinden Gelirler' THEN g.try_ttm END) AS yatirim_geliri,
    MAX(CASE WHEN g.kalem = 'Satış Gelirleri' THEN g.try_ttm END) AS ciro_ttm
  FROM hisse_finansal_tablolari_gelir_tablosu_kalemleri g
  JOIN kodlar k ON k.hisse_senedi_kodu = g.hisse_senedi_kodu
  WHERE g.yil = {YIL} AND g.ay = {AY} AND g.kalem IN ('Ana Ortaklık Payları', 'FAVÖK', 'Faaliyet Karı (Zararı)', 'Özkaynak Yöntemiyle Değerlenen Yatırımların Karlarından (Zararlarından) Paylar', 'Yatırım Faaliyetlerinden Gelirler', 'Satış Gelirleri')
  GROUP BY g.hisse_senedi_kodu
),
ort AS (
  SELECT tc.hisse_senedi_kodu AS kod,
    ROUND(AVG(CASE WHEN tc.fk > 0 AND tc.fk < 80 THEN tc.fk END)::numeric, 2) AS ort_fk,
    ROUND(AVG(CASE WHEN tc.pddd > 0 THEN tc.pddd END)::numeric, 2) AS ort_pddd,
    COUNT(CASE WHEN tc.fk > 0 AND tc.fk < 80 THEN 1 END) AS fk_veri_sayisi
  FROM hisse_senedi_tarihsel_carpanlar tc
  JOIN kodlar k ON k.hisse_senedi_kodu = tc.hisse_senedi_kodu
  WHERE tc.tarih_europe_istanbul >= '{3Y_ONCE}' GROUP BY tc.hisse_senedi_kodu
),
sektor_ort AS (
  SELECT s.baslik AS sektor,
    ROUND(AVG(CASE WHEN tc2.fk > 0 AND tc2.fk < 40 THEN tc2.fk END)::numeric, 2) AS sektor_ort_fk
  FROM hisse_senedi_tarihsel_carpanlar tc2
  JOIN hisse_senetleri hs2 ON hs2.hisse_senedi_kodu = tc2.hisse_senedi_kodu
  JOIN sektorler s ON s.id = hs2.sektor_id
  WHERE tc2.tarih_europe_istanbul >= '{SON_5_GUN}'
  GROUP BY s.baslik
  HAVING COUNT(DISTINCT tc2.hisse_senedi_kodu) >= 3
),
son AS (
  SELECT DISTINCT ON (tc.hisse_senedi_kodu) tc.hisse_senedi_kodu AS kod,
    ROUND(tc.fk::numeric, 2) AS son_fk, ROUND(tc.pddd::numeric, 2) AS son_pddd
  FROM hisse_senedi_tarihsel_carpanlar tc
  JOIN kodlar k ON k.hisse_senedi_kodu = tc.hisse_senedi_kodu
  WHERE tc.tarih_europe_istanbul >= '{SON_5_GUN}'
  ORDER BY tc.hisse_senedi_kodu, tc.tarih_europe_istanbul DESC
)
SELECT k.hisse_senedi_kodu AS kod, k.sektor, k.finansal_tablo_sablonu AS sablon,
  ROUND(k.piyasa_degeri::numeric, 0) AS pd, g.nk_ttm, g.nk_q4, g.favok_ttm,
  g.faal_kar_ttm, g.istirak_kar_payi, g.yatirim_geliri, g.ciro_ttm,
  o.ort_fk, o.ort_pddd, o.fk_veri_sayisi,
  so.sektor_ort_fk,
  s.son_fk, s.son_pddd
FROM kodlar k LEFT JOIN gelir g ON g.kod = k.hisse_senedi_kodu
LEFT JOIN ort o ON o.kod = k.hisse_senedi_kodu
LEFT JOIN sektor_ort so ON so.sektor = k.sektor
LEFT JOIN son s ON s.kod = k.hisse_senedi_kodu
ORDER BY k.hisse_senedi_kodu LIMIT 100
```

### Filtrelenmiş versiyon (sadece kârlı + iskontolu hisseleri döndürür)
Yukarıdaki sorguya gelir CTE'sine `HAVING nk_ttm > 0 AND favok_ttm > 0` ekle,
WHERE'e `s.son_fk < o.ort_fk` ekle → doğrudan geçen hisseleri verir.

### v2.5 Kâr Kalitesi Filtresi (Python tarafında veya SQL WHERE'de)
```
Sorgu çıktısından şu hisseler ELENİR veya CEZA alır:
  1. faal_kar_ttm < 0 AND nk_ttm > 0 → ELEN (faaliyet zararı + net kâr pozitif = tuzak)
     RTALB vakası: Faal.Kâr -19M, NK +881M, İştirak Kâr Payı 1,105M
  2. istirak_kar_payi > nk_ttm * 0.8 → ELEN (kâr tamamen iştirakten)
  3. istirak_kar_payi > nk_ttm * 0.5 → skor × 0.6 ceza (kâr kalitesi düşük)
  4. faal_kar_ttm > 0 AND nk_ttm > 0 AND faal_kar_ttm / nk_ttm < 0.3 → skor × 0.5 ceza
     CATES vakası: Faal.Kâr 368M / NK 1,788M = %21, Yatırım Geliri 2,750M
  5. faal_kar_ttm > 0 AND nk_ttm > 0 AND faal_kar_ttm / nk_ttm < 0.5 → skor × 0.7 ceza
  
SQL'de hard ELEN filtreleri:
  AND NOT (g.faal_kar_ttm < 0 AND g.nk_ttm > 0)
  AND NOT (g.istirak_kar_payi > g.nk_ttm * 0.8 AND g.istirak_kar_payi IS NOT NULL)
  
Python'da oran bazlı cezalar (ELEN değil, skor düşürme):
  if faal_kar_ttm > 0 and nk_ttm > 0:
      ratio = faal_kar_ttm / nk_ttm
      if ratio < 0.3: skor *= 0.5   # CATES tipi
      elif ratio < 0.5: skor *= 0.7
```

### v2.6 Ek Kontroller (Python tarafında — GSDDE Vakasından)
```
Rule 13 — F/K Veri Güvenilirliği:
  if fk_veri_sayisi / 750 < 0.5:
      y2_skor *= 0.5  # 3Y ort güvenilmez, Y2 iskonto skorunu yarıya indir
  
  GSDDE vakası: 286/750 = %38 → Y2 15p × 0.5 = 7.5p

Rule 14 — Yatırım Geliri / Ciro Kontrolü:
  if ciro_ttm > 0 and yatirim_geliri is not None:
      yg_oran = yatirim_geliri / ciro_ttm
      if yg_oran > 0.5: skor *= 0.5   # Gemi/varlık satışı baskın
      elif yg_oran > 0.3: skor *= 0.7
  
  ★ DİKKAT: Bu kural Rule 12 (Faal.Kâr/NK) ile AYRI çalışır.
  Rule 12 yakalayamaz çünkü yatırım geliri finansman gideri ile dengelenebilir.
  GSDDE: Yat.Gel. 302M / Ciro 585M = %52 → skor × 0.5

Rule 15 — Sektör Ort. F/K Tavanı:
  sektor_adil_fk = dinamik_adil_fk * sektor_carpani  # TCMB bazlı
  referans_fk = min(ort_fk, sektor_ort_fk * 1.5, sektor_adil_fk * 1.5)
  
  # Eğer referans kendi ortalamasından düşükse, o referansla iskonto hesapla
  if referans_fk < ort_fk:
      fk_iskonto = (1 - son_fk / referans_fk) * 100
  else:
      fk_iskonto = (1 - son_fk / ort_fk) * 100
  
  # Negatif iskonto (primli) → Y2 = 0p
  if fk_iskonto < 0: y2_skor = 0
  
  GSDDE: min(31.76, 25.44, 4.86) = 4.86x → 7.79/4.86 = primli → Y2 = 0p
```

---

## SORGU 15: BROKER KONSENSÜs TAHMİNLERİ (Faz 3 — Toplu)

```sql
SELECT
  t.hisse_senedi_kodu AS kod,
  t.yil,
  ROUND(AVG(t.net_kar)::numeric, 0) AS konsensus_nk,
  ROUND(AVG(t.satislar)::numeric, 0) AS konsensus_ciro,
  ROUND(AVG(t.favok)::numeric, 0) AS konsensus_favok,
  COUNT(DISTINCT t.araci_kurum_kodu) AS analist_sayisi
FROM hisse_senedi_araci_kurum_tahminleri t
WHERE t.hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
  AND t.yil IN (2025, 2026) AND t.ay = 12
GROUP BY t.hisse_senedi_kodu, t.yil
ORDER BY t.hisse_senedi_kodu, t.yil
LIMIT 100
```

## SORGU 16: BROKER HEDEF FİYATLAR (Faz 3 — Toplu, son 6 ay)

```sql
SELECT
  hf.hisse_senedi_kodu AS kod,
  COUNT(*) AS rapor_sayisi,
  ROUND(AVG(hf.hedef_fiyat)::numeric, 2) AS ort_hedef,
  MAX(hf.hedef_fiyat) AS max_hedef,
  MIN(hf.hedef_fiyat) AS min_hedef
FROM hisse_senedi_araci_kurum_hedef_fiyatlari hf
WHERE hf.hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
  AND hf.yayin_tarihi_europe_istanbul >= '{6_AY_ONCE}'
  AND hf.hedef_fiyat > 0
GROUP BY hf.hisse_senedi_kodu
ORDER BY hf.hisse_senedi_kodu
LIMIT 100
```

## KAP HABER TARAMA ŞABLONu (Faz 3 — Her hisse için)

```
dokumanlarda_ara(
  query="sözleşme sipariş yatırım kapasite ihale tesis",
  filter='dokuman_tipi = "kap_haberi" AND kap_bildirim_tipi = "ODA"
    AND iliskili_semboller = "{KOD}"
    AND yayinlanma_tarihi_utc > {6_AY_ONCE_UTC}',
  sirala="yayinlanma_tarihi_utc:desc",
  sayfa_basi=5
)
```

Katalist sınıflandırma:
- "sözleşme" / "sipariş" / "ihale" → Tier 1
- "yatırım" / "kapasite" / "tesis" → Tier 1/2
- "ortaklık" / "satın alma" → Tier 1
- "patent" / "lisans" → Tier 2
- "temettü" / "geri alım" → Tier 3

---

## BATCH STRATEJİSİ

### v2.5 Entegre (ÖNERİLEN):
```
Faz 1: 6 MCP sorgusu → Sorgu 14 CTE (574 hisse, 100'erli batch)
Faz 2: Python hesaplama (MCP çağrısı yok)
Faz 3: ~20-25 MCP çağrısı:
  - 1× Sorgu 15 (broker tahminler, toplu)
  - 1× Sorgu 16 (hedef fiyatlar, toplu)
  - ~15-20× dokumanlarda_ara (top hisseler KAP haberleri)
  - ~3-5× web_search (sektörel haberler)
Faz 4: Python final skorlama + CSV + GitHub push
Toplam: ~30 MCP/tool çağrısı
```
