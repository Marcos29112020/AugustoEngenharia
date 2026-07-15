import streamlit as st
import pandas as pd
from datetime import datetime
import re

# ===================== CONFIGURAÇÃO =====================
st.set_page_config(page_title="Augusto Construções | BI", page_icon="🏗️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #F1F5F9; }
    h1 { color: #1E3A8A; font-weight: 900; }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
col_logo, col_titulo = st.columns([1.3, 4.5])
with col_logo:
    st.image("https://i.ibb.co/tPFBw1h5/logo.jpg", width=185)
with col_titulo:
    st.markdown("<h1>AUGUSTO ENGENHARIA</h1>", unsafe_allow_html=True)
st.markdown("**Painel de Desempenho Operacional • Vibra Campo Limpo**")
st.markdown("---")

# ===================== CARREGAMENTO =====================
URL_GOOGLE_DRIVE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR3iZWG8EA_Q6_cxiWyr_opAjXEZ6Vulx829avjgamQQwjicTC9cuOqVtlXQz3eYe7pUH3MAMtG9ZkR/pub?gid=1542027995&single=true&output=csv"

@st.cache_data(ttl=0)
def load_data(url):
    df = pd.read_csv(url)
    df.columns = [str(col).strip().upper() for col in df.columns]
    if 'DATA' in df.columns:
        df['DATETIME'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y', errors='coerce')
        df['DATA'] = df['DATETIME'].dt.date
        df = df.dropna(subset=['DATA'])
    return df

df_raw = load_data(URL_GOOGLE_DRIVE)

df_raw['TAREFA / ATIVIDADE'] = df_raw['TAREFA / ATIVIDADE'].fillna("").astype(str).str.strip()
df_raw['OBSERVAÇÕES'] = df_raw.get('OBSERVAÇÕES', "").fillna("").astype(str).str.strip()

df_raw['STATUS_PRESENCA'] = df_raw['TAREFA / ATIVIDADE'].str.upper().apply(
    lambda x: "Falta" if "FALTOU" in x or "AUSENTE" in x or x == "" else "Presente"
)

# ===================== LÓGICA DE ATIVIDADE POR DATA =====================
def extrair_data_obs(obs):
    """Tenta extrair data de observações como 'transferido em 10/05/2025'"""
    patterns = [
        r'(\d{2}/\d{2}/\d{4})',
        r'(\d{2}/\d{2}/\d{2})',
        r'em (\d{2}/\d{2}/\d{4})'
    ]
    for pattern in patterns:
        match = re.search(pattern, obs, re.IGNORECASE)
        if match:
            try:
                return pd.to_datetime(match.group(1), dayfirst=True).date()
            except:
                pass
    return None

# Criar coluna de data de inatividade
df_raw['DATA_INATIVIDADE'] = df_raw['OBSERVAÇÕES'].apply(extrair_data_obs)

# ===================== FILTROS =====================
st.sidebar.header("Filtros")

equipes = ["Todos"] + sorted(df_raw['EQUIPE'].dropna().unique().tolist())
equipe_sel = st.sidebar.selectbox("Equipe", equipes)

data_min, data_max = df_raw['DATA'].min(), df_raw['DATA'].max()
datas_sel = st.sidebar.date_input("Período", [data_min, data_max], min_value=data_min, max_value=data_max)

# ===================== FILTRAR FUNCIONÁRIOS ATIVOS NO PERÍODO =====================
df_final = df_raw.copy()

if isinstance(datas_sel, (list, tuple)) and len(datas_sel) == 2:
    data_inicio, data_fim = datas_sel
    # Filtra registros dentro do período
    df_final = df_final[(df_final['DATA'] >= data_inicio) & (df_final['DATA'] <= data_fim)]
    
    # Filtra funcionários ativos no período (não inativados antes do fim do período)
    df_final = df_final[
        (df_final['DATA_INATIVIDADE'].isna()) | 
        (df_final['DATA_INATIVIDADE'] > data_fim)
    ]

# KPIs
total_reg = len(df_final)
total_faltas = len(df_final[df_final['STATUS_PRESENCA'] == "Falta"])
total_pres = total_reg - total_faltas
func_ativos = df_final['NOME'].nunique()

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total Lançamentos", total_reg)
with c2: st.metric("Funcionários Ativos", func_ativos)
with c3: st.metric("Presenças", total_pres)
with c4: st.metric("Faltas", total_faltas)

# Lista de Funcionários Ativos
st.subheader(f"👥 Funcionários Ativos no Período ({func_ativos})")
ativos = df_final[['NOME', 'EQUIPE']].drop_duplicates().sort_values('NOME')
st.dataframe(ativos, hide_index=True, use_container_width=True)

# Resto do dashboard (gráficos, fechamento mensal, etc.) pode ser adicionado aqui

st.info("Sistema de detecção de transferência/emprestimo por data nas observações ativado.")

# Visão Detalhada
st.subheader("Registros Detalhados")
df_exib = df_final.drop(columns=['STATUS_PRESENCA', 'MES_ANO', 'DATETIME', 'DATA_INATIVIDADE'], errors='ignore')
st.dataframe(df_exib, use_container_width=True, hide_index=True)
