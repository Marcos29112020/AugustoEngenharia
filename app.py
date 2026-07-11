import streamlit as st
import pandas as pd
from PIL import Image

# 1. Configuração da página do navegador (Visual Executivo)
st.set_page_config(
    page_title="Augusto Construções | BI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Premium - Identidade Visual Augusto Construções
st.markdown("""
    <style>
    .stApp { background-color: #F1F5F9; }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; max-width: 95%; }
    .marca-principal { color: #1E3A8A; font-weight: 900; font-size: 2.6rem; letter-spacing: -0.05em; margin-bottom: 0rem; line-height: 1.1; }
    .subtitulo-painel { color: #334155; font-weight: 700; font-size: 1.6rem; margin-top: 0.2rem; margin-bottom: 0.2rem; letter-spacing: -0.03em; }
    .legenda-contrato { color: #64748B; font-size: 0.95rem; margin-top: 0rem; margin-bottom: 0.5rem; }
    h3 { color: #1E293B; font-weight: 700; font-size: 1.4rem; margin-top: 1.5rem; margin-bottom: 1rem; }
    
    [data-testid="stMetricContainer"] {
        background-color: #FFFFFF; padding: 22px 25px; border-radius: 12px; border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    [data-testid="stMetricLabel"] { color: #475569 !important; font-weight: 600 !important; font-size: 0.95rem !important; }
    [data-testid="stMetricValue"] { color: #0F172A !important; font-weight: 700 !important; font-size: 2rem !important; }
    [data-testid="stSidebar"] { background-color: #F8FAFC; border-right: 1px solid #E2E8F0; }
    </style>
    """, unsafe_allow_html=True)

# ===================== LOGO + TÍTULO =====================
col_logo, col_titulo = st.columns([1.2, 5])

with col_logo:
    try:
        logo = Image.open("logo.png")           # Nome do arquivo deve ser "logo.png"
        st.image(logo, width=190)
    except FileNotFoundError:
        st.error("❌ Arquivo 'logo.png' não encontrado. Coloque-o na mesma pasta do app.")

with col_titulo:
    st.markdown("""
        <h1 style='margin-top: 35px; color: #1E3A8A; font-weight: 900; 
        font-size: 2.85rem; letter-spacing: -0.04em;'>
        AUGUSTO ENGENHARIA
        </h1>
    """, unsafe_allow_html=True)

# Subtítulos
st.markdown("<p class='subtitulo-painel'>Painel de Desempenho Operacional</p>", unsafe_allow_html=True)
st.markdown("<p class='legenda-contrato'>Contrato Ativo: Vibra Campo Limpo | Sincronização em Nuvem (Google Drive)</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; border-color: #CBD5E1;'>", unsafe_allow_html=True)

# 2. MOTOR DE LEITURA EM NUVEM
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

# Tratamento de nulos
df_raw['TAREFA / ATIVIDADE'] = df_raw['TAREFA / ATIVIDADE'].fillna("").astype(str).str.strip()
df_raw['OBSERVAÇÕES'] = df_raw.get('OBSERVAÇÕES', "").fillna("").astype(str).str.strip()

# REGRA DE PRESENÇA INTELIGENTE
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

# 3. Filtros
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

# 4. Processamento dos Filtros
df_final = df_raw.copy()
if equipe_sel != "Todos": df_final = df_final[df_final['EQUIPE'] == equipe_sel]
if nome_sel != "Todos": df_final = df_final[df_final['NOME'] == nome_sel]
if tarefa_sel != "Todos": df_final = df_final[df_final['TAREFA / ATIVIDADE'] == tarefa_sel]
if filtro_presenca == "Apenas Presentes": df_final = df_final[df_final['STATUS_PRESENCA'] == "Presente"]
elif filtro_presenca == "Apenas Faltas": df_final = df_final[df_final['STATUS_PRESENCA'] == "Falta"]

if isinstance(datas_sel, (list, tuple)) and len(datas_sel) == 2:
    data_inicio, data_fim = datas_sel
    df_final = df_final[(df_final['DATA'] >= data_inicio) & (df_final['DATA'] <= data_fim)]

# 5. KPIs
total_reg = len(df_final)
total_faltas = len(df_final[df_final['STATUS_PRESENCA'] == "Falta"])
total_pres = total_reg - total_faltas

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total de Lançamentos", f"{total_reg}")
with c2: st.metric("Funcionários Ativos", f"{df_final['NOME'].nunique()}")
with c3: st.metric("Presenças Confirmadas", f"{total_pres}")
with c4: st.metric("Faltas Registradas 🚨", f"{total_faltas}")

st.markdown("<br>", unsafe_allow_html=True)

# 6. Analytics
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

st.markdown("<br>", unsafe_allow_html=True)

# 7. Resumo de Frequência Mensal
st.markdown("### 🗓️ Resumo de Frequência Mensal (Fechamento de Cartão)")
lista_meses = sorted(list(df_raw['MES_ANO'].unique()))
mes_selecionado = st.selectbox("Selecione o Mês para Fechamento de Frequência", lista_meses)
df_mes = df_raw[df_raw['MES_ANO'] == mes
