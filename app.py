import streamlit as st
import pandas as pd

# ===================== CONFIGURAÇÃO =====================
st.set_page_config(
    page_title="Augusto Engenharia BI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Limpo
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .main .block-container { padding-top: 1.8rem; padding-bottom: 2rem; max-width: 98%; }
    h1 { color: #1E3A8A; font-weight: 900; letter-spacing: -0.04em; margin-bottom: 0.3rem; }
    h3 { color: #334155; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ===================== CABEÇALHO =====================
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.image("https://i.ibb.co/tPFBw1h5/logo.jpg", width=165)

with col_titulo:
    st.markdown("<h1>AUGUSTO ENGENHARIA</h1>", unsafe_allow_html=True)
    st.caption("Painel de Desempenho Operacional • Vibra Campo Limpo")

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

df_raw['TAREFA / ATIVIDADE'] = df_raw['TAREFA / ATIVIDADE'].fillna("").astype(str).str.strip()
df_raw['OBSERVAÇÕES'] = df_raw.get('OBSERVAÇÕES', "").fillna("").astype(str).str.strip()

df_raw['STATUS_PRESENCA'] = df_raw['TAREFA / ATIVIDADE'].str.upper().apply(
    lambda x: "Falta" if "FALTOU" in x or "AUSENTE" in x or x == "" else "Presente"
)

# ===================== FILTROS =====================
st.sidebar.header("🎯 Filtros")

equipes = ["Todos"] + sorted(df_raw['EQUIPE'].dropna().unique().tolist())
equipe_sel = st.sidebar.selectbox("Equipe", equipes)

df_filt = df_raw[df_raw['EQUIPE'] == equipe_sel] if equipe_sel != "Todos" else df_raw
nomes = ["Todos"] + sorted(df_filt['NOME'].dropna().unique().tolist())
nome_sel = st.sidebar.selectbox("Funcionário", nomes)

filtro_presenca = st.sidebar.radio("Frequência", ["Todos", "Apenas Presentes", "Apenas Faltas"])

data_min, data_max = df_raw['DATA'].min(), df_raw['DATA'].max()
datas_sel = st.sidebar.date_input("Período", [data_min, data_max], min_value=data_min, max_value=data_max)

# Aplicar Filtros
df_final = df_raw.copy()
if equipe_sel != "Todos": df_final = df_final[df_final['EQUIPE'] == equipe_sel]
if nome_sel != "Todos": df_final = df_final[df_final['NOME'] == nome_sel]
if filtro_presenca == "Apenas Presentes": df_final = df_final[df_final['STATUS_PRESENCA'] == "Presente"]
elif filtro_presenca == "Apenas Faltas": df_final = df_final[df_final['STATUS_PRESENCA'] == "Falta"]

if len(datas_sel) == 2:
    df_final = df_final[(df_final['DATA'] >= datas_sel[0]) & (df_final['DATA'] <= datas_sel[1])]

# ===================== KPIs =====================
st.subheader("Resumo Geral")
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total Lançamentos", len(df_final))
with c2: st.metric("Funcionários Ativos", df_final['NOME'].nunique())
with c3: st.metric("Presenças", len(df_final[df_final['STATUS_PRESENCA'] == "Presente"]))
with c4: st.metric("Faltas", len(df_final[df_final['STATUS_PRESENCA'] == "Falta"]))

st.markdown("---")

# ===================== GRÁFICOS =====================
st.subheader("Desempenho da Equipe")

g1, g2 = st.columns(2)

with g1:
    st.markdown("**Top 5 Funcionários com Mais Presenças**")
    if not df_final.empty:
        top_pres = (df_final[df_final['STATUS_PRESENCA'] == 'Presente']
                   .groupby('NOME')['DATA'].count()
                   .sort_values(ascending=False).head(5))
        st.bar_chart(top_pres, color="#1E3A8A", use_container_width=True)

with g2:
    st.markdown("**Top 3 Funcionários com Menos Faltas**")
    if not df_final.empty:
        todas = df_final[['NOME','EQUIPE']].drop_duplicates()
        faltas = (df_final[df_final['STATUS_PRESENCA']=='Falta']
                 .groupby('NOME')['DATA'].count().reset_index(name='FALTAS'))
        ranking = pd.merge(todas, faltas, on='NOME', how='left').fillna(0)
        top3 = ranking.sort_values('FALTAS').head(3)
        st.bar_chart(top3.set_index('NOME')['FALTAS'], color="#22C55E", use_container_width=True)

st.markdown("---")

# ===================== FECHAMENTO MENSAL =====================
st.subheader("Fechamento Mensal")
lista_meses = sorted(df_raw['MES_ANO'].unique())
mes_sel = st.selectbox("Selecione o Mês", lista_meses)

df_mes = df_raw[df_raw['MES_ANO'] == mes_sel]
if not df_mes.empty:
    pres = df_mes[df_mes['STATUS_PRESENCA']=='Presente'].groupby(['EQUIPE','NOME'])['DATA'].nunique().reset_index(name='DIAS NA OBRA')
    falt = df_mes[df_mes['STATUS_PRESENCA']=='Falta'].groupby(['EQUIPE','NOME'])['DATA'].nunique().reset_index(name='DIAS DE FALTA')
    base = df_mes[['EQUIPE','NOME']].drop_duplicates()
    df_fech = base.merge(pres, how='left').merge(falt, how='left').fillna(0)
    df_fech = df_fech.astype({'DIAS NA OBRA': int, 'DIAS DE FALTA': int})
    st.dataframe(df_fech.sort_values(by=['EQUIPE','NOME']), use_container_width=True, hide_index=True)

# ===================== VISÃO DETALHADA =====================
st.subheader("Registros Detalhados")
df_exib = df_final.drop(columns=['STATUS_PRESENCA', 'MES_ANO', 'DATETIME'], errors='ignore')

if 'OBSERVAÇÕES' in df_exib.columns:
    cols = [c for c in df_exib.columns if c != 'OBSERVAÇÕES'] + ['OBSERVAÇÕES']
    df_exib = df_exib[cols]

st.dataframe(df_exib, use_container_width=True, hide_index=True,
             column_config={"OBSERVAÇÕES": st.column_config.TextColumn("Observações", width="large")})
