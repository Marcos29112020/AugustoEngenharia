import streamlit as st
import pandas as pd

# ===================== CONFIGURAÇÃO =====================
st.set_page_config(
    page_title="Augusto Construções | BI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Premium
st.markdown("""
    <style>
    .stApp { background-color: #F1F5F9; }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; max-width: 95%; }
    
    [data-testid="stMetricContainer"] {
        background-color: #FFFFFF; padding: 22px 25px; border-radius: 12px; border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    </style>
    """, unsafe_allow_html=True)

# ===================== LOGO + TÍTULO =====================
col_logo, col_titulo = st.columns([1.1, 5])

with col_logo:
    st.image(
        "https://drive.google.com/uc?id=1YrL-wex96OXddunUAfQ9FoV_EjaPF-_X", 
        width=185
    )

with col_titulo:
    st.markdown("""
        <h1 style='margin-top: 32px; color: #1E3A8A; font-weight: 900; 
        font-size: 2.85rem; letter-spacing: -0.04em; line-height: 1.1;'>
        AUGUSTO ENGENHARIA
        </h1>
    """, unsafe_allow_html=True)

# ===================== DADOS =====================
URL_GOOGLE_DRIVE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR3iZWG8EA_Q6_cxiWyr_opAjXEZ6Vulx829avjgamQQwjicTC9cuOqVtlXQz3eYe7pUH3MAMtG9ZkR/pub?gid=1542027995&single=true&output=csv"

@st.cache_data(ttl=0)
def load_data_cloud(url):
    df = pd.read_csv(url)
    df.columns = [str(col).strip().upper() for col in df.columns]
    
    if 'DATA' in df.columns:
        df['DATETIME'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y', errors='coerce')
        df['DATA'] = df['DATETIME'].dt.date
        df = df.dropna(subset=['DATA'])
    return df

try:
    df_raw = load_data_cloud(URL_GOOGLE_DRIVE)
except Exception as e:
    st.error(f"Erro ao conectar com o Google Drive: {e}")
    st.stop()

if df_raw is None or df_raw.empty:
    st.error("Nenhum dado encontrado ou link inválido.")
    st.stop()

# Tratamento de colunas
df_raw['TAREFA / ATIVIDADE'] = df_raw['TAREFA / ATIVIDADE'].fillna("").astype(str).str.strip()
df_raw['OBSERVAÇÕES'] = df_raw.get('OBSERVAÇÕES', "").fillna("").astype(str).str.strip()

# Presença
df_raw['STATUS_PRESENCA'] = df_raw['TAREFA / ATIVIDADE'].str.upper().apply(
    lambda x: "Falta" if "FALTOU" in x or "AUSENTE" in x or x == "" else "Presente"
)

# Mês/Ano
df_raw['MES_ANO'] = df_raw['DATETIME'].dt.strftime('%m/%Y - %B')
meses_pt = {
    'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril',
    'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto',
    'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
}
for en, pt in meses_pt.items():
    df_raw['MES_ANO'] = df_raw['MES_ANO'].str.replace(en, pt, case=False)

# ===================== FILTROS =====================
st.sidebar.markdown("<h2 style='font-size:1.2rem; color:#0F172A; font-weight:700; margin-bottom:15px;'>🎯 Painel de Filtros</h2>", unsafe_allow_html=True)

equipes = ["Todos"] + sorted(list(df_raw['EQUIPE'].dropna().unique()))
equipe_sel = st.sidebar.selectbox("Filtro por Equipe", equipes)

df_filt_nome = df_raw[df_raw['EQUIPE'] == equipe_sel] if equipe_sel != "Todos" else df_raw
nomes = ["Todos"] + sorted(list(df_filt_nome['NOME'].dropna().unique()))
nome_sel = st.sidebar.selectbox("Filtro por Funcionário", nomes)

filtro_presenca = st.sidebar.radio("Filtro de Frequência", ["Todos", "Apenas Presentes", "Apenas Faltas"])

df_filt_tar = df_raw[df_raw['STATUS_PRESENCA'] == "Presente"]
tarefas = ["Todos"] + sorted(list(df_filt_tar['TAREFA / ATIVIDADE'].dropna().unique()))
tarefa_sel = st.sidebar.selectbox("Filtro por Tarefa / Atividade", tarefas)

data_min, data_max = df_raw['DATA'].min(), df_raw['DATA'].max()
datas_sel = st.sidebar.date_input("Intervalo de Tempo", [data_min, data_max], min_value=data_min, max_value=data_max)

# Processamento dos Filtros
df_final = df_raw.copy()
if equipe_sel != "Todos": df_final = df_final[df_final['EQUIPE'] == equipe_sel]
if nome_sel != "Todos": df_final = df_final[df_final['NOME'] == nome_sel]
if tarefa_sel != "Todos": df_final = df_final[df_final['TAREFA / ATIVIDADE'] == tarefa_sel]
if filtro_presenca == "Apenas Presentes": df_final = df_final[df_final['STATUS_PRESENCA'] == "Presente"]
elif filtro_presenca == "Apenas Faltas": df_final = df_final[df_final['STATUS_PRESENCA'] == "Falta"]

if isinstance(datas_sel, (list, tuple)) and len(datas_sel) == 2:
    data_inicio, data_fim = datas_sel
    df_final = df_final[(df_final['DATA'] >= data_inicio) & (df_final['DATA'] <= data_fim)]

# ===================== KPIs =====================
total_reg = len(df_final)
total_faltas = len(df_final[df_final['STATUS_PRESENCA'] == "Falta"])
total_pres = total_reg - total_faltas

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total de Lançamentos", f"{total_reg}")
with c2: st.metric("Funcionários Ativos", f"{df_final['NOME'].nunique()}")
with c3: st.metric("Presenças Confirmadas", f"{total_pres}")
with c4: st.metric("Faltas Registradas 🚨", f"{total_faltas}")

st.markdown("<br>", unsafe_allow_html=True)

# ===================== GRÁFICOS =====================
st.markdown("### 📊 Indicadores e Gráficos Gerenciais")
g1, g2 = st.columns(2)

with g1:
    st.markdown("**Volume Diário de Trabalho (Linha do Tempo)**")
    if not df_final.empty:
        df_timeline = df_final[df_final['STATUS_PRESENCA'] == 'Presente'].groupby('DATA').size().reset_index(name='Registros')
        df_timeline = df_timeline.set_index('DATA')
        st.line_chart(df_timeline, color="#1E3A8A", use_container_width=True)
    else:
        st.info("Sem dados para o período.")

with g2:
    st.markdown("**Top 5 Atividades Mais Executadas**")
    if not df_final.empty:
        df_ranking_data = df_final[(df_final['STATUS_PRESENCA'] == 'Presente') & (df_final['TAREFA / ATIVIDADE'] != "")]
        df_ranking = df_ranking_data['TAREFA / ATIVIDADE'].value_counts().head(5)
        st.bar_chart(df_ranking, color="#475569", use_container_width=True)
    else:
        st.info("Sem atividades mapeadas.")

# ===================== FECHAMENTO MENSAL =====================
st.markdown("### 🗓️ Resumo de Frequência Mensal (Fechamento de Cartão)")
lista_meses = sorted(list(df_raw['MES_ANO'].unique()))
mes_selecionado = st.selectbox("Selecione o Mês para Fechamento de Frequência", lista_meses)
df_mes = df_raw[df_raw['MES_ANO'] == mes_selecionado]

if not df_mes.empty:
    df_presencas_calc = df_mes[df_mes['STATUS_PRESENCA'] == 'Presente'].groupby(['EQUIPE', 'NOME'])['DATA'].nunique().reset_index(name='DIAS NA OBRA')
    df_faltas_calc = df_mes[df_mes['STATUS_PRESENCA'] == 'Falta'].groupby(['EQUIPE', 'NOME'])['DATA'].nunique().reset_index(name='DIAS DE FALTA')
    todas_equipes_nomes = df_mes[['EQUIPE', 'NOME']].drop_duplicates()
    df_fechamento = pd.merge(todas_equipes_nomes, df_presencas_calc, on=['EQUIPE', 'NOME'], how='left').fillna(0)
    df_fechamento = pd.merge(df_fechamento, df_faltas_calc, on=['EQUIPE', 'NOME'], how='left').fillna(0)
    df_fechamento['DIAS NA OBRA'] = df_fechamento['DIAS NA OBRA'].astype(int)
    df_fechamento['DIAS DE FALTA'] = df_fechamento['DIAS DE FALTA'].astype(int)
    df_fechamento = df_fechamento.sort_values(by=['EQUIPE', 'NOME'])
    st.dataframe(df_fechamento, use_container_width=True, hide_index=True)

# ===================== VISÃO DETALHADA =====================
st.markdown("### 📋 Visão Detalhada dos Registros (Linha por Linha)")
df_exibicao = df_final.drop(columns=['STATUS_PRESENCA', 'MES_ANO', 'DATETIME'], errors='ignore')

if 'OBSERVAÇÕES' in df_exibicao.columns:
    cols = [col for col in df_exibicao.columns if col != 'OBSERVAÇÕES'] + ['OBSERVAÇÕES']
    df_exibicao = df_exibicao[cols]

st.dataframe(
    df_exibicao, 
    use_container_width=True, 
    hide_index=True,
    column_config={
        "OBSERVAÇÕES": st.column_config.TextColumn("Observações", width="large")
    }
)
