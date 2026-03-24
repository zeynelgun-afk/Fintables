# BIST Değerleme Tarayıcısı — zeynelgun-afk/Fintables

**Borsa İstanbul hisseleri için sistematik değerleme ve tarama sistemi**

## Framework v8 (Mart 2026)

- **5 Yöntem Hedef Fiyat**: FD/FAVÖK, Forward F/K, PD/DD, Broker, Momentum
- **Faiz Bazlı Dinamik Sinyal**: Min AL (%52 mevcut TCMB + %15), Adil F/K (3.85x yılsonu konsensüs)
- **6 Yöntem Skorlama**: Değerleme, momentum, kâr sürprizi, PEG, katalist, makro risk
- **GYO/Holding Metodolojisi**: NAV iskontosunun çift filtresi (ucuzluk + momentum)

## Q4 2025 Tarama Sonuçları

| Sinyal | Hisse | Potansiyel | Hedef Fiyat | Skor |
|--------|-------|-----------|------------|------|
| 🥇 ALTIN | CATES | +200% | 22.50 | 9.2 |
| 💚 GÜÇLÜ AL | ESCOM | +150% | 18.75 | 8.7 |
| 🟢 AL | SRVGY | +87% | 12.30 | 7.1 |
| 🔵 TUT | A1CAP | +50% | 20.40 | 5.8 |
| ⚪ İZLE | ORGE | +22% | 8.90 | 4.2 |

**58 hisse tarandı | 7 ALTIN | 1 GÜÇLÜ AL | 3 AL | 8 TUT | 13 İZLE | 26 SAT**

## Dosyalar

```
├── SKILL.md                    # Framework v8 kuralları (tüm adımlar 1-26)
├── sql-sorgulari.md           # Fintables MCP SQL şablonları
├── backtest-bulgular.md       # 8 çeyrek backtest sonuçları
├── haber-katalist-avcisi.md   # Haber bazlı fiyatlanmamış fırsatlar
├── prompt-kullanim.md         # Kullanım örnekleri
├── config.json                # Faiz parametreleri, tarihler
├── scripts/
│   └── pipeline_v25.py        # Otomatik tarama (Fintables → Excel)
├── data/
│   ├── q4_2025_sonuclar.csv   # Q4 2025 tarama çıktısı
│   ├── son_tarama.csv          # Son çeyrek hedef fiyatlı
│   └── arsiv/
│       └── 2025_Q4.csv        # Tarihsel arşiv
└── docs/
    └── sektor-detay.md         # Sektör-spesifik metodoloji
```

## Faiz Parametreleri (Mart 2026)

```
Mevcut TCMB Faizi:     %37.0  (Min AL eşiği = %52)
Forward Faiz (yılsonu): %30.0  (Adil F/K = 3.85x)
Faiz Rejimi:           SABİT  (Jeopolitik riskler)
```

## Backtested Performans

- **Faiz İndirimi Döneminde** (Q1 2023, Q1 2025): α+65.5% vs α+5.5% (fark +59.9 puan)
- **Faiz Sabit Döneminde** (Q2-Q4 2024): α+2.4%
- **Boğa Pazarında** (Q1 2023): α-9.4% (konsensüs uyarı)
- **Katalistli vs Katalistsiz**: +59.9 puan fark (Faz 3 zorunlu)

## Kullanım

```bash
# Full tarama (adım 0-9)
python scripts/pipeline_v25.py --donem Q4_2025 --test

# Belirli hisse
python scripts/pipeline_v25.py --kod THYAO ASELS SRVGY

# Excel raporu
python scripts/pipeline_v25.py --output BIST_Q4_2025_6YONTEM_TARAMA.xlsx
```

## Temel İlkeler

✅ **Deterministik**: Aynı veri → aynı çıktı  
✅ **Adım Atlamayı Reddeder**: Faz 1-3 tam uygulanır  
✅ **MCP Veri**: Fintables gerçek finansal tabloları  
✅ **Framework Entegrasyonu**: Bulgu doğrulandı mı → skill dosyası güncellendi  

---

**Son Güncelleme**: 24 Mart 2026 | Framework v8.1 | Python 3.10+
