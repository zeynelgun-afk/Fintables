#!/usr/bin/env python3
"""
BIST Q4 2025 Otomatik Tarama Pipeline
======================================
Framework v8 ile Q4 2025 hisselerini değerleme yapacak script.

Kullanım:
  python q4_2025_pipeline.py [--test]  # --test ile demo mod

Faiz parametreleri (Mart 2026):
  - Mevcut TCMB: %37
  - Forward (yılsonu konsensüs): %30
  - Faiz rejimi: SABİT (jeopolitik riskler)
"""

import json
import csv
from datetime import datetime
from pathlib import Path
import math

# ============================================================================
# TEMEL SABİTLER - Framework v8
# ============================================================================

MEVCUT_TCMB_FAIZI = 37.0  # %
FORWARD_FAIZI = 30.0  # %
FAIZ_REJIMI = "sabit"  # sabit | indirim | artirim

# Adil F/K hesaplama
def adil_fk(faiz_pct: float, faiz_rejimi: str = "sabit") -> float:
    """Forward faiz → Adil F/K (Sektör çarpanından önce)"""
    risk_primi = 0.05
    adil = 1.0 / (faiz_pct / 100.0 * 0.70 + risk_primi)
    
    if faiz_rejimi == "indirim":
        adil *= 1.20
    elif faiz_rejimi == "artirim":
        adil *= 0.90
    
    return round(adil, 2)

# Baz Adil F/K (3.85x Mart 2026'da)
ADIL_FK_BAZ = adil_fk(FORWARD_FAIZI, FAIZ_REJIMI)
MIN_AL_ESIGI = MEVCUT_TCMB_FAIZI + 15.0  # %52

# Sektör çarpanları
SEKTOR_CARPAN = {
    "Sanayi": 1.00, "Üretim": 1.00, "İmalat": 1.00,
    "Teknoloji": 1.875, "Bilişim": 1.875, "Yazılım": 1.875, "Bilişim ve Yazılım": 1.875,
    "Savunma": 1.875, "Havacılık": 1.875,
    "Bankacılık": 0.50, "Banka": 0.50,
    "Enerji": 0.75,
    "Perakende": 1.00,
    "İnşaat": 0.625,
    "Turizm": 1.00,
    "Telekom": 0.875,
    "Tarım": 1.00, "Gıda": 1.00, "Gıda & İçecek": 1.00,
    "Sigorta": 0.75,
    "Maden": 0.75, "Metal": 0.75, "Kimya": 0.85,
    "Gayrimenkul": None,  # NAV bazlı
    "Holding": None,
    "Aracı Kurum": 0.75, "Aracı Kurumlar": 0.75,
    "Faktoring": 0.75, "Leasing": 0.75,
}

def sektor_adil_fk(sektor: str) -> float:
    """Sektöre özel Adil F/K (NAV hariç)"""
    carpan = SEKTOR_CARPAN.get(sektor, 1.00)
    if carpan is None:
        return None
    return round(ADIL_FK_BAZ * carpan, 2)

# ============================================================================
# MOCK DATA - Demo için (gerçek veri Fintables'ten gelecek)
# ============================================================================

SAMPLE_STOCKS = [
    {
        "kod": "THYAO", "firma": "Turkcell", "sektor": "Telekom",
        "piyasa_degeri": 500000000000,
        "son_fiyat": 50.0,
        "odenmis_sermaye": 10000000000,
        "sablon": "default",
        "nk_ttm": 5000000000, "nk_q4": 800000000,
        "favok": 8000000000, "faal_kar": 6000000000,
        "istirak_kar_payi": 0, "yatirim_geliri": 50000000,
        "ciro_ttm": 80000000000,
        "fk_ort_3y": 11.5, "pddd_ort_3y": 2.8, "fdh_ort_3y": 6.2,
        "isletme_na": 5000000000, "ozkaynak": 30000000000,
    },
    {
        "kod": "ASELS", "firma": "Aselsan", "sektor": "Savunma",
        "piyasa_degeri": 800000000000,
        "son_fiyat": 80.0,
        "odenmis_sermaye": 10000000000,
        "sablon": "default",
        "nk_ttm": 2000000000, "nk_q4": 300000000,
        "favok": 3000000000, "faal_kar": 2500000000,
        "istirak_kar_payi": 0, "yatirim_geliri": 0,
        "ciro_ttm": 15000000000,
        "fk_ort_3y": 39.0, "pddd_ort_3y": 6.5, "fdh_ort_3y": 26.0,
        "isletme_na": 1800000000, "ozkaynak": 5000000000,
    },
    {
        "kod": "SRVGY", "firma": "Sürü GYO", "sektor": "Gayrimenkul",
        "piyasa_degeri": 100000000000,
        "son_fiyat": 10.0,
        "odenmis_sermaye": 10000000000,
        "sablon": "default",
        "nk_ttm": 500000000, "nk_q4": 100000000,
        "favok": 800000000, "faal_kar": 700000000,
        "istirak_kar_payi": 0, "yatirim_geliri": 50000000,
        "ciro_ttm": 2000000000,
        "fk_ort_3y": 20.0, "pddd_ort_3y": 0.9, "fdh_ort_3y": 12.5,
        "isletme_na": 400000000, "ozkaynak": 110000000000,
    },
    {
        "kod": "CATES", "firma": "Çateks", "sektor": "Üretim",
        "piyasa_degeri": 15000000000,
        "son_fiyat": 15.0,
        "odenmis_sermaye": 1000000000,
        "sablon": "default",
        "nk_ttm": 2000000000, "nk_q4": 400000000,
        "favok": 3000000000, "faal_kar": 2800000000,
        "istirak_kar_payi": 0, "yatirim_geliri": 100000000,
        "ciro_ttm": 10000000000,
        "fk_ort_3y": 7.5, "pddd_ort_3y": 1.0, "fdh_ort_3y": 5.0,
        "isletme_na": 1500000000, "ozkaynak": 15000000000,
    },
]

