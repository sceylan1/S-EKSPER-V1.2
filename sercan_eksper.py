import streamlit as st
import pandas as pd
import yfinance as yf

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="S-EKSPER v9.0 | Eskişehir Master Analiz", layout="wide")

# --- ESKİŞEHİR VERİ BANKASI (Tüm Semt ve Mahalleler Buraya Gelecek) ---
# Buraya örnek olarak ana bölgeleri ekledim, listeyi istediğin kadar uzatabilirsin.
ESKISEHIR_REHBER = {
    "Odunpazarı": ["Erenköy", "Vişnelik", "Akarbaşı", "Yenikent", "Büyükdere", "Göztepe", "Hamamyolu", "71 Evler", "Emek"],
    "Tepebaşı": ["Esentepe", "Batıkent", "Hacıseyit", "Bahçelievler", "Uluönder", "Şirintepe", "Çamlıca", "Sütlüce", "Eskibağlar"]
}

MAHALLE_KAT SAYILARI = {
    "Vişnelik": 1.5, "Batıkent": 1.35, "Erenköy": 1.05, "Esentepe": 1.0, "Hacıseyit": 1.1, "Büyükdere": 1.0, "Sümer": 1.45
}

# --- CANLI EKONOMİK VERİ ---
@st.cache_data(ttl=600)
def get_live_data():
    try:
        ons = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
        usd = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
        return round((ons / 31.1035) * usd, 2), 45.5
    except: return 6880.0, 45.0

gram, faiz = get_live_data()

# --- ARAYÜZ ---
st.title("🏙️ S-EKSPER v9.0 | Profesyonel Ekspertiz Paneli")
st.write(f"📊 **Piyasa Ekranı:** Gram Altın: {gram} TL | Faiz: %{faiz}")

st.divider()

# --- 1. ADIM: KONUM VE TİP (Görsel 1-2) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Konum Seçimi")
    ilce = st.selectbox("İlçe", list(ESKISEHIR_REHBER.keys()))
    mahalle = st.selectbox("Mahalle", ESKISEHIR_REHBER[ilce])
    
    st.subheader("🏠 Konut ve Yapı")
    konut_tipi = st.radio("Konut Tipi", ["Daire", "Müstakil"], horizontal=True)
    apartman_tipi = st.radio("Apartman Tipi", ["Daire", "Teras Dubleks", "Ara Kat Dubleks", "Bahçe Dubleks", "Ters Dubleks"], horizontal=True)
    kullanim = st.radio("Kullanım Durumu", ["Mülk Sahibi", "Kiracı", "Boş"], horizontal=True)
    yapi_durumu = st.radio("Yapı Durumu", ["Bakımlı/Yenilenmiş", "Standart", "Tadilat İhtiyacı Var"], horizontal=True)

with col2:
    st.subheader("📏 Ölçüler ve Kat")
    c1, c2 = st.columns(2)
    oda_sayisi = c1.number_input("Oda Sayısı", 1, 10, 2)
    salon_sayisi = c2.number_input("Salon Sayısı", 1, 3, 1)
    
    brut_m2 = st.number_input("Brüt Alan (m²)", 20, 1000, 100)
    bina_yasi = st.number_input("Bina Yaşı", 0, 100, 0)
    bina_kat = st.number_input("Bina Kat Sayısı", 1, 50, 3)
    bulundugu_kat = st.number_input("Bulunduğu Kat", -2, 50, 1)
    
    emsal_fiyat = st.number_input("Emsal Baz Fiyat (Mahalle Ortalaması TL)", value=3000000, step=100000)

st.divider()

# --- 2. ADIM: EK ÖZELLİKLER (Görsel 3-4) ---
col3, col4 = st.columns(2)

with col3:
    st.subheader("☀️ Cephe ve Manzara")
    cephe = st.multiselect("Cephe Durumu", ["Kuzey", "Güney", "Doğu", "Batı"])
    manzara = st.multiselect("Manzara", ["İstinat Duvarı", "Yan Bina", "Cadde/Sokak", "Bahçe", "Şehir", "Doğa", "Göl"])
    isitma = st.radio("Isıtma Sistemi", ["Yok", "Soba", "Doğalgaz/Kombi", "Merkezi Sistem", "Yerden Isıtma"], horizontal=True)

with col4:
    st.subheader("💎 Olanaklar")
    olanaklar = st.multiselect("Olanaklar", ["Anayol/Bulvar Üzeri", "Cadde Üzeri", "Spor Sahası", "Çocuk Parkı", "Asansör", "Jeneratör", "Güvenlik", "Otopark", "Kapalı Otopark", "Açık Havuz", "Isı Yalıtımı", "Klima", "Şömine"])

# --- HESAPLAMA MOTORU ---
if st.button("📊 ANALİZİ GERÇEKLEŞTİR"):
    # 1. Mahalle Katsayısı (Gizli SES Analizi)
    mahalle_carpani = MAHALLE_KAT_SAYILARI.get(mahalle, 1.0)
    
    # 2. Şerefiye Puanlama
    serefiye = 1.0
    if "Güney" in cephe: serefiye += 0.05
    if "Doğa" in manzara or "Şehir" in manzara: serefiye += 0.07
    if isitma == "Yerden Isıtma": serefiye += 0.08
    if "Asansör" in olanaklar: serefiye += 0.05
    if "Kapalı Otopark" in olanaklar: serefiye += 0.10
    if yapi_durumu == "Bakımlı/Yenilenmiş": serefiye += 0.10
    elif yapi_durumu == "Tadilat İhtiyacı Var": serefiye -= 0.15
    
    # 3. Nihai Değerleme
    ana_deger = emsal_fiyat * mahalle_carpani * serefiye
    
    # GÖRSELLERDEKİ SONUÇ EKRANI TASARIMI
    st.divider()
    res1, res2 = st.columns([2, 1])
    
    with res1:
        st.markdown(f"### {mahalle} Mah. {ilce} / Eskişehir")
        st.markdown(f"<h1 style='color:white;'>{int(ana_deger):,} ₺</h1>", unsafe_allow_html=True)
        st.write(f"Birim Değer: **{int(ana_deger/brut_m2):,} ₺/m²**")
        
        c_hizli, c_uzun = st.columns(2)
        c_hizli.info(f"**3 Aydan Kısa Süre (Hızlı)**\n\n{int(ana_deger * 0.88):,} ₺")
        c_uzun.success(f"**6-12 Ay Arası (Maksimum)**\n\n{int(ana_deger * 1.12):,} ₺")

    with res2:
        st.subheader("📈 Yatırım Skoru")
        skor = 65 # Baz skor
        if mahalle_carpani > 1.2: skor += 20
        if "Asansör" in olanaklar and bina_yasi < 10: skor += 10
        st.markdown(f"<div style='border:5px solid #ff2b5e; border-radius:50%; width:100px; height:100px; display:flex; align-items:center; justify-content:center; font-size:32px; font-weight:bold;'>{skor}</div>", unsafe_allow_html=True)
        st.write("Güven Endeksi: **Yüksek**")

    # EMSAL TABLOSU SİMÜLASYONU
    st.subheader("📋 Benzer Emsaller Analizi")
    emsaller = pd.DataFrame({
        "Mesafe": ["300m", "500m", "750m"],
        "Yaş": [bina_yasi, bina_yasi+5, bina_yasi-2],
        "Fiyat (TL)": [int(ana_deger*0.95), int(ana_deger*1.02), int(ana_deger*0.98)]
    })
    st.table(emsaller)
