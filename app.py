import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Augusto Engenharia BI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Melhorado
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .main .block-container { padding-top: 1.8rem; padding-bottom: 2rem; }
    h1 { color: #1E3A8A; font-weight: 900; letter-spacing: -0.04em; }
    .metric-container { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ===================== CABEÇALHO =====================
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://i.ibb.co/tPFBw1h5/logo.jpg", width=160)

with col2:
    st.markdown("<h1>AUGUSTO ENGENHARIA</h1>", unsafe_allow_html=True)
    st.markdown("**Painel de Desempenho Operacional** — Vibra Campo Limpo")

st.markdown("---")

# ===================== DADOS =====================
URL_GOOGLE_DRIVE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR3iZWG8EA_Q6_cxiWyr_opAjXEZ6Vulx829avjgamQQwjicTC9cuOqVtlXQz3eYe7pUH3MAMtG9ZkR/pub?gid=1542027995&single=true&output=csv"

@st.cache_data(ttl=300)
def load_data(url):
    df = pd.read_csv(url)
    df.columns = [str(col).strip().upper() for col in df.columns]
    if 'DATA' in df.columns:
        df['DATETIME'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y', errors='coerce')
        df['DATA'] = df['DATETIME'].dt.date
        df = df.dropna(subset=['DATA'])
    return df

df_raw = load_data(URL_GOOGLE_DRIVE)

# Tratamento básico
df_raw['TAREFA / ATIVIDADE'] = df_raw['TAREFA / ATIVIDADE'].fillna("").astype(str).str.strip()
df_raw['OBSERVAÇÕES'] = df_raw.get('OBSERVAÇÕES', "").fillna("").astype(str).str.strip()
df_raw['STATUS_PRESENCA'] = df_raw['TAREFA / ATIVIDADE'].str.upper().apply(
    lambda x: "Falta" if "FALTOU" in x or "AUSENTE" in x or x == "" else "Presente"
)

# ===================== FILTROS (Sidebar) =====================
st.sidebar.header("Filtros")

equipes = ["Todos"] + sorted(df_raw['EQUIPE'].dropna().unique().tolist())
equipe_sel = st.sidebar.selectbox("Equipe", equipes)

# ... (resto dos filtros mantidos, mas simplificados)

# ===================== KPIs (Destaque) =====================
st.subheader("Resumo Geral")
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total Lançamentos", len(df_final))
with c2: st.metric("Funcionários Ativos", df_final['NOME'].nunique())
with c3: st.metric("Presenças", total_pres)
with c4: st.metric("Faltas", total_faltas, delta=None)

st.markdown("---")

# ===================== GRÁFICOS PRINCIPAIS =====================
st.subheader("Desempenho da Equipe")

g1, g2 = st.columns(2)

with g1:
    st.markdown("**Top 5 com Mais Presenças**")
    presencas = (df_final[df_final['STATUS_PRESENCA'] == 'Presente']
                .groupby('NOME')['DATA'].count()
                .sort_values(ascending=False).head(5))
    st.bar_chart(presencas, color="#1E3A8A", use_container_width=True)

with g2:
    st.markdown("**Top 3 com Menos Faltas**")
    todas = df_final[['NOME','EQUIPE']].drop_duplicates()
    faltas = (df_final[df_final['STATUS_PRESENCA']=='Falta']
             .groupby('NOME')['DATA'].count().reset_index(name='FALTAS'))
    ranking = pd.merge(todas, faltas, on='NOME', how='left').fillna(0)
    top3 = ranking.sort_values('FALTAS').head(3)
    st.bar_chart(top3.set_index('NOME')['FALTAS'], color="#22C55E", use_container_width=True)

# Gráfico de Equipes
st.markdown("**Presenças × Faltas por Equipe**")
por_equipe = df_final.groupby('EQUIPE')['STATUS_PRESENCA'].value_counts().unstack(fill_value=0)
st.bar_chart(por_equipe, color=["#1E3A8A", "#EF4444"], use_container_width=True)

# ===================== TABELAS IMPORTANTES (abaixo) =====================
st.markdown("### Fechamento Mensal")
# (manter o fechamento mensal)

st.markdown("### Registros Detalhados")
# Mostrar dataframe com scroll, mas simplificado
