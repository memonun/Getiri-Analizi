import streamlit as st
import requests
import pandas as pd
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Yatırım Karşılaştırıcı", layout="centered")
st.title("📊 Fon vs Döviz & Altın Karşılaştırma Aracı")

api_key = os.getenv("EXCHANGE_RATE_API_KEY")
print(f"API Anahtarı: {api_key}")

# Kullanıcıdan veri al
fon_adi = st.text_input("Fon Adı", value="V Mall Fon")
alim_tarihi = st.date_input("Alım Tarihi", value=date(2024, 4, 26), max_value=date.today())
fon_birim_fiyati = st.number_input("Alım Fiyatı (TL)", min_value=0.0, value=20100.0, step=1.0)
adet = st.number_input("Alınan Adet", min_value=1, value=50, step=1)
fon_guncel_fiyati = st.number_input("Fonun Güncel Fiyatı (TL)", min_value=0.0, value=35133.0, step=1.0)
st.info("📌 Not: Seçtiğiniz tarih için altın (XAU) verisi her zaman bulunamayabilir. Bu durumda altın kuru hesaplaması yapılamayabilir.")


submit = st.button("Karşılaştırmayı Göster")

# Fonksiyon: API'den kur bilgilerini al
def get_historical_rates(tarih_str):
    access_key = os.getenv('EXCHANGE_RATE_API_KEY')
    if not access_key:
        st.error("API anahtarı bulunamadı. Lütfen 'EXCHANGE_RATE_API_KEY' ortam değişkenini ayarlayın.")
        return None
    url = f"https://api.exchangerate.host/historical?access_key={access_key}&date={tarih_str}&source=TRY&currencies=USD,EUR,XAU"
    try:
        res = requests.get(url)
        data = res.json()
        if not data.get("success", True):
            st.error(f"API hatası: {data.get('error', {}).get('info', 'Bilinmeyen hata')}")
            return None
        return {
            "USD": 1/data["quotes"]["TRYUSD"],
            "EUR": 1/data["quotes"]["TRYEUR"],
            "XAU": 1/data["quotes"]["TRYXAU"]
        }
    except Exception as e:
        st.error(f"Kur verileri alınırken hata oluştu: {e}")
        return None
    
def get_live_rates():
    access_key = os.getenv('EXCHANGE_RATE_API_KEY')
    if not access_key:
        st.error("API anahtarı bulunamadı. Lütfen 'EXCHANGE_RATE_API_KEY' ortam değişkenini ayarlayın.")
    
    url = f"https://api.exchangerate.host/live?access_key={access_key}&source=TRY&currencies=USD,EUR,XAU"
    try:
        res = requests.get(url)
        data = res.json()
        if not data.get("success", True):
            st.error(f"API hatası: {data.get('error', {}).get('info', 'Bilinmeyen hata')}")
            return None
        return {
            "USD": 1/data["quotes"]["TRYUSD"],
            "EUR": 1/data["quotes"]["TRYEUR"],
            "XAU": 1/data["quotes"]["TRYXAU"]
        }
    except Exception as e:
        st.error(f"Kur verileri alınırken hata oluştu: {e}")
        return None
    
if submit:
    tarih_str = alim_tarihi.strftime("%Y-%m-%d")
    today_str = date.today().strftime("%Y-%m-%d")

    # Yatırım miktarı
    yatirim_tutari = fon_birim_fiyati * adet

    # Kur bilgileri
    historical_rates = get_historical_rates(tarih_str)
    current_rates = get_live_rates()

    if historical_rates and current_rates:
        alim_miktarlari = {
            "USD": yatirim_tutari / historical_rates["USD"],
            "EUR": yatirim_tutari / historical_rates["EUR"],
            "XAU": yatirim_tutari / historical_rates["XAU"],
        }

        bugunku_degerler = {
            "USD": alim_miktarlari["USD"] * current_rates["USD"],
            "EUR": alim_miktarlari["EUR"] * current_rates["EUR"],
            "XAU": alim_miktarlari["XAU"] * current_rates["XAU"],
            "Fon": adet * fon_guncel_fiyati,
        }

        getiri_oranlari = {
            k: (bugunku_degerler[k] - yatirim_tutari) / yatirim_tutari * 100 for k in bugunku_degerler
        }

        # Tablo oluştur
        df = pd.DataFrame([
            {
                "Yatırım Aracı": fon_adi,
                "Başlangıç Fiyatı": f"{fon_birim_fiyati:,.2f} TL",
                "Alınan Miktar": f"{adet} Adet",
                "Güncel Fiyat": f"{fon_guncel_fiyati:,.2f} TL",
                "Bugünkü Değer (TL)": f"{bugunku_degerler['Fon']:,.2f} TL",
                "Getiri Oranı (%)": f"%{getiri_oranlari['Fon']:.2f}"
            },
            {
                "Yatırım Aracı": "USD ($)",
                "Başlangıç Fiyatı": f"{historical_rates['USD']:,.2f} TL",
                "Alınan Miktar": f"{alim_miktarlari['USD']:,.2f} $",
                "Güncel Fiyat": f"{current_rates['USD']:,.2f} TL",
                "Bugünkü Değer (TL)": f"{bugunku_degerler['USD']:,.2f} TL",
                "Getiri Oranı (%)": f"%{getiri_oranlari['USD']:.2f}"
            },
            {
                "Yatırım Aracı": "EUR (€)",
                "Başlangıç Fiyatı": f"{historical_rates['EUR']:,.2f} TL",
                "Alınan Miktar": f"{alim_miktarlari['EUR']:,.2f} €",
                "Güncel Fiyat": f"{current_rates['EUR']:,.2f} TL",
                "Bugünkü Değer (TL)": f"{bugunku_degerler['EUR']:,.2f} TL",
                "Getiri Oranı (%)": f"%{getiri_oranlari['EUR']:.2f}"
            },
            {
                "Yatırım Aracı": "Ons Altın",
                "Başlangıç Fiyatı": f"{historical_rates['XAU']:,.2f} TL",
                "Alınan Miktar": f"{alim_miktarlari['XAU']:,.4f} ons",
                "Güncel Fiyat": f"{current_rates['XAU']:,.2f} TL",
                "Bugünkü Değer (TL)": f"{bugunku_degerler['XAU']:,.2f} TL",
                "Getiri Oranı (%)": f"%{getiri_oranlari['XAU']:.2f}"
            },
        ])

        st.success("İşte sonuçlar:")
        st.dataframe(df, use_container_width=True)

        st.caption("Veriler https://exchangerate.host üzerinden alınmaktadır.")
