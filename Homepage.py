import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# -------------------------
# Cargar archivo YAML
# -------------------------
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

    st.title("🏠 Homepage")
    st.write("Contenido privado de la app…")

elif auth_status is False:
    st.error("❌ Usuario o contraseña incorrectos")

else:
    st.warning("Ingrese sus credenciales para continuar")
