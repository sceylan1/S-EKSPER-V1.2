import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="S-EKSPER v8.0 | Profesyonel Raporlama", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #121212; color: #ffffff; }
    .report-card { background-color: #1e1e1e; padding: 25px; border-radius: 15px; border: 1px solid #333; margin-bottom: 20px; }
    .price-large { font-size: 48px; font-weight: bold; color: #ffffff; }
    .score-circle { border: 5px solid #ff2b5e; border-radius: 50%; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; }
    .stButton>button { background-color: #ff2b5e; color: white; border-radius: 8px; width: 100%; font-weight: bold; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- ESKİŞEHİR MAHALLE VERİ BANKASI (GİZLİ ANALİZ) ---
ESKISEHIR_DATA = {
    "Erenköy": {"ses": 1.05, "yatirim_skoru": 86, "ilce": "Odunpazarı", "ilce_skoru": 59, "deprem": "0.29g (1. Bölge)"},
    "Esentepe": {"ses": 1.0, "yatirim_skoru": 78, "ilce": "Tepebaşı", "ilce_skoru": 65, "deprem": "0.25g"},
    "Batıkent": {"ses": 1.35, "yatirim_skoru": 92, "ilce": "Tepebaşı", "ilce_skoru": 65, "deprem": "0.22g"},
    "Vişnelik": {"ses": 1.5, "yatirim_skoru": 95, "ilce": "Odunpazarı", "ilce_skoru": 59, "deprem": "0.28g"},
    "Hacıseyit": {"ses": 1.1, "yatirim_skoru": 82, "ilce": "Tepebaşı", "ilce_skoru": 65, "deprem": "0.24g"}
}

# --- CANLI EKONOMİK VERİ ---
@st.cache_data(ttl=600)
def get_market_data():
    try:
        ons = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
        usd = yf.Ticker("USDTRY=X").history(period="1d")['Close'].iloc[-1]
        gram = (ons / 31.1035) * usd
        return round(gram, 2), 45.5
    except: return 6850.0, 45.0

# --- FORM VE GİRİŞLER ---
gram, faiz = get_market_data()

st.title("🛡️ S-EKSPER v8.0 | Stratejik Analiz Paneli")
st.sidebar.write(f"🟡 Altın: **{gram} TL** | 🏠 Faiz: **%{faiz}**")

# HARİTA ÜZERİNDEN SEÇİM SİMÜLASYONU
mahalle_secimi = st.selectbox("📍 Eskişehir Haritası / Mahalle Seçimi", list(ESKISEHIR_DATA.keys()))
mahalle_bilgi = ESKISEHIR_DATA[mahalle_secimi]

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Mülk Özellikleri")
    konut_tipi = st.radio("Konut Tipi", ["Daire", "Müstakil"], horizontal=True)
    durum = st.radio("Kullanım Durumu", ["Mülk Sahibi", "Kiracı", "Boş"], horizontal=True)
    yapi = st.radio("Yapı Durumu", ["Bakımlı", "Standart", "Tadilatlı"], horizontal=True)
    m2 = st.number_input("Brüt Alan (m²)", value=100)
    emsal = st.number_input("Emsal Fiyat (TL)", value=3500000)

with col2:
    st.subheader("✨ Olanaklar ve Konum")
    konum_ozellikleri = st.multiselect("Konum Analizi", ["Toplu Ulaşıma Yakın", "Okullara Yakın", "Sağlık Hizmetlerine Yakın", "Merkeze Yakın", "Yeşil Alan Yakını"])
    isitma = st.selectbox("Isıtma", ["Doğalgaz/Kombi", "Yerden Isıtma", "Merkezi"])
    ekstralar = st.multiselect("Olanaklar", ["Asansör", "Isı Yalıtımı", "Otopark", "Güvenlik"])

# --- HESAPLAMA VE RAPORLAMA ---
if st.button("ANALİZİ TAMAMLA VE RAPORU ÇIKART"):
    # Gizli Katsayı Hesaplama
    final_multiplier = mahalle_bilgi['ses']
    if "Yerden Isıtma" in isitma: final_multiplier += 0.08
    if "Asansör" in ekstralar: final_multiplier += 0.05
    
    reel_deger = emsal * final_multiplier
    hizli_satis = reel_deger * 0.85
    uzun_vade = reel_deger * 1.10

    st.divider()

    # EKRAN GÖRÜNTÜSÜNDEKİ ANA RAPOR YAPISI
    r1, r2 = st.columns([2, 1])
    with r1:
        st.markdown(f"### {mahalle_secimi} Mah. Odunpazarı / Eskişehir")
        st.markdown(f"<div class='price-large'>{int(reel_deger):,} ₺</div>", unsafe_allow_html=True)
        st.write("3 - 6 Ay Arası Beklenirse Tahmini Değer")
        
        c_hizli, c_uzun = st.columns(2)
        c_hizli.info(f"**3 Aydan Kısa Süre**\n\n{int(hizli_satis):,} ₺")
        c_uzun.success(f"**6 - 12 Ay Arası**\n\n{int(uzun_vade):,} ₺")

    with r2:
        st.write("### Yatırım Skoru")
        st.markdown(f"<div class='score-circle'>{mahalle_bilgi['yatirim_skoru']}</div>", unsafe_allow_html=True)
        st.write("Bölgesel Deprem Tehlikesi:", mahalle_bilgi['deprem'])

    # YATIRIM VE BÖLGE ANALİZİ (RESİM 2'DEKİ GİBİ)
    st.divider()
    st.subheader("📊 Detaylı Analiz Kartları")
    a1, a2, a3, a4 = st.columns(4)
    
    a1.metric("Fiyat Analizi", "%75 Dönüşüm", help="Bölgedeki emsallere göre dönüşüm potansiyeli")
    a2.metric("Bölge Analizi", f"{mahalle_secimi}: {mahalle_bilgi['yatirim_skoru']}")
    a3.metric("Konum Analizi", f"{len(konum_ozellikleri)}/5 Artı Puan")
    a4.metric("Parsel Analizi", "İmar %100")

    # EMSAL TABLOSU (RESİM 4'DEKİ GİBİ)
    st.subheader("📋 Yakın Zamanlı Emsaller")
    emsal_df = pd.DataFrame({
        "Mesafe (m)": [350, 450, 600, 800],
        "Zaman (Gün)": [150, 30, 180, 90],
        "Alan (m²)": [m2, m2-5, m2+10, m2-2],
        "Değer (TL)": [reel_deger*0.95, reel_deger*0.98, reel_deger*1.05, reel_deger*0.92]
    })
    st.table(emsal_df)

st.sidebar.write("---")
st.sidebar.write("**Sercan CEYLAN**")
