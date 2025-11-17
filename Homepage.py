# ---------------- IMPORTS FIRST ----------------
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import json
import pandas as pd
import re
import numpy as np
from streamlit_dynamic_filters import DynamicFilters
from barcode import EAN13
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import time
import io
import streamlit.components.v1 as components
import base64

# -------------- PAGE CONFIG ---------------------
st.set_page_config(
  page_title="506RealState",
  page_icon="🏠",
  layout="wide",
)

# -------------- DATA LOADING --------------------

CSV_URL = "https://raw.githubusercontent.com/jchavesmartinez/real_state_tool/refs/heads/main/merged_contacts_listings_flat.csv"

@st.cache_data(show_spinner=True)
def load_listings_data() -> pd.DataFrame:
    try:
        df = pd.read_csv(CSV_URL)
        return df
    except Exception as e:
        st.error(f"❌ Error cargando CSV desde GitHub: {e}")
        return pd.DataFrame()

df_listings = load_listings_data()

if "df_listings" not in st.session_state:
    st.session_state["df_listings"] = df_listings

# -------------- UI --------------------

st.title("🏠 506RealState - Explorador de propiedades")

if df_listings.empty:
    st.warning("No se pudieron cargar los datos de propiedades.")
else:
    st.subheader("Tabla de propiedades (merged_contacts_listings_flat.csv)")
    st.write(f"Filas: {len(df_listings)} | Columnas: {len(df_listings.columns)}")
    st.dataframe(df_listings, use_container_width=True)
