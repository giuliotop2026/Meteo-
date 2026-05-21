# ==========================================
# PROTOCOLLO GRANITO 3.0 - PIAZZATO BLINDATO
# TEMA LIGHT PROFESSIONAL + MOTORE GEOLOCALIZZATO + REFRESH NATIVO
# ==========================================

import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime
import altair as alt
import time

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(
    page_title="GRANITO 3.0 - METEO LIGHT",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. STILE CSS LIGHT PROFESSIONAL
st.markdown("""
    <style>
    .main { background-color: #f8fafc; color: #1e293b; }
    h1, h2, h3 { color: #1e293b !important; font-family: 'Helvetica', sans-serif; font-weight: 700; }
    [data-testid="stMetric"] {
        background-color: #ffffff; border: 1px solid #e2e8f0; padding: 20px;
        border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border-left: 6px solid #10b981;
    }
    [data-testid="stMetricValue"] { color: #1e293b !important; font-weight: 800; }
    [data-testid="stMetricLabel"] { color: #64748b !important; font-size: 16px; font-weight: 600; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px 8px 0 0; padding: 10px 20px; color: #64748b; }
    .stTabs [aria-selected="true"] { background-color: #10b981 !important; color: white !important; font-weight: bold; }
    section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

API_URL = "https://api.open-meteo.com/v1/forecast"
GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"

# SESSION STATE PER IL LUOGO
if "LATITUDE" not in st.session_state:
    st.session_state.LATITUDE = 40.828
if "LONGITUDE" not in st.session_state:
    st.session_state.LONGITUDE = 14.333
if "NOME_CITTA" not in st.session_state:
    st.session_state.NOME_CITTA = "SAN GIORGIO A CREMANO"

# FUNZIONE GEOCODING
def OTTIENI_COORDINATE(CITTA):
    PARAMS_GEO = {
        "name": CITTA,
        "count": 1,
        "language": "it",
        "format": "json"
    }
    try:
        RES = requests.get(GEO_URL, params=PARAMS_GEO)
        RES.raise_for_status()
        DATA = RES.json()
        if "results" in DATA and len(DATA["results"]) > 0:
            return DATA["results"][0]["latitude"], DATA["results"][0]["longitude"], DATA["results"][0]["name"].upper()
        else:
            return None, None, None
    except:
        return None, None, None

# 3. MOTORE DI ESTRAZIONE INVIOLABILE
@st.cache_data(ttl=60)
def SCANSIONA_ABISSO(LAT, LON):
    PARAMS = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": "temperature_2m,precipitation,wind_speed_10m",
        "minutely_15": "precipitation",
        "models": "ecmwf_ifs04,gfs_seamless,icon_seamless",
        "timezone": "Europe/Rome",
        "forecast_days": 3
    }
    try:
        RESPONSE = requests.get(API_URL, params=PARAMS)
        RESPONSE.raise_for_status()
        return RESPONSE.json()
    except:
        return None

def CALCOLA_CEMENTO(DF, TIPO):
    DF = DF.fillna(0.0) # SCUDO ANTI-VUOTO
    if TIPO == "TEMP":
        return (DF["temperature_2m_ecmwf_ifs04"] * 0.50) + (DF["temperature_2m_gfs_seamless"] * 0.30) + (DF["temperature_2m_icon_seamless"] * 0.20)
    elif TIPO == "RAIN":
        return (DF["precipitation_ecmwf_ifs04"] * 0.50) + (DF["precipitation_gfs_seamless"] * 0.30) + (DF["precipitation_icon_seamless"] * 0.20)
    elif TIPO == "WIND":
        return (DF["wind_speed_10m_ecmwf_ifs04"] * 0.50) + (DF["wind_speed_10m_gfs_seamless"] * 0.30) + (DF["wind_speed_10m_icon_seamless"] * 0.20)

# SIDEBAR: IL NUOVO MOTORE DI RICERCA
st.sidebar.markdown("### 📍 CAMBIA COORDINATE")
CITTA_INPUT = st.sidebar.text_input("INSERISCI CITTÀ", value=st.session_state.NOME_CITTA)
if st.sidebar.button("SCANSIONA NUOVO LUOGO", type="primary"):
    NUOVA_LAT, NUOVA_LON, NOME_REALE = OTTIENI_COORDINATE(CITTA_INPUT)
    if NUOVA_LAT and NUOVA_LON:
        st.session_state.LATITUDE = NUOVA_LAT
        st.session_state.LONGITUDE = NUOVA_LON
        st.session_state.NOME_CITTA = NOME_REALE
        st.cache_data.clear()
        st.sidebar.success(f"LUOGO BLINDATO: {NOME_REALE}")
    else:
        st.sidebar.error("ERRORE: CITTÀ NON TROVATA O FAVORITO DI CARTA.")

# 4. INTERFACCIA PRINCIPALE E CALCOLO DEL VINCITORE NASCOSTO
st.title("⚡ GRANITO 3.0 — PREVISIONE BLINDATA")
st.markdown(f"##### DENSITÀ TECNICA REALE SU: **{st.session_state.NOME_CITTA}**")

DATI_GREGGI = SCANSIONA_ABISSO(st.session_state.LATITUDE, st.session_state.LONGITUDE)

if DATI_GREGGI:
    # ELABORAZIONE FUSA NEL CEMENTO
    DF_ORARIO = pd.DataFrame(DATI_GREGGI["hourly"])
    DF_ORARIO["DATA_ORA"] = pd.to_datetime(DF_ORARIO["time"])
    DF_ORARIO["TEMP_CEMENTO"] = CALCOLA_CEMENTO(DF_ORARIO, "TEMP")
    DF_ORARIO["RAIN_CEMENTO"] = CALCOLA_CEMENTO(DF_ORARIO, "RAIN")
    DF_ORARIO["WIND_CEMENTO"] = CALCOLA_CEMENTO(DF_ORARIO, "WIND")
    
    DF_15MIN = pd.DataFrame(DATI_GREGGI["minutely_15"])
    DF_15MIN["DATA_ORA"] = pd.to_datetime(DF_15MIN["time"])
    DF_15MIN["RAIN_CEMENTO"] = CALCOLA_CEMENTO(DF_15MIN, "RAIN")
    
    ORA_ATTUALE = pd.Timestamp.now(tz="Europe/Rome").tz_localize(None)
    DF_ORARIO_FUTURO = DF_ORARIO[DF_ORARIO["DATA_ORA"] >= ORA_ATTUALE.floor('H')]
    DF_15MIN_FUTURO = DF_15MIN[DF_15MIN["DATA_ORA"] >= ORA_ATTUALE.floor('15T')].head(12)
    
    if not DF_ORARIO_FUTURO.empty:
        RIGA_LIVE = DF_ORARIO_FUTURO.iloc[0]
        ULTIMO_SYNC = datetime.now().strftime("%H:%M:%S")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"🟢 **CANTIERE ATTIVO**")
        st.sidebar.info(f"Ultimo Sync: {ULTIMO_SYNC}")
        
        # METRICHE LIVE
        C1, C2, C3 = st.columns(3)
        C1.metric("TEMPERATURA", f"{RIGA_LIVE['TEMP_CEMENTO']:.1f} °C", "STABILE E INVIOLABILE")
        C2.metric("PIOGGIA ATTUALE", f"{RIGA_LIVE['RAIN_CEMENTO']:.2f} mm", "CERTEZZA 10000%")
        C3.metric("VENTO", f"{RIGA_LIVE['WIND_CEMENTO']:.1f} km/h", "POLMONI D'ACCIAIO")
        
        st.markdown("---")
        
        # TABS: I TRE SCUDI TEMPORALI E LA MAPPA
        T1, T2, T3, T4 = st.tabs(["🚀 NOWCASTING", "🛡️ PROSSIME 24 ORE", "🔭 ORIZZONTE 72 ORE", "🗺️ RADAR"])
        
        with T1:
            st.markdown("### 🔴 RADAR PIOGGIA (OGNI 15 MIN)")
            CHART_15 = alt.Chart(DF_15MIN_FUTURO).mark_bar(color='#10b981', cornerRadius=4).encode(
                x=alt.X('hoursminutes(DATA_ORA):O', title='Ora'),
                y=alt.Y('RAIN_CEMENTO:Q', title='Pioggia (mm)'),
                tooltip=['DATA_ORA', 'RAIN_CEMENTO']
            ).properties(height=350)
            st.altair_chart(CHART_15, use_container_width=True)

        with T2:
            C_T, C_R = st.columns(2)
            with C_T:
                st.markdown("### 🌡️ TRACCIATO TERMICO")
                CHART_T = alt.Chart(DF_ORARIO_FUTURO.head(24)).mark_line(color='#f59e0b', size=4).encode(
                    x=alt.X('hours(DATA_ORA):O', title='Ora'),
                    y=alt.Y('TEMP_CEMENTO:Q', title='Gradi °C', scale=alt.Scale(zero=False))
                ).properties(height=300)
                st.altair_chart(CHART_T, use_container_width=True)
            with C_R:
                st.markdown("### 🌧️ PRECIPITAZIONI")
                CHART_R = alt.Chart(DF_ORARIO_FUTURO.head(24)).mark_bar(color='#3b82f6').encode(
                    x=alt.X('hours(DATA_ORA):O', title='Ora'),
                    y=alt.Y('RAIN_CEMENTO:Q', title='Pioggia (mm)')
                ).properties(height=300)
                st.altair_chart(CHART_R, use_container_width=True)

        with T3:
            st.markdown("### 🔭 TENDENZA A 3 GIORNI (PIAZZATO BLINDATO)")
            DF_72 = DF_ORARIO_FUTURO.head(72).copy()
            DF_72['Giorno'] = DF_72['DATA_ORA'].dt.strftime('%d %b - %H:%M')
            CHART_72 = alt.Chart(DF_72).mark_area(opacity=0.3, color='#3b82f6').encode(
                x=alt.X('DATA_ORA:T', title='Timeline'),
                y=alt.Y('RAIN_CEMENTO:Q', title='Pioggia (mm)')
            ).properties(height=350)
            st.altair_chart(CHART_72, use_container_width=True)
            st.dataframe(DF_72[['Giorno', 'TEMP_CEMENTO', 'RAIN_CEMENTO', 'WIND_CEMENTO']], use_container_width=True)

        with T4:
            st.markdown("### 🗺️ RADAR DI DENSITÀ TECNICA")
            MAP = folium.Map(location=[st.session_state.LATITUDE, st.session_state.LONGITUDE], zoom_start=13, tiles="cartodbpositron")
            folium.Marker([st.session_state.LATITUDE, st.session_state.LONGITUDE], popup=st.session_state.NOME_CITTA, icon=folium.Icon(color="green", icon="info-sign")).add_to(MAP)
            st_folium(MAP, width=1200, height=450)

    # REFRESH AUTOMATICO INVIOLABILE OGNI 60 SECONDI
    time.sleep(60)
    st.rerun()
else:
    st.error("⚠️ SORGENTE INSTABILE. RIPRISTINO IN CORSO...")
    time.sleep(10)
    st.rerun()
