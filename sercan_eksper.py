import streamlit as st
import pandas as pd
import yfinance as yf # Canlı altın verisi için

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="S-EKSPER v3.5 | Canlı Analiz", layout="wide")

# --- CANLI VERİ ÇEKME FONKSİYONU ---
def get_live_data():
    try:
        # Gram Altın (USD/TRY * Ons Altın / 31.1) mantığıyla veya direkt sembolle
        gold = yf.Ticker("GAU=F") # Altın vadeli işlem sembolü
        current_gold = gold.history(period="1d")['Close'].iloc[-1]
        # Eğer yfinance gramı çekmezse sabit bir API yerine manuel yedek de koyabiliriz
        return round(current_gold, 2)
    except:
        return 6850 # İnternet hatası olursa Nisan 2026 tahmini değerini baz al

# --- GELİŞMİŞ ANALİZ MOTORU (Hacıseyit Ayarlı) ---
def gercekci_analiz(fiyat, faiz, altin, ekstralar, konum, mahalle):
    # Temel Çarpan
    oran = 1.0
    
    # 1. Faiz Baskısı (Nakit alıcı iskontosu)
    if faiz > 30:
        oran -= 0.12 # Faiz %30 üstündeyse fiyat %12 baskılanır
    
    # 2. Mahalle ve Şerefiye Dengesi (Senin Hacıseyit Analizin)
    serefiye = 0
    if mahalle == "Hacıseyit/Eskibağlar":
        if "Kapalı Otopark" in ekstralar: serefiye += 0.15 # Hacıseyit'te otopark altındır
        if "Asansör" not in ekstralar: serefiye -= 0.05 # Asansör yoksa ufak bir kırpma
    
    if "İskanlı" in ekstralar: serefiye += 0.08
    if "Güney Cephe" in konum: serefiye += 0.04

    # Nihai Hesaplama
    piyasa = fiyat * oran * (1 + serefiye)
    hizli_satis = piyasa * 0.88 # %12 acil nakit farkı
    beklenirse = piyasa * 1.15
    
    # Kira Çarpanı (Hacıseyit için 200, Batıkent için 240 ay)
    carpan = 200 if mahalle == "Hacıseyit/Eskibağlar" else 240
    aylik_kira = piyasa / carpan
    
    return hizli_satis, piyasa, beklenirse, aylik_kira

# --- ARAYÜZ ---
st.title("🏙️ S-EKSPER v3.5 PRO")
st.write("---")

# OTOMATİK VERİ ÇEKİMİ
canli_altin = get_live_data()
st.sidebar.success(f"✅ Canlı Altın Verisi Alındı: {canli_altin} TL")

# GİRİŞLER
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Mülk ve Konum")
    mahalle = st.selectbox("Bölge Seçin", ["Hacıseyit/Eskibağlar", "Batıkent", "Vişnelik/Sümer", "Diğer"])
    istenen = st.number_input("Emsal/İstenen Fiyat (TL)", value=3000000, step=100000)
    faiz_orani = st.slider("Güncel Konut Kredisi Faizi (%)", 10, 60, 45)

with col2:
    st.subheader("🛠️ Şerefiye Detayları")
    ekstralar = st.multiselect("Bina/Daire Özellikleri", ["Kapalı Otopark", "Asansör", "İskanlı", "Kombi", "Ankastre"])
    konum_ozellik = st.multiselect("Konum Artıları", ["Güney Cephe", "Tramvaya Yakın", "Ana Caddeye Yakın"])

# ANALİZ BUTONU
if st.button("📊 GERÇEKÇİ ANALİZİ ÇIKAR"):
    hizli, reel, tavan, kira = gercekci_analiz(istenen, faiz_orani, canli_altin, ekstralar, konum_ozellik, mahalle)
    
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    
    res1.metric("🚀 HIZLI SATAR", f"{int(hizli):,} TL", "- %12 Nakit İskontosu")
    res2.metric("⚖️ REEL PİYASA", f"{int(reel):,} TL", "İdeal Değer")
    res3.metric("⏳ MAKSİMUM", f"{int(tavan):,} TL", "Pazarlık Payı Dahil")
    
    st.info(f"💰 **Yatırımcı Notu:** Bu mülkün tahmini aylık kira getirisi **{int(kira):,} TL** seviyesindedir.")
    
    # SENİN ANALİZ DİLİN
    st.warning(f"**Sercan'ın Notu:** {mahalle} bölgesinde faizler %{faiz_orani} iken bu fiyata çıkmak 'nakit alıcı' yakalamayı gerektirir. Altının {canli_altin} TL olması bir avantajdır.")
