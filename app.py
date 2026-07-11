import streamlit as st
import pandas as pd
import datetime

# 1. Configuração da página do navegador (Visual Executivo Premium)
st.set_page_config(
    page_title="Augusto Construções | BI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Premium - Identidade Visual Augusto Construções com Super Contraste na Lateral
st.markdown("""
    <style>
    /* Fundo institucional cinza claro da área de gráficos */
    .stApp { background-color: #F1F5F9; }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; max-width: 95%; }
    
    /* Topo do Painel */
    .marca-principal { color: #1E3A8A; font-weight: 900; font-size: 2.6rem; letter-spacing: -0.05em; margin-bottom: 0rem; line-height: 1.1; }
    .subtitulo-painel { color: #334155; font-weight: 700; font-size: 1.6rem; margin-top: 0.2rem; margin-bottom: 0.2rem; letter-spacing: -0.03em; }
    .legenda-contrato { color: #64748B; font-size: 0.95rem; margin-top: 0rem; margin-bottom: 0.5rem; }
    h3 { color: #1E293B; font-weight: 700; font-size: 1.4rem; margin-top: 1.5rem; margin-bottom: 1rem; }
    
    /* Cartões de Métricas Estilizados */
    [data-testid="stMetricContainer"] {
        background-color: #FFFFFF; padding: 22px 25px; border-radius: 12px; border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    [data-testid="stMetricLabel"] { color: #475569 !important; font-weight: 600 !important; font-size: 0.95rem !important; }
    [data-testid="stMetricValue"] { color: #0F172A !important; font-weight: 700 !important; font-size: 2rem !important; }
    
    /* =========================================================================
       ⚠️ BLINDAGEM DA BARRA LATERAL: Força Fundo Escuro e Textos Brancos para Contraste Máximo
       ========================================================================= */
    [data-testid="stSidebar"] { 
        background-color: #1E293B !important; 
        border-right: 1px solid #334155; 
    }
    /* Força a cor branca em todos os textos, labels e botões de rádio da barra lateral */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stWidgetLabel {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    /* Estiliza os fundos dos inputs dentro da lateral para não sumirem no fundo escuro */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: #334155 !important;
        border-radius: 8px;
    }
    [data-testid="stSidebar"] .stSelectbox div {
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Cabeçalho Institucional Estilizado
st.markdown("<h1 class='marca-principal'>🏗️ AUGUSTO CONSTRUÇÕES</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo-painel'>Painel de Desempenho Operacional</p>", unsafe_allow_html=True)
st.markdown("<p class='legenda-contrato'>Contrato Ativo: Vibra Campo Limpo | Sincronização em Nuvem (Google Drive)</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; border-color: #CBD5E1;'>", unsafe_allow_html=True)

# 2. MOTOR DE LEITURA EM NUVEM FIXO E DEFINITIVO
URL_GOOGLE_DRIVE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR3iZWG8EA_Q6_cxiWyr_opAjXEZ6Vulx829avjgamQQwjicTC9cuOqVtlXQz3eYe7pUH3MAMtG9ZkR/pub?gid=1542027995&single=true&output=csv"

@st.cache_data(ttl=0)  # TTL=0 garante atualização instantânea a cada F5
def load_data_cloud(url):
    # Força a leitura inicial de todas as colunas como strings para evitar incompatibilidades
    df = pd.read_csv(url, dtype=str)
    
    if df.shape[1] < 4:
        st.error("A tabela do Google Drive precisa conter pelo menos 4 colunas básicas.")
        st.stop()
        
    # Renomeação por índice absoluto garantido
    df.columns = ['DATA_ORIGINAL', 'EQUIPE', 'NOME', 'TAREFA_ATIVIDADE'] + list(df.columns[4:])
    
    # Conversão rigorosa de datas para o ecossistema Python
    df['DATETIME'] = pd.to_datetime(df['DATA_ORIGINAL'], format='%d/%m/%Y', errors='coerce')
    df['DATA'] = df['DATETIME'].dt.date
    
    # Elimina linhas sem data válida
    df = df.dropna(subset=['DATA'])
    return df

try:
    df_raw = load_data_cloud(URL_GOOGLE_DRIVE)
except Exception as e:
    st.error(f"Erro crítico ao ler planilha em nuvem: {e}")
    st.stop()

if df_raw is None or df_raw.empty:
    st.error("Nenhum dado válido encontrado no link fornecido.")
    st.stop()

# Saneamento e limpeza de dados nulos
df_raw['EQUIPE'] = df_raw['EQUIPE'].fillna("Não Informado").astype(str).str.strip()
df_raw['NOME'] = df_raw['NOME'].fillna("Não Informado").astype(str).str.strip()
df_raw['TAREFA_ATIVIDADE'] = df_raw['TAREFA_ATIVIDADE'].fillna("").astype(str).str.strip()

# REGRA DE PRESENÇA BLINDADA: Identifica faltas textuais ou células vazias
df_raw['STATUS_PRESENCA'] = df_raw['TAREFA_ATIVIDADE'].str.upper().apply(
    lambda x: "Falta" if "FALTOU" in x or "AUSENTE" in x or x == "" else "Presente"
)

# Geração das colunas de fechamento mensal por extenso
df_raw['MES_ANO'] = df_raw['DATETIME'].dt.strftime('%m/%Y - %B')
meses_pt = {
    'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril',
    'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto',
    'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
}
for en, pt in meses_pt.items():
    df_raw['MES_ANO'] = df_raw['MES_ANO'].str.replace(en, pt, case=False)

# 3. FILTROS OPERACIONAIS NA BARRA LATERAL
st.sidebar.markdown("<h2 style='font-size:1.2rem; color:#FFFFFF; font-weight:700; margin-bottom:15px; margin-top:0px;'>🎯 Painel de Filtros</h2>", unsafe_allow_html=True)

equipes = ["Todos"] + sorted(list(df_raw['EQUIPE'].unique()))
equipe_sel = st.sidebar.selectbox("Filtro por Equipe", equipes)

df_filt_nome = df_raw[df_raw['EQUIPE'] == equipe_sel] if equipe_sel != "Todos" else df_raw
nomes = ["Todos"] + sorted(list(df_filt_nome['NOME'].unique()))
nome_sel = st.sidebar.selectbox("Filtro por Funcionário", nomes)

filtro_presenca = st.sidebar.radio("Filtro de Frequência", ["Todos", "Apenas Presentes", "Apenas Faltas"])

df_filt_tar = df_raw[df_raw['STATUS_PRESENCA'] == "Presente"]
tarefas = ["Todos"] + sorted(list(df_filt_tar['TAREFA_ATIVIDADE'].unique()))
tarefa_sel = st.sidebar.selectbox("Filtro por Tarefa / Atividade", tarefas)

# Extração de limites de tempo
data_min = df_raw['DATA'].min()
data_max = df_raw['DATA'].max()
if isinstance(data_min, datetime.datetime): data_min = data_min.date()
if isinstance(data_max, datetime.datetime): data_max = data_max.date()

datas_sel = st.sidebar.date_input(
    "Intervalo de Tempo", 
    [data_min, data_max], 
    min_value=data_min, 
    max_value=data_max
)

# 4. PROCESSAMENTO E FILTRAGEM DO DATAFRAME FINAL
df_final = df_raw.copy()
if equipe_sel != "Todos": df_final = df_final[df_final['EQUIPE'] == equipe_sel]
if nome_sel != "Todos": df_final = df_final[df_final['NOME'] == nome_sel]
if tarefa_sel != "Todos": df_final = df_final[df_final['TAREFA_ATIVIDADE'] == tarefa_sel]

if filtro_presenca == "Apenas Presentes": 
    df_final = df_final[df_final['STATUS_PRESENCA'] == "Presente"]
elif filtro_presenca == "Apenas Faltas": 
    df_final = df_final[df_final['STATUS_PRESENCA'] == "Falta"]

# Correção lógica contra seleções parciais ou clique único no calendário do Streamlit
if isinstance(datas_sel, (list, tuple)):
    if len(datas_sel) == 2:
        df_final = df_final[(df_final['DATA'] >= datas_sel[0]) & (df_final['DATA'] <= datas_sel[1])]
    elif len(datas_sel) == 1:
        df_final = df_final[df_final['DATA'] == datas_sel[0]]

# 5. CARTÕES EXECUTIVOS DE MÉTRICAS (KPIs)
total_reg = len(df_final)
total_faltas = len(df_final[df_final['STATUS_PRESENCA'] == "Falta"])
total_pres = total_reg - total_faltas

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total de Lançamentos", f"{total_reg}")
with c2: st.metric("Funcionários Ativos", f"{df_final['NOME'].nunique()}")
with c3: st.metric("Presenças Confirmadas", f"{total_pres}")
with c4: st.metric("Faltas Registradas 🚨", f"{total_faltas}")

st.markdown("<br>", unsafe_allow_html=True)

# 6. ÁREA DE ANALYTICS E GRÁFICOS GERENCIAIS
st.markdown("### 📊 Indicadores e Gráficos Gerenciais")
g1, g2 = st.columns(2)

with g1:
    st.markdown("**Volume Diário de Trabalho (Linha do Tempo)**")
    if not df_final.empty:
        df_timeline = df_final[df_final['STATUS_PRESENCA'] == 'Presente'].groupby('DATA').size().reset_index(name='Registros')
        df_timeline = df_timeline.set_index('DATA')
        st.line_chart(df_timeline, color="#1E3A8A", use_container_width=True)
    else:
        st.info("Sem dados operacionais para o período selecionado.")

with g2:
    st.markdown("**Top 5 Atividades Mais Executadas**")
    df_ranking_data = df_final[(df_final['STATUS_PRESENCA'] == 'Presente') & (df_final['TAREFA_ATIVIDADE'] != "")]
    if not df_ranking_data.empty:
        df_ranking = df_ranking_data['TAREFA_ATIVIDADE'].value_counts().head(5)
        st.bar_chart(df_ranking, color="#475569", use_container_width=True)
    else:
        st.info("Sem atividades para ranquear no filtro selecionado.")

st.markdown("<br>", unsafe_allow_html=True)

# 7. RESUMO DE FREQUÊNCIA MENSAL (FECHAMENTO DE CARTÃO)
st.markdown("### 🗓️ Resumo de Frequência Mensal (Fechamento de Cartão)")
st.markdown("Auditoria consolidada de dias trabalhados e faltas por funcionário no mês selecionado.")

lista_meses = sorted(list(df_raw['MES_ANO'].unique()))
mes_selecionado = st.selectbox("Selecione o Mês para Fechamento de Frequência", lista_meses)
df_mes = df_raw[df_raw['MES_ANO'] == mes_selecionado]

if not df_mes.empty:
    df_presencas_calc = df_mes[df_mes['STATUS_PRESENCA'] == 'Presente'].groupby(['EQUIPE', 'NOME'])['DATA'].nunique().reset_index(name='DIAS NA OBRA')
