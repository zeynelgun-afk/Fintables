# SQL Şablonları v2.5 — Fintables MCP

## Önemli Kısıtlar
- Hard row limit: max 100 satır → LIMIT 100 OFFSET N pagination
- Bloke: LATERAL, TRIM/BTRIM, AT TIME ZONE, CURRENT_DATE/NOW(), generate_series()
- Çalışan: UNNEST(ARRAY[...]), CTE, literal tarih ('2026-03-19')
- character(50) kolonlarda join → padding dikkate al
- Her oturumda `finansal_beceri_yukle` ile şema yükle

---

# 🟢 ANA YÖNTEM: Kapsamlı Birleşik CTE (Sorgu 14)

> **Tam tarama için TEK SORGU yeterli.** Hisse listesi + gelir tablosu + 3Y tarihsel çarpanlar
> TEK SORGUDA çekilir. 574 hisse = 6 batch (OFFSET 0/100/200/300/400/500).
> Eski yöntem (Sorgu 1-11 ayrı ayrı) artık kullanılmıyor.

## Tam Veri Çekimi (Filtresiz)

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
    MAX(CASE WHEN g.kalem = 'FAVÖK' THEN g.try_ttm END) AS favok_ttm
  FROM hisse_finansal_tablolari_gelir_tablosu_kalemleri g
  JOIN kodlar k ON k.hisse_senedi_kodu = g.hisse_senedi_kodu
  WHERE g.yil = {YIL} AND g.ay = {AY} AND g.kalem IN ('Ana Ortaklık Payları', 'FAVÖK')
  GROUP BY g.hisse_senedi_kodu
),
ort AS (
  SELECT tc.hisse_senedi_kodu AS kod,
    ROUND(AVG(CASE WHEN tc.fk > 0 AND tc.fk < 80 THEN tc.fk END)::numeric, 2) AS ort_fk,
    ROUND(AVG(CASE WHEN tc.pddd > 0 THEN tc.pddd END)::numeric, 2) AS ort_pddd
  FROM hisse_senedi_tarihsel_carpanlar tc
  JOIN kodlar k ON k.hisse_senedi_kodu = tc.hisse_senedi_kodu
  WHERE tc.tarih_europe_istanbul >= '{3Y_ONCE}' GROUP BY tc.hisse_senedi_kodu
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
  o.ort_fk, o.ort_pddd, s.son_fk, s.son_pddd
FROM kodlar k LEFT JOIN gelir g ON g.kod = k.hisse_senedi_kodu
LEFT JOIN ort o ON o.kod = k.hisse_senedi_kodu
LEFT JOIN son s ON s.kod = k.hisse_senedi_kodu
ORDER BY k.hisse_senedi_kodu LIMIT 100
```

## Filtrelenmiş Versiyon (Sadece Geçen Hisseler)

NK>0 + FAVÖK>0 + F/K iskontolu olanları doğrudan döndürür.
SQL'de filtreleme sayesinde Python'a sadece ~90-100 hisse gider.

```sql
-- Yukarıdaki sorgunun gelir CTE'sine ekle:
  HAVING MAX(CASE WHEN g.kalem = 'Ana Ortaklık Payları' THEN g.try_ttm END) > 0
    AND MAX(CASE WHEN g.kalem = 'FAVÖK' THEN g.try_ttm END) > 0
-- Son SELECT'e ekle:
WHERE s.son_fk IS NOT NULL AND o.ort_fk IS NOT NULL
  AND s.son_fk > 0 AND s.son_fk < o.ort_fk
ORDER BY (1 - s.son_fk / o.ort_fk) DESC
```

## Batch Stratejisi

| Yöntem | Batch Sayısı | Toplam Sorgu | Kullanım |
|--------|-------------|--------------|----------|
| **v2.5 Pratik (ÖNERİLEN)** | 6 × 100 | 6 MCP sorgusu | Tam tarama |
| v2.4 Eski | 2+4+4 = 10+ batch | ~20 MCP sorgusu | Kullanılmıyor |

---

# 🔵 TEK HİSSE DETAYLI ANALİZ SORGULARI

> Tam taramada gerek yok. Tek hisse derinlemesine incelenirken kullan.

## Bilanço Kalemleri (Özkaynak, Nakit, Borç)

```sql
SELECT hisse_senedi_kodu AS kod, kalem, try_donemsel
FROM hisse_finansal_tablolari_bilanco_kalemleri
WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
  AND yil = {YIL} AND ay = {AY}
  AND kalem IN (
    'Ana Ortaklığa Ait Özkaynaklar', 'Toplam Özkaynaklar',
    'Nakit ve Nakit Benzerleri', 'Toplam Finansal Borçlar',
    'Net Borç', 'Toplam Varlıklar', 'Ödenmiş Sermaye'
  )
ORDER BY hisse_senedi_kodu, kalem
LIMIT 100
```

## Nakit Akış Tablosu (İşletme NA — Nakit Dönüşüm Kalitesi)

```sql
SELECT hisse_senedi_kodu AS kod, kalem, try_donemsel, try_ttm
FROM hisse_finansal_tablolari_nakit_akis_tablosu_kalemleri
WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
  AND yil = {YIL} AND ay = {AY}
  AND kalem = 'İşletme Faaliyetlerinden Nakit Akışları'
ORDER BY hisse_senedi_kodu
LIMIT 100
```

## Finansal Oranlar (ROE, Marjlar)

```sql
SELECT hisse_senedi_kodu AS kod, oran, deger
FROM hisse_finansal_tablolari_finansal_oranlari
WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
  AND yil = {YIL} AND ay = {AY}
  AND oran IN ('Özkaynak Karlılığı', 'Brüt Kar Marjı', 'Net Kar Marjı', 'FAVÖK Marjı')
ORDER BY hisse_senedi_kodu, oran
LIMIT 100
```

## Broker Tahminleri ve Hedef Fiyatlar

```sql
SELECT hisse_senedi_kodu AS kod, araci_kurum, tavsiye, hedef_fiyat, tarih
FROM hisse_senedi_araci_kurum_hedef_fiyatlari
WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
ORDER BY hisse_senedi_kodu, tarih DESC
LIMIT 100
```

```sql
SELECT hisse_senedi_kodu AS kod, yil, araci_kurum, net_kar_tahmini, ciro_tahmini
FROM hisse_senedi_araci_kurum_tahminleri
WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}']) AND yil >= 2025
ORDER BY hisse_senedi_kodu, yil, araci_kurum
LIMIT 100
```

---

# 🟡 ARŞİV: Eski Sorgular (v2.4, referans)

> Bu sorgular artık tam taramada kullanılmıyor.
> Tek hisse detaylı analizinde veya geçmiş uyumluluk için referans.

## [ARŞİV] Sorgu 1: Ön Filtreli Hisse Listesi

```sql
SELECT
  hs.kod, hs.baslik AS sirket_adi, s.baslik AS sektor,
  hs.finansal_tablo_sablonu AS sablon, hs.piyasa_degeri, hs.son_fiyat