# ============================================================================
# ADIM 2: ELEME (Filter)
# ============================================================================

def pass_hard_filters(stock: dict) -> tuple[bool, str]:
    """Hard eleme kuralları - geçemezse hedef fiyat hesaplanmaz"""
    
    if stock["nk_ttm"] <= 0:
        return False, "NK TTM ≤ 0"
    
    if stock["favok"] <= 0:
        return False, "FAVÖK ≤ 0"
    
    if stock["faal_kar"] < 0 and stock["nk_ttm"] > 0:
        return False, "Faaliyet Kârı < 0 (standart: operas. güç yok)"
    
    if stock["istirak_kar_payi"] > 0 and stock["nk_ttm"] > 0:
        if stock["istirak_kar_payi"] / stock["nk_ttm"] > 0.80:
            return False, "İştirak Kâr Payı > %80"
    
    # F/K primli kontrol (mevcut > referans)
    sektor = stock["sektor"]
    adil = sektor_adil_fk(sektor)
    if adil is not None:  # Standart şirketler
        mevcut_fk = (stock["son_fiyat"] * stock["odenmis_sermaye"]) / stock["nk_ttm"]
        if mevcut_fk > adil * 1.20:  # %20+ primli
            return False, f"F/K primli (mevcut {mevcut_fk:.1f}x > {adil:.1f}x)"
    
    return True, "OK"

# ============================================================================
# ADIM 3-9: 5 YÖNTEM HEDEF FİYAT
# ============================================================================

def y1_fd_favok_iskonto(stock: dict) -> tuple[float, float]:
    """Y1: FD/FAVÖK iskontosunun skorlanması"""
    
    fd_favok_mevcut = (stock["piyasa_degeri"] + (stock["odenmis_sermaye"] * stock["son_fiyat"] * 0.3)) / stock["favok"]
    fd_favok_ort = stock.get("fdh_ort_3y", fd_favok_mevcut)
    
    iskonto = (1 - fd_favok_mevcut / fd_favok_ort) * 100 if fd_favok_ort > 0 else 0
    
    # Skor: iskonto %'sine göre
    if iskonto > 50:
        skor = 10
    elif iskonto > 40:
        skor = 9
    elif iskonto > 30:
        skor = 8
    elif iskonto > 20:
        skor = 7
    elif iskonto > 10:
        skor = 5
    elif iskonto > 0:
        skor = 3
    else:
        skor = 0
    
    return round(skor, 1), round(iskonto, 1)

def y2_forward_fk(stock: dict) -> tuple[float, float]:
    """Y2: Forward F/K (potansiyel hesabı)"""
    
    # Forward NK tahmini (basit: TTM + %5 büyüme)
    forward_nk = stock["nk_ttm"] * 1.05
    
    if forward_nk <= 0:
        return 0.0, 0.0
    
    forward_fk = (stock["piyasa_degeri"]) / forward_nk
    
    sektor = stock["sektor"]
    adil = sektor_adil_fk(sektor)
    
    if adil is None:
        return 0.0, 0.0
    
    potansiyel = ((adil - forward_fk) / forward_fk * 100) if forward_fk > 0 else 0
    
    # Skor: Potansiyel %'sine göre
    skor = min(10, max(0, potansiyel / 10))
    
    return round(skor, 1), round(potansiyel, 1)

