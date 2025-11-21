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
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import streamlit.components.v1 as components
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# -------------------------
# Cargar archivo YAML
# -------------------------

st.set_page_config(
  page_title="Lilliput Inventory Management",
  page_icon="🔬",
  layout="wide",
)


with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# -------------------------
# Crear autenticador
# -------------------------
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# -------------------------
# Renderizar login (NO se unpackea)
# -------------------------
try:
    authenticator.login(
        "main",
        fields={
            "Form name": "Login",
            "Username": "Usuario",
            "Password": "Contraseña",
            "Login": "Ingresar",
        },
    )
except Exception as e:
    st.error(e)

# -------------------------
# Leer estado de autenticación desde session_state
# -------------------------
auth_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")
username = st.session_state.get("username")

if auth_status:
    # Ya está logueado
    st.sidebar.success(f"Bienvenido {name}")
    authenticator.logout("Cerrar sesión", "sidebar")


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
        # 👉 CONTENEDOR PARA MÉTRICAS AL INICIO
        metrics_container = st.container()

        st.subheader("Tabla de propiedades")

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

            df_for_filters = df_listings.copy()

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

            filters.display_filters(
                location="columns",
                num_columns=2,
                gap="small"
            )

            df_filtered = filters.filter_df()
        else:
            df_filtered = df_listings.copy()

        # --------- Filtros por columnas 0/1 (amenities, etc.) con radios ---------
        st.markdown("### 🎛 Filtros por amenities (0/1)")

        binary_cols = []
        for col in df_filtered.columns:
            vals = set(df_filtered[col].dropna().unique())
            if vals.issubset({0, 1}) and len(vals) > 0:
                binary_cols.append(col)

        binary_cols = sorted(binary_cols)
        amenity_choices = {}

        if binary_cols:
            with st.expander("Mostrar filtros de amenities (0/1)", expanded=False):
                n_cols = 3
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

        # 👉 AQUÍ RELLENAS LAS MÉTRICAS DEL CONTENEDOR DE ARRIBA
        with metrics_container:
            st.markdown("## 📊 Resumen de resultados filtrados")
            c1, c2, c3 = st.columns(3)

            total_listings = len(df_final)

            # Por si la columna 'Precio' no es numérica, la limpiamos rápido
            if "Precio" in df_final.columns:
                precios = pd.to_numeric(df_final["Precio"], errors="coerce")
                precios = precios.dropna()
            else:
                precios = pd.Series(dtype=float)

            if not precios.empty:
                precio_prom = precios.mean()
                precio_min = precios.min()
                precio_max = precios.max()
            else:
                precio_prom = precio_min = precio_max = 0

            c1.metric("Cantidad de listings", total_listings)
            c2.metric("Precio promedio", f"${precio_prom:,.0f}")
            c3.metric("Rango de precios", f"${precio_min:,.0f} - ${precio_max:,.0f}")

        # --------- TABLA FINAL ---------
        st.write(f"Filas después de filtrar: {len(df_final)}")
        st.dataframe(df_final, use_container_width=True)






elif auth_status is False:
    st.error("❌ Usuario o contraseña incorrectos")

else:
    st.warning("Ingrese sus credenciales para continuar")
