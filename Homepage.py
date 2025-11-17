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

    st.write(f"Total filas (sin filtrar): {len(df_listings)} | Columnas: {len(df_listings.columns)}")

    # ----------------- Filtros dinámicos -----------------
    # Ajusta la lista de columnas según las que tenga tu CSV
    possible_filters = [
        col for col in [
            "Categoria",
            "Localización",
            "Precio",
            "Recámaras",
            "Baños",
            "Parking",
            "Año de construcción",
            "contact_name"
        ] 
        if col in df_listings.columns
    ]

    if possible_filters:
        st.markdown("### 🔎 Filtros dinámicos")
        df_for_filters = df_listings.copy()

        filters = DynamicFilters(
            df_for_filters,
            filters=possible_filters
        )

        filters.display_filters()

        df_filtered = filters.filter_df()

        st.write(f"Filas después de filtrar: {len(df_filtered)}")
        st.dataframe(df_filtered, use_container_width=True)
    else:
        st.info("No se encontraron columnas adecuadas para filtros dinámicos, mostrando tabla completa.")
        st.dataframe(df_listings, use_container_width=True)
