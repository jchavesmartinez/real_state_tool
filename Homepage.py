# ---------------- IMPORTS PRIMERO ----------------
import streamlit as st
import pandas as pd
import numpy as np
import json
import re
import time
import io
import base64

from streamlit_dynamic_filters import DynamicFilters
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from barcode import EAN13
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import streamlit.components.v1 as components

# ---------------- CONFIG PÁGINA ----------------
st.set_page_config(
    page_title="506RealState",
    page_icon="🏠",
    layout="wide",
)

# ---------------- CARGA DE DATOS (CON CACHE) ----------------

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
st.session_state["df_listings"] = df_listings

# ---------------- UI PRINCIPAL ----------------

st.title("🏠 506RealState - Explorador de propiedades")

if df_listings.empty:
    st.warning("No se pudieron cargar los datos de propiedades.")
else:
    st.subheader("Tabla de propiedades (merged_contacts_listings_flat.csv)")
    st.write(f"Filas totales (sin filtrar): {len(df_listings)} | Columnas: {len(df_listings.columns)}")

    # --------- Filtros dinámicos con DynamicFilters ---------
    # Seleccionamos solo columnas que EXISTEN en el CSV
    candidate_filters = [
        "Categoria",
        "Localización",
        "Precio",
        "Recámaras",
        "Baños",
        "Parking",
        "Año de construcción",
        "contact_name"
    ]
    filter_cols = [c for c in candidate_filters if c in df_listings.columns]

    if filter_cols:
        st.markdown("### 🔎 Filtros dinámicos")

        # Creamos una copia para los filtros (opcional, por seguridad)
        df_for_filters = df_listings.copy()

        filters = DynamicFilters(
            df_for_filters,
            filters=filter_cols
        )

        # Muestra los filtros en la UI
        filters.display_filters()

        # DataFrame filtrado
        df_filtered = filters.filter_df()

        st.write(f"Filas después de filtrar: {len(df_filtered)}")
        st.dataframe(df_filtered, use_container_width=True)
    else:
        st.info("No se encontraron columnas adecuadas para filtros dinámicos, mostrando tabla completa.")
        st.dataframe(df_listings, use_container_width=True)
