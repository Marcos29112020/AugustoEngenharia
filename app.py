import streamlit as st
import pandas as pd
from datetime import datetime

# ===================== CONFIGURAÇÃO DA PÁGINA =====================
st.set_page_config(
    page_title="Augusto Construções BI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== ESTILIZAÇÃO PROFISSIONAL =====================
st.markdown("""
    <style>
    .stApp { background-color: #F1F5F9; }
    .main .block-container { padding-top: 1.8rem; padding-bottom: 2rem; max-width: 98%; }
    .marca-principal { 
        color: #1E3A8A; 
        font-weight: 900; 
        font-size: 2.8rem; 
        letter-spacing: -0.04em; 
        margin-bottom: 0.2rem; 
    }
    .subtitulo-painel { 
        color: #334155; 
        font-weight: 700; 
        font-size: 1.65rem; 
        margin-top: 0; 
    }
    .legenda-contrato { 
        color: #64748B; 
        font-size: 1rem; 
        margin-top: 0; 
    }
    [data-testid="stMetricContainer"] {
        background-color: #FFFFFF;
        padding: 25px 30px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='marca-principal'>🏗️ AUGUSTO CONSTRUÇÕES</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo-painel'>Painel de Desempenho Operacional</p>", unsafe_allow_html=True)
st.markdown("<p class='legenda-contrato'>Contrato Ativo • Vibra Campo Limpo • Sincronização em Nuvem (Google Drive)</p>", unsafe_allow_html=True)
st.markdown("---")

# ===================== CONFIGURAÇÃO DO GOOGLE SHEETS =====================
st.sidebar.header("🔗 Conexão com Dados")
URL_GOOGLE_DRIVE = st.sidebar.text_input(
    "Link Publicado do Google Sheets (CSV)",
    value="https://docs.google.com/spreadsheets/d/e/SEU_LINK_AQUI/pub?output=csv",
    help="Vá em Arquivo > Compartilhar > Publicar na Web > Copie o link com output=csv"
)

@st.cache_data(ttl=300)  # Atualiza a cada 5 minutos
def load_data_cloud(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(col).strip().upper() for col in df.columns]
        
        if 'DATA' in df.columns:
            # Tenta diferentes formatos de data
            df['DATETIME'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y', errors='coerce')
            if df['DATETIME'].isna().all():
                df['DATETIME'] = pd.to_datetime(df['DATA'], format='%d%m%Y', errors='coerce')
            
            df['DATA'] = df['DATETIME'].dt.date
            df = df.dropna(subset=['DATA'])
        return df
    except Exception as e:
        st.error(f"❌ Erro ao conectar com o Google Drive: {e}")
        st.info("Verifique se o link está publicado corretamente como CSV.")
        return None

df_raw = load_data_cloud(URL_GOOGLE_DRIVE)

if df_raw is None or df_raw.empty:
    st.stop()

# ===================== TRATAMENTO DE DADOS =====================
df_raw['TAREFA  ATIVIDADE'] = df_raw['TAREFA  ATIVIDADE'].fillna('').astype(str).str.strip()
df_raw['OBSERVAÇÕES'] = df_raw.get('OBSERVAÇÕES', '').fillna('').astype(str).str.strip()

# Regra Inteligente de Presença
df_raw['STATUS_PRESENCA'] = df_raw['TAREFA  ATIVIDADE'].str.upper().apply(
    lambda x: 'Falta' if any(kw in x for kw in ['FALTOU', 'AUSENTE', 'FALTA']) or x.strip() == '' else 'Presente'
)

# Mês/Ano em Português
df_raw['MES_ANO'] = df_raw['DATETIME'].dt.strftime('%m/%Y - %B')
meses_pt = {
    'January':'Janeiro','February':'Fevereiro','March':'Março','April':'Abril',
    'May':'Maio','June':'Junho','July':'Julho','August':'Agosto',
    'September':'Setembro','October':'Outubro','November':'Novembro','December':'Dezembro'
}
for en, pt in meses_pt.items():
    df_raw['MES_ANO'] = df_raw['MES_ANO'].str.replace(en, pt, case=False)

# ===================== FILTROS LATERAIS =====================
st.sidebar.markdown("### 🎯 Filtros")

equipes = ["Todos"] + sorted(df_raw['EQUIPE'].dropna().unique().tolist())
equipe_sel = st.sidebar.selectbox("Equipe", equipes)

# Filtra nomes conforme equipe
df_filt_nome = df_raw[df_raw['EQUIPE'] == equipe_sel] if equipe_sel != "Todos" else df_raw
nomes = ["Todos"] + sorted(df_filt_nome['NOME'].dropna().unique().tolist())
nome_sel = st.sidebar.selectbox("Funcionário", nomes)

filtro_presenca = st.sidebar.radio("Frequência", ["Todos", "Apenas Presentes", "Apenas Faltas"])

df_filt_tar = df_raw[df_raw['STATUS_PRESENCA'] == "Presente"]
tarefas = ["Todos"] + sorted(df_filt_tar['TAREFA  ATIVIDADE'].dropna().unique().tolist())
tarefa_sel = st.sidebar.selectbox("Tarefa / Atividade", tarefas)

data_min, data_max = df_raw['DATA'].min(), df_raw['DATA'].max()
datas_sel = st.sidebar.date_input("Período", [data_min, data_max], min_value=data_min, max_value=data_max)

busca_obs = st.sidebar.text_input("🔍 Buscar em Observações", "")

# ===================== APLICAÇÃO DOS FILTROS =====================
df_final = df_raw.copy()

if equipe_sel != "Todos": df_final = df_final[df_final['EQUIPE'] == equipe_sel]
if nome_sel != "Todos": df_final = df_final[df_final['NOME'] == nome_sel]
if tarefa_sel != "Todos": df_final = df_final[df_final['TAREFA  ATIVIDADE'] == tarefa_sel]
if filtro_presenca == "Apenas Presentes": df_final = df_final[df_final['STATUS_PRESENCA'] == "Presente"]
if filtro_presenca == "Apenas Faltas": df_final = df_final[df_final['STATUS_PRESENCA'] == "Falta"]
if busca_obs:
    df_final = df_final[df_final['OBSERVAÇÕES'].str.contains(busca_obs, case=False, na=False)]

if len(datas_sel) == 2:
    df_final = df_final[(df_final['DATA'] >= datas_sel[0]) & (df_final['DATA'] <= datas_sel[1])]

# ===================== KPIs =====================
total_reg = len(df_final)
total_faltas = len(df_final[df_final['STATUS_PRESENCA'] == "Falta"])
total_pres = total_reg - total_faltas

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Total de Lançamentos", f"{total_reg:,}")
with col2: st.metric("Funcionários Ativos", df_final['NOME'].nunique())
with col3: st.metric("Presenças Confirmadas", f"{total_pres:,}")
with col4: st.metric("Faltas Registradas", f"{total_faltas:,}", delta=None)

# ===================== GRÁFICOS =====================
st.markdown("### 📊 Análise Visual")
g1, g2 = st.columns(2)

with g1:
    st.markdown("**Volume Diário de Trabalho**")
    if not df_final.empty:
        timeline = df_final[df_final['STATUS_PRESENCA'] == 'Presente'].groupby('DATA').size()
        st.line_chart(timeline, use_container_width=True, color="#1E3A8A")
    else:
        st.info("Sem dados no período selecionado.")

with g2:
    st.markdown("**Top 5 Atividades**")
    if not df_final.empty:
        top_ativ = (df_final[df_final['STATUS_PRESENCA'] == 'Presente']['TAREFA  ATIVIDADE']
                   .value_counts().head(5))
        st.bar_chart(top_ativ, use_container_width=True)

# ===================== FECHAMENTO MENSAL =====================
st.markdown("### 🗓️ Fechamento Mensal de Frequência")
meses = sorted(df_raw['MES_ANO'].unique())
mes_sel = st.selectbox("Selecione o Mês", meses)

df_mes = df_raw[df_raw['MES_ANO'] == mes_sel]

if not df_mes.empty:
    pres = df_mes[df_mes['STATUS_PRESENCA']=='Presente'].groupby(['EQUIPE','NOME'])['DATA'].nunique().reset_index(name='DIAS NA OBRA')
    falt = df_mes[df_mes['STATUS_PRESENCA']=='Falta'].groupby(['EQUIPE','NOME'])['DATA'].nunique().reset_index(name='DIAS DE FALTA')
    
    base = df_mes[['EQUIPE','NOME']].drop_duplicates()
    fechamento = base.merge(pres, on=['EQUIPE','NOME'], how='left').merge(falt, on=['EQUIPE','NOME'], how='left').fillna(0)
    fechamento = fechamento.astype({'DIAS NA OBRA': int, 'DIAS DE FALTA': int})
    
    st.dataframe(fechamento.sort_values(by=['EQUIPE','NOME']), use_container_width=True, hide_index=True)

# ===================== VISÃO DETALHADA =====================
st.markdown("### 📋 Visão Detalhada dos Registros")
df_exib = df_final.drop(columns=['STATUS_PRESENCA', 'MES_ANO', 'DATETIME'], errors='ignore')

# Coloca Observações no final
if 'OBSERVAÇÕES' in df_exib.columns:
    cols = [c for c in df_exib.columns if c != 'OBSERVAÇÕES'] + ['OBSERVAÇÕES']
    df_exib = df_exib[cols]

st.dataframe(
    df_exib,
    use_container_width=True,
    hide_index=True,
    column_config={
        "OBSERVAÇÕES": st.column_config.TextColumn("Observações", width="large")
    }
)

st.caption(f"Atualizado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