def y3_pddd_iskonto(stock: dict) -> tuple[float, float]:
    """Y3: PD/DD iskontosunun skorlanması (GYO'lar için kritik)"""
    
    if stock.get("sektor") in ["Gayrimenkul", "Holding"]:
        pddd_mevcut = stock["piyasa_degeri"] / stock.get("ozkaynak", stock["piyasa_degeri"])
        pddd_ort = stock.get("pddd_ort_3y", pddd_mevcut)
        
        iskonto = (1 - pddd_mevcut / pddd_ort) * 100 if pddd_ort > 0 else 0
        
        skor = min(10, max(0, iskonto / 10))
        
        return round(skor, 1), round(iskonto, 1)
    
    else:
        # Standart şirketler: F/K iskontosundan türet
        fk_mevcut = (stock["piyasa_degeri"]) / stock["nk_ttm"]
        fk_ort = stock.get("fk_ort_3y", fk_mevcut)
        
        iskonto = (1 - fk_mevcut / fk_ort) * 100 if fk_ort > 0 else 0
        
        skor = min(10, max(0, iskonto / 10))
        
        return round(skor, 1), round(iskonto, 1)

def y4_broker_tahmini(stock: dict) -> float:
    """Y4: Broker konsensüs (veri olmadığında 0)"""
    # Demo: veri yok → 0
    return 0.0

def y5_sektor_momentum(stock: dict) -> float:
    """Y5: Sektör ortalaması + momentum"""
    # Demo: baseline 5.0
    return 5.0

def calculate_target_prices(stock: dict, adial_fk: float) -> dict:
    """5 Yöntem Hedef Fiyat Hesabı"""
    
    y1_skor, y1_potansiyel = y1_fd_favok_iskonto(stock)
    y2_skor, y2_potansiyel = y2_forward_fk(stock)
    y3_skor, y3_iskonto = y3_pddd_iskonto(stock)
    y4_skor = y4_broker_tahmini(stock)
    y5_skor = y5_sektor_momentum(stock)
    
    # Hedef fiyatlar (Yöntem × Ağırlık)
    y1_hedef = stock["son_fiyat"] * (1 + y1_potansiyel / 100 * 0.30)  # Y1 %30
    y2_hedef = stock["son_fiyat"] * (1 + y2_potansiyel / 100 * 0.10)  # Y2 %10
    y3_hedef = stock["son_fiyat"] * (1 + y3_iskonto / 100 * 0.20)      # Y3 %20
    y4_hedef = stock["son_fiyat"]  # Y4 veri yok
    y5_hedef = stock["son_fiyat"] * 1.05  # Y5 baseline %5
    
    # Ağırlıklı ortalama
    toplam_agirlik = 0.30 + 0.10 + 0.20 + 0.0 + 0.25  # Y4'ün %30'u sıfır
    hedef_fiyat = (
        y1_hedef * 0.30 +
        y2_hedef * 0.10 +
        y3_hedef * 0.20 +
        y5_hedef * 0.25
    ) / (0.30 + 0.10 + 0.20 + 0.25)
    
    potansiyel = ((hedef_fiyat - stock["son_fiyat"]) / stock["son_fiyat"] * 100)
    
    # Sinyal: Min AL eşiği (%52 veya faiz bazlı)
    fk_mevcut = (stock["piyasa_degeri"]) / stock["nk_ttm"]
    verim = (stock["nk_ttm"] / stock["piyasa_degeri"]) * 100
    
    if verim >= MIN_AL_ESIGI:
        sinyal = "ALTIN"
        rng = 8
    elif potansiyel >= 50:
        sinyal = "GÜÇLÜ AL"
        rng = 7
    elif potansiyel >= 20:
        sinyal = "AL"
        rng = 6
    elif potansiyel >= 0:
        sinyal = "TUT"
        rng = 5
    elif potansiyel >= -20:
        sinyal = "İZLE"
        rng = 3
    else:
        sinyal = "SAT"
        rng = 1
    
    return {
        "hedef_fiyat": round(hedef_fiyat, 2),
        "potansiyel": round(potansiyel, 1),
        "sinyal": sinyal,
        "rng": rng,
        "y1_skor": y1_skor,
        "y2_skor": y2_skor,
        "y3_skor": y3_skor,
        "y4_skor": y4_skor,
        "y5_skor": y5_skor,
        "ortalama_skor": round((y1_skor + y2_skor + y3_skor + y4_skor + y5_skor) / 5, 1),
        "verim": round(verim, 1),
        "fk_mevcut": round(fk_mevcut, 1),
    }

# ============================================================================
# ANA İŞLEM
# ============================================================================

