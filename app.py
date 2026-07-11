import streamlit as st
import pandas as pd
from PIL import Image  # ← Adicionado

# 1. Configuração da página
st.set_page_config(
    page_title="Augusto Construções | BI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== LOGO + TÍTULO =====================
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    try:
        logo = Image.open("logo.png")  # Nome do arquivo da logo
        st.image(logo, width=180)
    except FileNotFoundError:
        st.warning("Logo não encontrada. Coloque o arquivo 'logo.png' na pasta do app.")

with col_titulo:
    st.markdown("<h1 style='margin-top: 25px; color: #1E3A8A; font-weight: 900; font-size: 2.8rem; letter-spacing: -0.04em;'>AUGUSTO ENGENHARIA</h1>", unsafe_allow_html=True)

# Subtítulo
st.markdown("<p class='subtitulo-painel'>Painel de Desempenho Operacional</p>", unsafe_allow_html=True)
st.markdown("<p class='legenda-contrato'>Contrato Ativo: Vibra Campo Limpo | Sincronização em Nuvem (Google Drive)</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; border-color: #CBD5E1;'>", unsafe_allow_html=True)