FROM hisse_senetleri hs
LEFT JOIN sektorler s ON s.id = hs.sektor_id
WHERE hs.piyasa_degeri > 3000000000
  AND hs.finansal_tablo_sablonu = 'default'
ORDER BY hs.piyasa_degeri DESC
LIMIT 100 OFFSET 0
```

## [ARŞİV] Sorgu 2: TTM Gelir Tablosu

```sql
SELECT ft.hisse_senedi_kodu AS kod, ft.donem,
  MAX(CASE WHEN fk.baslik = 'Satış Gelirleri' THEN ft.deger END) AS ciro,
  MAX(CASE WHEN fk.baslik = 'Brüt Kar (Zarar)' THEN ft.deger END) AS brut_kar,
  MAX(CASE WHEN fk.baslik = 'Esas Faaliyet Karı (Zararı)' THEN ft.deger END) AS faal_kar,
  MAX(CASE WHEN fk.baslik = 'Ana Ortaklık Payları' THEN ft.deger END) AS net_kar
FROM hisse_finansal_tablolari ft
JOIN hisse_finansal_tablolari_finansal_kalemleri fk ON fk.id = ft.finansal_kalem_id
WHERE ft.hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
  AND ft.donem IN ('{SON_DONEM}', '{ONCEKI_DONEM}')
  AND ft.tablo_tipi = 'gelir_tablosu'
GROUP BY ft.hisse_senedi_kodu, ft.donem
ORDER BY ft.hisse_senedi_kodu, ft.donem DESC
```
⚠️ NOT: Bu sorgu eski şema (`hisse_finansal_tablolari_finansal_kalemleri`) kullanıyor.
Yeni şemada `hisse_finansal_tablolari_gelir_tablosu_kalemleri` tablosu doğrudan kalem isimlerini içeriyor.

## [ARŞİV] Sorgu 11: Tarihsel Çarpanlar (3Y Ortalama)

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
    ROUND(fd_favok::numeric, 2) AS son_fd_favok
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
  o.ort_fd_favok_3y, s.son_fd_favok
FROM ort o JOIN son s ON s.hisse_senedi_kodu = o.hisse_senedi_kodu
ORDER BY fk_iskonto_pct DESC NULLS LAST
```
→ Artık Sorgu 14'ün ort/son CTE'leri ile aynı işi yapıyor. Tek hisse detaylı çarpan analizinde kullanılabilir (FD/FAVÖK dahil olduğu için).

## [ARŞİV] Sorgu 11b: Sektör Medyan Çarpanları

```sql
SELECT s.baslik AS sektor,
  COUNT(DISTINCT tc.hisse_senedi_kodu) AS hisse_sayisi,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tc.fk)
    FILTER (WHERE tc.fk > 0 AND tc.fk < 80)::numeric, 2) AS medyan_fk,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tc.pddd)
    FILTER (WHERE tc.pddd > 0)::numeric, 2) AS medyan_pddd
FROM hisse_senedi_tarihsel_carpanlar tc
JOIN hisse_senetleri hs ON hs.kod = tc.hisse_senedi_kodu
JOIN sektorler s ON s.id = hs.sektor_id
WHERE tc.tarih_europe_istanbul >= '{SON_5_GUN}'
GROUP BY s.baslik
HAVING COUNT(DISTINCT tc.hisse_senedi_kodu) >= 3
ORDER BY s.baslik
```

## [ARŞİV] Sorgu 11c: Son Günün Çarpanları (Yedek)

```sql
SELECT DISTINCT ON (hisse_senedi_kodu)
  hisse_senedi_kodu AS kod, tarih_europe_istanbul AS tarih,
  ROUND(fk::numeric, 2) AS fk,
  ROUND(pddd::numeric, 2) AS pddd,
  ROUND(fd_favok::numeric, 2) AS fd_favok
FROM hisse_senedi_tarihsel_carpanlar
WHERE hisse_senedi_kodu = ANY(ARRAY['{KODLAR}'])
ORDER BY hisse_senedi_kodu, tarih_europe_istanbul DESC
```
