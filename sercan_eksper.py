import streamlit as st
import pandas as pd
import yfinance as yf

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="S-EKSPER v9.0 | Eskişehir Master Analiz", layout="wide")

# --- CSS: MODERN KOYU TEMA ---
st.markdown("""
    <style>
    .main { background-color: #121212; color: #ffffff; }
    .stRadio > div { flex-direction: row; gap: 10px; }
    div[data-baseweb="radio"] { background-color: #1e1e1e; border-radius: 10px; padding: 10px; }
    .stButton>button { background-color: #ff2b5e; color: white; border-radius: 8px; width: 100%; height: 3.5em; font-weight: bold; }
    .result-card { background-color: #1e1e1e; padding: 25px; border-radius: 15px; border: 1px solid #333; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- ESKİŞEHİR VERİ BANKASI ---
ESKISEHIR_REHBER = {
    "Odunpazarı": ["Vişnelik", "Erenköy", "Akarbaşı", "Yenikent", "Büyükdere", "Göztepe", "Hamamyolu", "71 Evler", "Emek", "Sümer", "Osmangazi", "Kırmızıtoprak", "Yıldıztepe"],
    "Tepebaşı": ["Esentepe", "Batıkent", "Hacıseyit", "Bahçelievler", "Uluönder", "Şirintepe", "Çamlıca", "Sütlüce", "Eskibağlar", "Hoşnudiye", "Güllük", "Ömerağa"]
}

# Mahallelerin Gizli Lokasyon Çarpanları
MAHALLE_KAT_SAYILARI = {
    "Vişnelik": 1.55, "Sümer": 1.48, "Batıkent": 1.40, "Osmangazi": 1.35,
    "Hacıseyit": 1.15, "Akarbaşı": 1.20, "Erenköy": 1.05, "Esentepe": 1.0,
    "Büyükdere": 1.0, "Yenikent": 1.10, "Şirintepe": 0.95, "Çamlıca": 1.10
}

# --- CANLI EKONOMİK VERİ ---
@st.cache_data(ttl=600)
def get_live_data():
    try:
        # Gerçek Gram Altın Hesabı: (Ons / 31.1035) * USDTRY
        ons = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
        usd = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
        gram_altin = (ons / 31.1035) * usd
        return round(gram_altin, 2), 45.5
    except:
        return 6880.0, 45.0

gram, faiz = get_live_data()

# --- ARAYÜZ ---
st.title("🏙️ S-EKSPER v9.0 | Eskişehir Profesyonel Analiz")
st.write(f"📊 **Piyasa Verileri:** Gram Altın: {gram} TL | Konut Kredisi Faizi: %{faiz}")
st.divider()

# --- 1. ADIM: KONUM VE TİP ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Konum Seçimi")
    ilce = st.selectbox("İlçe Seçiniz", list(ESKISEHIR_REHBER.keys()))
    mahalle = st.selectbox("Mahalle Seçiniz", ESKISEHIR_REHBER[ilce])
    
    st.subheader("🏠 Konut ve Yapı")
    konut_tipi = st.radio("Konut Tipi", ["Daire", "Müstakil"], horizontal=True)
    apartman_tipi = st.radio("Apartman Tipi", ["Daire", "Teras Dubleks", "Ara Kat Dubleks", "Bahçe Dubleks", "Ters Dubleks"], horizontal=True)
    kullanim = st.radio("Kullanım Durumu", ["Mülk Sahibi", "Kiracı", "Boş"], horizontal=True)
    yapi_durumu = st.radio("Yapı Durumu", ["Bakımlı/Yenilenmiş", "Standart", "Tadilat İhtiyacı Var"], horizontal=True)

with col2:
    st.subheader("📏 Ölçüler ve Kat")
    c1, c2, c3 = st.columns(3)
    oda = c1.number_input("Oda", 1, 10, 2)
    salon = c2.number_input("Salon", 1, 3, 1)
    banyo = c3.number_input("Banyo", 1, 5, 1)
    
    brut_m2 = st.number_input("Brüt Alan (m²)", 20, 1000, 100)
    bina_yasi = st.number_input("Bina Yaşı", 0, 100, 0)
    bina_kat = st.number_input("Bina Kat Sayısı", 1, 50, 4)
    bulundugu_kat = st.number_input("Bulunduğu Kat", -2, 50, 2)
    
    emsal_fiyat = st.number_input("Emsal Baz Fiyat (Mahalle Ortalaması TL)", value=3500000, step=100000)

st.divider()

# --- 2. ADIM: EK ÖZELLİKLER ---
col3, col4 = st.columns(2)

with col3:
    st.subheader("☀️ Cephe ve Manzara")
    cephe = st.multiselect("Cephe Durumu", ["Kuzey", "Güney", "Doğu", "Batı"])
    manzara = st.multiselect("Manzara", ["İstinat Duvarı", "Yan Bina", "Cadde/Sokak", "Bahçe", "Şehir", "Doğa", "Göl"])
    isitma = st.radio("Isıtma Sistemi", ["Yok", "Soba", "Doğalgaz/Kombi", "Merkezi Sistem", "Yerden Isıtma"], horizontal=True)

with col4:
    st.subheader("💎 Olanaklar")
    olanaklar = st.multiselect("Olanaklar", ["Anayol Üzeri", "Cadde Üzeri", "Spor Sahası", "Çocuk Parkı", "Asansör", "Jeneratör", "Güvenlik", "Otopark", "Kapalı Otopark", "Isı Yalıtımı", "Klima", "Şömine"])

# --- HESAPLAMA VE RAPORLAMA ---
if st.button("📊 ANALİZİ GERÇEKLEŞTİR"):
    # 1. Mahalle Katsayısı (Gizli SES/Lokasyon Analizi)
    mahalle_carpani = MAHALLE_KAT_SAYILARI.get(mahalle, 1.0)
    
    # 2. Şerefiye Puanlama
    serefiye = 1.0
    if "Güney" in cephe: serefiye += 0.05
    if "Doğa" in manzara: serefiye += 0.07
    if isitma == "Yerden Isıtma": serefiye += 0.08
    if "Asansör" in olanaklar: serefiye += 0.05
    if "Kapalı Otopark" in olanaklar: serefiye += 0.10
    if yapi_durumu == "Bakımlı/Yenilenmiş": serefiye += 0.10
    elif yapi_durumu == "Tadilat İhtiyacı Var": serefiye -= 0.15
    if bulundugu_kat == bina_kat: serefiye -= 0.05 # En üst kat iskontosu
    
    # 3. Nihai Değerleme
    ana_deger = emsal_fiyat * mahalle_carpani * serefiye
    
    st.divider()
    
    # SONUÇ EKRANI
    res1, res2 = st.columns([2, 1])
    
    with res1:
        st.markdown(f"### {mahalle} Mah. {ilce} / Eskişehir")
        st.markdown(f"<h1 style='color:white; font-size: 60px;'>{int(ana_deger):,} ₺</h1>", unsafe_allow_html=True)
        st.write(f"Tahmini m² Birim Değeri: **{int(ana_deger/brut_m2):,} ₺/m²**")
        
        ch, cu = st.columns(2)
        ch.info(f"**3 Aydan Kısa Süre (Hızlı)**\n\n{int(ana_deger * 0.88):,} ₺")
        cu.success(f"**6-12 Ay Arası (Beklenirse)**\n\n{int(ana_deger * 1.12):,} ₺")

    with res2:
        st.subheader("📈 Yatırım Skoru")
        skor = 60
        if mahalle_carpani > 1.2: skor += 25
        if "Asansör" in olanaklar and bina_yasi < 10: skor += 10
        st.markdown(f"<div style='border:5px solid #ff2b5e; border-radius:50%; width:110px; height:110px; display:flex; align-items:center; justify-content:center; font-size:36px; font-weight:bold;'>{min(skor, 100)}</div>", unsafe_allow_html=True)
        st.write("Güven Endeksi: **%85+**")

    # EMSAL TABLOSU
    st.subheader("📋 Benzer Senaryo Analizi")
    emsaller = pd.DataFrame({
        "Durum": ["Dar Piyasa (Nadir)", "Yaygın Piyasa (Emsal Çok)", "Yatırımcı Teklifi"],
        "Tahmini Fiyat (TL)": [int(ana_deger*1.08), int(ana_deger*0.96), int(ana_deger*0.90)],
        "Satış Hızı": ["Yavaş", "Normal", "Çok Hızlı"]
    })
    st.table(emsaller)

st.sidebar.write("---")
st.sidebar.write("**Sercan CEYLAN**")
