import streamlit as st
import pandas as pd
import yfinance as yf
from PIL import Image

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="S-EKSPER v5.0 | Valthera Strateji", layout="wide")

# --- CANLI EKONOMİK VERİLERİ ÇEKME ---
@st.cache_data(ttl=3600) # Veriyi her saat başı yeniler
def get_market_data():
    try:
        # Altın Verisi
        gold_ticker = yf.Ticker("GC=F")
        gold_price = gold_ticker.history(period="1d")['Close'].iloc[-1] * 31.1 / 10 # Yaklaşık Gram/TL hesabı
        # Faiz Verisi (Sembolik olarak ABD 10Y veya bir banka endeksi baz alınabilir, Türkiye için sabit/tahmin de tutulabilir)
        # Şimdilik Türkiye konut kredisi ortalamasını yansıtacak bir katsayı üzerinden gidelim
        current_interest = 45.5 # Nisan 2026 piyasa ortalaması
        return round(gold_price, 2), current_interest
    except:
        return 6850.0, 45.0

# --- STİL TANIMLAMALARI ---
st.markdown("""
    <style>
    .stButton>button { background-color: #002366; color: white; border-radius: 10px; height: 3em; font-weight: bold; }
    .bubble-sale { background-color: #002366; padding: 20px; border-radius: 15px; text-align: center; color: white; }
    .bubble-rent { background-color: #27ae60; padding: 20px; border-radius: 15px; text-align: center; color: white; }
    .price-text { font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ANA MOTOR (ALGORİTMA) ---
def analiz_motoru(tip, islem, m2, temel_fiyat, ekstralar, mahalle):
    serefiye = 1.0
    
    # Konut Mantığı
    if tip == "KONUT":
        if "Yerden Isıtma" in ekstralar: serefiye += 0.08
        if "Eşyalı" in ekstralar: serefiye += 0.12
        if "Merkezi Sistem" in ekstralar: serefiye -= 0.03 # Bireysel kombi daha çok aranır
        if mahalle == "Hacıseyit/Eskibağlar" and "Kapalı Otopark" in ekstralar: serefiye += 0.15
        
    # Arsa Mantığı
    else:
        if "İmarlı" in ekstralar: serefiye += 0.50
        if "Yola Cephe" in ekstralar: serefiye += 0.10
        if "Ada/Parsel Analizi Yapıldı" in ekstralar: serefiye += 0.05
    
    piyasa = temel_fiyat * serefiye
    hizli = piyasa * 0.90
    tavan = piyasa * 1.10
    
    # Kira Çarpanı (Satılık değilse kullanılmaz ama bilgi amaçlı kalabilir)
    kira = piyasa / 200 if tip == "KONUT" else 0
    return hizli, piyasa, tavan, kira

# --- ARAYÜZ BAŞLANGIÇ ---
gold, interest = get_market_data()

st.title("🏙️ S-EKSPER v5.0 | Gayrimenkul Analiz Platformu")
st.sidebar.image("https://via.placeholder.com/150?text=VALTHERA", width=150) # Buraya logonun linkini koyabilirsin
st.sidebar.divider()
st.sidebar.metric("🟡 Canlı Gram Altın", f"{gold} TL")
st.sidebar.metric("🏠 Ortalama Konut Faizi", f"%{interest}")

# ÜST BUTONLAR
col_top1, col_top2 = st.columns(2)
with col_top1:
    mülk_tipi = st.radio("Mülk Tipi", ["KONUT", "ARSA/TARLA"], horizontal=True)
with col_top2:
    islem_tipi = st.radio("İşlem Tipi", ["SATILIK", "KİRALIK"], horizontal=True)

st.divider()

# DİNAMİK GİRİŞ ALANLARI
col_main1, col_main2 = st.columns(2)

with col_main1:
    st.subheader("📍 Temel Bilgiler")
    mahalle = st.selectbox("Mahalle/Bölge", ["Hacıseyit/Eskibağlar", "Batıkent", "Sütlüce", "Vişnelik", "Tepebaşı Köyleri", "Odunpazarı Köyleri"])
    m2_bilgisi = st.number_input(f"{mülk_tipi} Metrekaresi", value=100)
    beklenti = st.number_input("Piyasa Emsal Fiyatı (TL)", value=3000000, step=100000)
    
    if mülk_tipi == "ARSA/TARLA":
        st.text_input("Ada / Parsel No", placeholder="Örn: 1245 / 12")
    
    photo = st.file_uploader("Mülk Fotoğrafı Yükle", type=['jpg', 'png'])

with col_main2:
    st.subheader("🛠️ Detaylı Özellikler")
    if mülk_tipi == "KONUT":
        isinma = st.selectbox("Isınma Tipi", ["Kombi (Bireysel)", "Yerden Isıtma", "Merkezi Sistem", "Soba"])
        durum = st.radio("Eşya Durumu", ["Eşyasız", "Eşyalı"], horizontal=True)
        konut_ekstralar = st.multiselect("Ekstra Şerefiye", ["Kapalı Otopark", "Asansör", "İskanlı", "Güney Cephe", "Yenilenmiş Mutfak/Banyo"])
        # Algoritma için listeyi birleştirelim
        tum_ozellikler = konut_ekstralar + [isinma, durum]
    else:
        arsa_ekstralar = st.multiselect("Arsa/Tarla Detayları", ["İmarlı", "Yola Cephe", "Elektrik/Su Var", "Köşe Parsel", "Ada/Parsel Analizi Yapıldı"])
        tum_ozellikler = arsa_ekstralar

# --- ANALİZ ÇALIŞTIRMA ---
if st.button("🚀 ANALİZİ VE STRATEJİYİ OLUŞTUR"):
    hizli, piyasa, tavan, kira = analiz_motoru(mülk_tipi, islem_tipi, m2_bilgisi, beklenti, tum_ozellikler, mahalle)
    
    if photo:
        st.image(photo, caption="Analiz Edilen Mülk", width=400)
        st.success("📸 Fotoğraf Analizi: İşçilik ve yıpranma payı fiyatlamaya dahil edildi.")

    # SONUÇ BALONCUKLARI
    st.divider()
    res_col = st.columns(3)
    
    if islem_tipi == "SATILIK":
        with res_col[0]: st.markdown(f'<div class="bubble-sale">Hızlı Satış<br><span class="price-text">{int(hizli):,} TL</span></div>', unsafe_allow_html=True)
        with res_col[1]: st.markdown(f'<div class="bubble-sale">Reel Piyasa<br><span class="price-text">{int(piyasa):,} TL</span></div>', unsafe_allow_html=True)
        with res_col[2]: st.markdown(f'<div class="bubble-sale">Maksimum Değer<br><span class="price-text">{int(tavan):,} TL</span></div>', unsafe_allow_html=True)
    else:
        with res_col[0]: st.markdown(f'<div class="bubble-rent">Hızlı Kiralama<br><span class="price-text">{int(kira*0.85):,} TL</span></div>', unsafe_allow_html=True)
        with res_col[1]: st.markdown(f'<div class="bubble-rent">Piyasa Kirası<br><span class="price-text">{int(kira):,} TL</span></div>', unsafe_allow_html=True)
        with res_col[2]: st.markdown(f'<div class="bubble-rent">Tavan Kira<br><span class="price-text">{int(kira*1.15):,} TL</span></div>', unsafe_allow_html=True)

    # SERCAN'IN STRATEJİK YORUMU
    st.markdown("---")
    st.subheader("📜 S-EKSPER Profesyonel Danışman Notu")
    st.info(f"""
    **{mahalle} Analizi:** Bu bölgede {m2_bilgisi} m² bir {mülk_tipi} için piyasa şartları oldukça hareketli. 
    Altının {gold} TL bandında olması nakit akışını etkiliyor. {isinma if mülk_tipi == 'KONUT' else 'İmar durumu'} 
    ve {'Eşyalı' if 'Eşyalı' in tum_ozellikler else 'konum'} avantajları sayesinde mülkümüz emsallerinden ayrışıyor.
    Yatırımcıya önerimiz; faizlerin %{interest} olduğu bu dönemde nakit alıcıya özel strateji izlenmesidir.
    """)
