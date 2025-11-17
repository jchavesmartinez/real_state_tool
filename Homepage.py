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

        # Copia limpia para filtros
        df_for_filters = df_listings.copy()

        # Normalizar columnas tipo object para que DynamicFilters no se rompa
        for col in df_for_filters.columns:
            if df_for_filters[col].dtype == "object":
                df_for_filters[col] = (
                    df_for_filters[col]
                    .astype(str)
                    .replace("nan", "")
                    .replace("None", "")
                )

        filters = DynamicFilters(
            df_for_filters,
            filters=filter_cols
        )

        filters.display_filters()

        # DataFrame filtrado por DynamicFilters
        df_filtered = filters.filter_df()
    else:
        df_filtered = df_listings.copy()

    # --------- Filtros por columnas 0/1 (amenities, etc.) con radios ---------
    # Detectar columnas binarias (solo 0 y 1, ignorando NaN)
    binary_cols = []
    for col in df_filtered.columns:
        vals = set(df_filtered[col].dropna().unique())
        if vals.issubset({0, 1}) and len(vals) > 0:
            binary_cols.append(col)

    # Opcional: ordenar alfabéticamente o escoger sólo algunas
    binary_cols = sorted(binary_cols)

    st.markdown("### 🎛 Filtros por amenities (0/1)")

    binary_cols = []
    for col in df_filtered.columns:
        vals = set(df_filtered[col].dropna().unique())
        if vals.issubset({0, 1}) and len(vals) > 0:
            binary_cols.append(col)

    # Ordenar alfabéticamente
    binary_cols = sorted(binary_cols)

    st.markdown("### 🎛 Filtros por amenities (0/1)")

    amenity_choices = {}

    if binary_cols:
        with st.expander("Mostrar filtros de amenities (0/1)", expanded=False):
            n_cols = 3  # número de columnas que quieres en la cuadrícula

            # Recorremos las columnas binarias en bloques de n_cols
            for start in range(0, len(binary_cols), n_cols):
                cols = st.columns(n_cols)
                slice_cols = binary_cols[start:start + n_cols]

                for idx, col_name in enumerate(slice_cols):
                    with cols[idx]:
                        choice = st.radio(
                            label=col_name,
                            options=["Indiferente", "Sí", "No"],
                            horizontal=True,
                            key=f"amen_{col_name}"
                        )
                        amenity_choices[col_name] = choice
    else:
        st.info("No se encontraron columnas binarias (0/1) para filtrar.")

    # Aplicar filtros de radios SOBRE el resultado de DynamicFilters
    df_final = df_filtered.copy()

    for col, choice in amenity_choices.items():
        if choice == "Sí":
            df_final = df_final[df_final[col] == 1]
        elif choice == "No":
            df_final = df_final[df_final[col] == 0]
        # "Indiferente" → no se filtra por esa columna

    st.write(f"Filas después de filtrar: {len(df_final)}")
    st.dataframe(df_final, use_container_width=True)