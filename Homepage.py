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
import json as json_lib  # para evitar conflicto de nombre si quieres

# ------------------------------------------------------------------------------
# Configuración general de la página
# ------------------------------------------------------------------------------

# st.cache_data.clear()
st.set_page_config(
    page_title="506RealState",
    page_icon="🏠",
    layout="wide",
)

# ---------------------------- Variables generales --------------------------------
# (aquí puedes ir poniendo tus variables globales si ya las tenías)

# ------------------------------------------------------------------------------
# Cargar CSV desde GitHub con cache
# ------------------------------------------------------------------------------

CSV_URL = "https://raw.githubusercontent.com/jchavesmartinez/real_state_tool/refs/heads/main/merged_contacts_listings_flat.csv"

@st.cache_data(show_spinner=True)
def load_listings_data() -> pd.DataFrame:
    try:
        df = pd.read_csv(CSV_URL)
        return df
    except Exception as e:
        st.error(f"❌ Error cargando el CSV desde GitHub: {e}")
        return pd.DataFrame()  # evita que falle toda la app

df_listings = load_listings_data()

# Guardar en session_state por si lo usas en otras secciones/páginas
if "df_listings" not in st.session_state:
    st.session_state["df_listings"] = df_listings

# ------------------------------------------------------------------------------
# UI principal
# ------------------------------------------------------------------------------

st.title("🏠 506RealState - Explorador de propiedades")

if df_listings.empty:
    st.warning("No se pudieron cargar los datos de propiedades.")
else:
    st.subheader("Tabla de propiedades (merged_contacts_listings_flat.csv)")
    st.write(f"Filas: {len(df_listings)} | Columnas: {len(df_listings.columns)}")

    st.dataframe(df_listings, use_container_width=True)

    # Ejemplo: podrías empezar a jugar con filtros dinámicos después
    # filters = DynamicFilters(df_listings, filters=['Categoria', 'Localización'])
    # filters.display_filters()
    # filtered_df = filters.filter_df()
    # st.dataframe(filtered_df, use_container_width=True)

# ------------------------------------------------------------------------------
# A partir de aquí puedes seguir con el resto de tu lógica (códigos previos)
# por ejemplo: generación de PDFs, códigos de barras, integración con Google Drive, etc.
# ------------------------------------------------------------------------------