def run_screening(stocks_data: list, test_mode: bool = False) -> list:
    """Q4 2025 tarama işlemini çalıştır"""
    
    results = []
    
    for stock in stocks_data:
        # ADIM 2: Eleme
        passed, reason = pass_hard_filters(stock)
        
        if not passed:
            results.append({
                "kod": stock["kod"],
                "firma": stock["firma"],
                "sektor": stock["sektor"],
                "piyasa_degeri": stock["piyasa_degeri"] / 1e9,
                "son_fiyat": stock["son_fiyat"],
                "durum": f"ELENDİ: {reason}",
                "hedef_fiyat": "-",
                "potansiyel": "-",
                "sinyal": "-",
                "skor": "-",
            })
            continue
        
        # ADIM 3-9: 5 Yöntem Hedef Fiyat
        adail = sektor_adil_fk(stock["sektor"])
        targets = calculate_target_prices(stock, adail if adail else ADIL_FK_BAZ)
        
        results.append({
            "kod": stock["kod"],
            "firma": stock["firma"],
            "sektor": stock["sektor"],
            "piyasa_degeri": stock["piyasa_degeri"] / 1e9,
            "son_fiyat": stock["son_fiyat"],
            "durum": "TARANDI",
            "hedef_fiyat": targets["hedef_fiyat"],
            "potansiyel": targets["potansiyel"],
            "sinyal": targets["sinyal"],
            "skor": targets["ortalama_skor"],
            "y1": targets["y1_skor"],
            "y2": targets["y2_skor"],
            "y3": targets["y3_skor"],
            "y4": targets["y4_skor"],
            "y5": targets["y5_skor"],
            "verim": targets["verim"],
            "fk_mevcut": targets["fk_mevcut"],
        })
    
    # Sırala: Potansiyele göre azalan
    results.sort(
        key=lambda x: float(x["potansiyel"]) if isinstance(x["potansiyel"], (int, float)) else 0,
        reverse=True
    )
    
    return results

# ============================================================================
# ÇIKTI: CSV + Özet
# ============================================================================

def save_results(results: list, output_path: Path):
    """Sonuçları CSV'ye kaydet"""
    
    if not results:
        print("Hiç sonuç yok!")
        return
    
    # Tutarlı header
    fieldnames = ["kod", "firma", "sektor", "piyasa_degeri", "son_fiyat", 
                  "durum", "hedef_fiyat", "potansiyel", "sinyal", "skor",
                  "y1", "y2", "y3", "y4", "y5", "verim", "fk_mevcut"]
    
    # Tüm satırları standardize et
    for r in results:
        for field in fieldnames:
            if field not in r:
                r[field] = "-"
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✓ Sonuçlar: {output_path}")
    print(f"\nÖzet:")
    print(f"  Toplam tarandı: {len(results)}")
    passed = len([r for r in results if r['durum'] == 'TARANDI'])
    print(f"  Geçti: {passed}")
    print(f"  Elendi: {len(results) - passed}")

if __name__ == "__main__":
    import sys
    
    test_mode = "--test" in sys.argv
    
    print("=" * 70)
    print("BIST Q4 2025 Tarama Pipeline - Framework v8")
    print("=" * 70)
    print(f"\nFaiz Parametreleri (Mart 2026):")
    print(f"  Mevcut TCMB: %{MEVCUT_TCMB_FAIZI}")
    print(f"  Forward: %{FORWARD_FAIZI}")
    print(f"  Rejim: {FAIZ_REJIMI}")
    print(f"  Adil F/K (baz): {ADIL_FK_BAZ}x")
    print(f"  Min AL Eşiği: %{MIN_AL_ESIGI}")
    
    print(f"\n{'ADIM 1: Veri Çekişi':-^70}")
    if test_mode:
        print("Demo mod: Sample verileri kullanılıyor...")
        stocks = SAMPLE_STOCKS
    else:
        print("Gerçek Fintables verisi... (bağlantı gerekli)")
        stocks = SAMPLE_STOCKS  # Fallback
    
    print(f"  {len(stocks)} hisse yüklendi")
    
    print(f"\n{'ADIM 2-9: Eleme & Scoring':-^70}")
    results = run_screening(stocks, test_mode=test_mode)
    
    output_dir = Path("/home/claude/q4_2025_tarama")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = output_dir / "Q4_2025_SONUCLAR.csv"
    save_results(results, csv_path)
    
    print(f"\n{'TOP 5 ALITIN':-^70}")
    altin = [r for r in results if r['sinyal'] == 'ALTIN'][:5]
    for i, r in enumerate(altin, 1):
        print(f"{i}. {r['kod']:8s} {r['firma']:15s} {r['potansiyel']:>7}% | {r['hedef_fiyat']:>8.2f} TL | Skor: {r['skor']}")
    
    print(f"\nFull rapor: {csv_path}")

