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
# Login (VERSIÓN CORRECTA)
# -------------------------
name, auth_status, username = authenticator.login(
    "main",
    fields={
        "Form name": "Login",
        "Username": "Usuario",
        "Password": "Contraseña",
        "Login": "Ingresar",
    },
)

# -------------------------
# Resultado del login
# -------------------------
if auth_status:
    st.sidebar.success(f"Bienvenido {name}")
    authenticator.logout("Cerrar sesión", "sidebar")

    st.title("🏠 Homepage")
    st.write("Contenido privado de la app...")

elif auth_status is False:
    st.error("❌ Usuario o contraseña incorrectos")

elif auth_status is None:
    st.warning("Ingrese sus credenciales para continuar")
