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
        c4, c5, c6 = st.columns(3)

        total_listings = len(df_final)

        # --- Limpieza de columnas numéricas ---
        def to_num(series):
            return pd.to_numeric(series, errors="coerce")

        m2_tot = to_num(df_final.get("M² totales"))
        m2_cons = to_num(df_final.get("m²"))
        alquiler_usd = to_num(df_final.get("Alquiler_USD"))
        precio_m2_cons = to_num(df_final.get("Precio/M² de construcción_USD"))
        precio_m2_terreno = to_num(df_final.get("Precio/M² de terreno_USD"))
        dias_publicado = to_num(df_final.get("Dias Publicado"))
        precio_total = to_num(df_final.get("Precio")) if "Precio" in df_final else None

        # --- Métricas ---
        # Precio por m² construcción
        prom_precio_m2_cons = precio_m2_cons.mean()

        # Precio por m² terreno
        prom_precio_m2_terreno = precio_m2_terreno.mean()

        # Alquiler promedio
        prom_alquiler_usd = alquiler_usd.mean()

        # Tiempo promedio publicado
        prom_dias_publicado = dias_publicado.mean()

        # Relación m² construcción vs totales
        if m2_tot.notna().sum() > 0:
            ratio_m2 = (m2_cons / m2_tot).mean()
        else:
            ratio_m2 = 0


        # --- Mostrar métricas ---
        c1.metric("Cantidad de listings", total_listings)
        c2.metric("Precio prom. m² construcción", 
                f"${prom_precio_m2_cons:,.0f}" if not np.isnan(prom_precio_m2_cons) else "N/A")
        c3.metric("Precio prom. m² terreno", 
                f"${prom_precio_m2_terreno:,.0f}" if not np.isnan(prom_precio_m2_terreno) else "N/A")

        c4.metric("Alquiler mensual promedio", 
                f"${prom_alquiler_usd:,.0f}" if not np.isnan(prom_alquiler_usd) else "N/A")

        c5.metric("Días publicados (promedio)", 
                f"{prom_dias_publicado:,.0f}" if not np.isnan(prom_dias_publicado) else "N/A")

        c6.metric("Relación construcción / lote", 
                f"{ratio_m2:.2f}" if not np.isnan(ratio_m2) else "N/A")


        # --------- TABLA FINAL ---------
        st.write(f"Filas después de filtrar: {len(df_final)}")
        st.dataframe(df_final, use_container_width=True)






elif auth_status is False:
    st.error("❌ Usuario o contraseña incorrectos")

else:
    st.warning("Ingrese sus credenciales para continuar")
