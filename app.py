import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ===================== CONFIGURAÇÃO =====================
st.set_page_config(
    page_title="Augusto Construções | BI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta de cores da marca
COR_PRIMARIA = "#1E3A8A"   # Azul institucional
COR_SUCESSO  = "#16A34A"   # Verde (presença / positivo)
COR_ALERTA   = "#DC2626"   # Vermelho (faltas / atenção)
COR_NEUTRO   = "#64748B"   # Cinza texto secundário
COR_FUNDO    = "#F1F5F9"

# ===================== ESTILIZAÇÃO GLOBAL =====================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background-color: {COR_FUNDO}; }}
    .main .block-container {{ padding-top: 1.8rem; padding-bottom: 2.5rem; max-width: 96%; }}

    h1 {{ color: {COR_PRIMARIA}; font-weight: 900; letter-spacing: -0.04em; }}

    /* Subtítulo e legenda do contrato (antes sem estilo nenhum) */
    .subtitulo-painel {{
        font-size: 1.05rem; font-weight: 600; color: #334155; margin: 0;
    }}
    .legenda-contrato {{
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 0.82rem; font-weight: 600; color: {COR_PRIMARIA};
        background: #DBEAFE; padding: 4px 12px; border-radius: 999px;
        margin-top: 8px;
    }}

    /* Cards de seção nativos do Streamlit (st.container(border=True)) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF;
        border-radius: 16px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04), 0 4px 14px rgba(15,23,42,0.03);
        padding: 4px 6px;
    }}

    /* Esconder a barra de ferramentas do Plotly (limpo, sem clutter) */
    .modebar {{ display: none !important; }}

    /* Abas: parecem botões de navegação, não links de texto perdidos */
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; margin-bottom: 4px; }}
    .stTabs [data-baseweb="tab"] {{
        height: 44px; background-color: #FFFFFF; border-radius: 10px;
        border: 1px solid #E2E8F0; padding: 0 20px; font-weight: 700;
        color: #64748B;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COR_PRIMARIA} !important; color: #FFFFFF !important;
        border-color: {COR_PRIMARIA} !important;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{ display:none; }}
    .stTabs [data-baseweb="tab-border"] {{ display:none; }}
    </style>
    """, unsafe_allow_html=True)


def secao_titulo(icone, texto, cor=COR_PRIMARIA):
    """Cabeçalho de seção com ícone em badge colorido."""
    st.markdown(f"""
        <div style='display:flex; align-items:center; gap:10px; margin: 4px 0 14px 4px;'>
            <div style='background:{cor}1A; color:{cor}; width:34px; height:34px;
                        border-radius:10px; display:flex; align-items:center;
                        justify-content:center; font-size:1.05rem;'>{icone}</div>
            <span style='font-size:1.2rem; font-weight:800; color:#0F172A;'>{texto}</span>
        </div>
    """, unsafe_allow_html=True)


def kpi_card(label, valor, icone, cor, destaque=False):
    """Card de KPI. destaque=True dá fundo colorido (usar só para o número que
    o chefe TEM que ver primeiro — ex: faltas). Os demais ficam neutros em
    branco para não competir por atenção."""
    if destaque:
        bg = f"{cor}"
        cor_label = "rgba(255,255,255,0.85)"
        cor_valor = "#FFFFFF"
        borda = "none"
        sombra = f"0 8px 20px {cor}40"
    else:
        bg = "#FFFFFF"
        cor_label = COR_NEUTRO
        cor_valor = cor
        borda = "1px solid #E2E8F0"
        sombra = "0 1px 2px rgba(15,23,42,0.04), 0 4px 14px rgba(15,23,42,0.03)"

    st.markdown(f"""
        <div style='background:{bg}; border-radius:16px; padding:18px 22px;
                    border:{borda}; box-shadow:{sombra}; height:100%;'>
            <div style='display:flex; align-items:center; justify-content:space-between;'>
                <span style='font-size:0.72rem; font-weight:700; color:{cor_label};
                            text-transform:uppercase; letter-spacing:0.06em;'>{label}</span>
                <span style='font-size:1.1rem;'>{icone}</span>
            </div>
            <div style='font-size:2.3rem; font-weight:800; color:{cor_valor}; margin-top:6px; line-height:1;'>{valor}</div>
        </div>
    """, unsafe_allow_html=True)


def grafico_barra_horizontal(serie, cor, altura=260):
    """Gráfico de barras horizontais legível (nomes longos não cortam mais o eixo)."""
    serie = serie.sort_values(ascending=True)
    fig = go.Figure(go.Bar(
        x=serie.values,
        y=serie.index,
        orientation='h',
        marker_color=cor,
        text=serie.values,
        textposition='outside',
        textfont=dict(size=12, color='#0F172A'),
    ))
    fig.update_layout(
        height=altura,
        margin=dict(l=10, r=30, t=10, b=10),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#E2E8F0', zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=12, color='#334155')),
        font=dict(family='Inter, sans-serif'),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


# ===================== CABEÇALHO (card "hero") =====================
st.markdown(f"""
    <div style='background:linear-gradient(120deg, #FFFFFF 0%, #F8FAFC 100%);
                border:1px solid #E2E8F0; border-radius:18px; padding:20px 28px;
                box-shadow:0 1px 2px rgba(15,23,42,0.04), 0 6px 18px rgba(15,23,42,0.04);
                display:flex; align-items:center; gap:22px; margin-bottom:22px;'>
        <img src='https://i.ibb.co/tPFBw1h5/logo.jpg' style='width:80px; height:80px;
             border-radius:14px; object-fit:cover;'/>
        <div>
            <div style='font-size:2.1rem; font-weight:900; color:{COR_PRIMARIA};
                        letter-spacing:-0.03em; line-height:1.1;'>AUGUSTO ENGENHARIA</div>
            <div style='font-size:1rem; font-weight:600; color:#334155; margin-top:2px;'>
                Painel de Desempenho Operacional</div>
            <div class='legenda-contrato' style='margin-top:10px;'>
                🏗️ Contrato Ativo: Vibra Campo Limpo &nbsp;•&nbsp; ☁️ Sincronização em Nuvem (Google Drive)
            </div>
        </div>
    </div>
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
df_raw['NOME'] = df_raw['NOME'].fillna("").astype(str).str.strip()
df_raw['EQUIPE'] = df_raw['EQUIPE'].fillna("").astype(str).str.strip()

# Regra de Presença
# A partir de 07/2026 as faltas passaram a ser registradas na coluna OBSERVAÇÕES
# (e, às vezes, ainda na TAREFA / ATIVIDADE, como fallback). Por isso a checagem
# precisa olhar as duas colunas juntas. Não usamos mais "TAREFA vazia = Falta".
palavras_falta = ['FALTOU', 'AUSENTE']
texto_busca_falta = (df_raw['TAREFA / ATIVIDADE'] + " " + df_raw['OBSERVAÇÕES']).str.upper()
df_raw['STATUS_PRESENCA'] = texto_busca_falta.apply(
    lambda x: "Falta" if any(p in x for p in palavras_falta) else "Presente"
)

# Coluna para identificar quem realmente pertence à obra
palavras_excluir = ['EMPRESTADO', 'TRANSFERIDO', 'OUTRA OBRA', 'CEDIDO', 'FOI PARA']
df_raw['PERTENCE_A_OBRA'] = ~df_raw['OBSERVAÇÕES'].str.upper().str.contains('|'.join(palavras_excluir), na=False)

df_raw['MES_ANO'] = df_raw['DATETIME'].dt.strftime('%m/%Y - %B')

# ===================== FILTROS =====================
st.sidebar.markdown("<h2 style='font-size:1.2rem; color:#0F172A; font-weight:700; margin-bottom:15px;'>🎯 Painel de Filtros</h2>", unsafe_allow_html=True)

equipes = ["Todos"] + sorted(list(df_raw['EQUIPE'].dropna().unique()))
equipe_sel = st.sidebar.selectbox("Filtro por Equipe", equipes)

df_func_ativos = df_raw[df_raw['PERTENCE_A_OBRA'] == True]

df_filt_nome = df_func_ativos[df_func_ativos['EQUIPE'] == equipe_sel] if equipe_sel != "Todos" else df_func_ativos
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
total_func_ativos = df_func_ativos['NOME'].nunique()
taxa_presenca = round((total_pres / total_reg) * 100, 1) if total_reg > 0 else 0.0

if taxa_presenca >= 90:
    cor_taxa = COR_SUCESSO
elif taxa_presenca >= 80:
    cor_taxa = "#D97706"
else:
    cor_taxa = COR_ALERTA

c1, c2, c3, c4, c5 = st.columns(5)
with c1: kpi_card("Total de Lançamentos", f"{total_reg}", "📋", COR_PRIMARIA)
with c2: kpi_card("Funcionários Ativos", f"{total_func_ativos}", "👷", COR_PRIMARIA)
with c3: kpi_card("Presenças Confirmadas", f"{total_pres}", "✅", COR_SUCESSO)
with c4: kpi_card("Faltas Registradas", f"{total_faltas}", "🚨", "#DC2626", destaque=True)
with c5: kpi_card("Taxa de Presença", f"{taxa_presenca}%", "📈", cor_taxa)

st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

# ===================== NAVEGAÇÃO EM ABAS =====================
# Em vez de empilhar tudo numa rolagem só, o painel agora abre direto na
# "Visão Geral" (o que o chefe precisa ver em 5 segundos) e deixa o
# fechamento mensal e o detalhamento linha-a-linha em abas separadas,
# acessadas só por quem precisa investigar mais fundo.
tab_geral, tab_fechamento, tab_detalhe = st.tabs([
    "📊  Visão Geral", "🗓️  Fechamento Mensal", "📋  Detalhamento"
])

# --------------------- ABA 1: VISÃO GERAL ---------------------
with tab_geral:
    with st.container(border=True):
        secao_titulo("📊", "Análise de Desempenho")
        st.caption("Ranking acumulado no período filtrado — não representa uma linha do tempo.")

        g1, g2, g3 = st.columns(3)

        with g1:
            st.markdown("**Tarefas Mais Frequentes**")
            if not df_final.empty:
                servicos = df_final['TAREFA / ATIVIDADE'].value_counts().head(6)
                grafico_barra_horizontal(servicos, COR_PRIMARIA)
            else:
                st.info("Sem dados no período.")

        with g2:
            st.markdown("**Maior Nº de Presenças**")
            if not df_final.empty:
                presenca = (df_final.groupby('NOME')['STATUS_PRESENCA']
                           .apply(lambda x: (x == 'Presente').sum())
                           .sort_values(ascending=False).head(6))
                grafico_barra_horizontal(presenca, COR_SUCESSO)
            else:
                st.info("Sem dados no período.")

        with g3:
            st.markdown("**Aproveitamento por Equipe**")
            if not df_final.empty:
                por_equipe = df_final.groupby('EQUIPE').agg(
                    QTD_PESSOAS=('NOME', 'nunique'),
                    TRABALHO_REALIZADO=('TAREFA / ATIVIDADE', 'count')
                ).reset_index()
                st.dataframe(
                    por_equipe,
                    use_container_width=True,
                    height=260,
                    hide_index=True,
                    column_config={
                        "TRABALHO_REALIZADO": st.column_config.ProgressColumn(
                            "Trabalho Realizado",
                            min_value=0,
                            max_value=int(por_equipe['TRABALHO_REALIZADO'].max()) if not por_equipe.empty else 1,
                            format="%d",
                        ),
                        "QTD_PESSOAS": st.column_config.NumberColumn("Qtd. Pessoas"),
                        "EQUIPE": st.column_config.TextColumn("Equipe"),
                    }
                )
            else:
                st.info("Sem dados no período.")

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

    # Lista de funcionários fica escondida por padrão (informação de apoio,
    # não é o que o chefe precisa ver primeiro) — um clique revela.
    with st.expander(f"👥 Ver lista completa de Funcionários Ativos da Obra ({total_func_ativos})"):
        st.dataframe(
            df_func_ativos[['NOME', 'EQUIPE']].drop_duplicates().sort_values('NOME'),
            hide_index=True,
            use_container_width=True
        )

# --------------------- ABA 2: FECHAMENTO MENSAL ---------------------
with tab_fechamento:
    with st.container(border=True):
        secao_titulo("🗓️", "Resumo de Frequência Mensal (Fechamento de Cartão)")
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

            # Formatação condicional: faltas > 0 saltam aos olhos em vermelho
            def destaca_falta(val):
                if isinstance(val, (int, float)) and val > 0:
                    return f'background-color:#FEE2E2; color:{COR_ALERTA}; font-weight:700;'
                return ''

            def destaca_presenca(val):
                if isinstance(val, (int, float)) and val > 0:
                    return f'color:{COR_SUCESSO}; font-weight:600;'
                return ''

            # Styler.applymap() foi descontinuado em versões recentes do pandas
            # em favor de Styler.map(). Usamos map() e caímos para applymap()
            # só se estiver rodando numa versão bem antiga do pandas.
            estilo = df_fechamento.style
            try:
                estilo = estilo.map(destaca_falta, subset=['DIAS DE FALTA'])
                estilo = estilo.map(destaca_presenca, subset=['DIAS NA OBRA'])
            except AttributeError:
                estilo = estilo.applymap(destaca_falta, subset=['DIAS DE FALTA'])
                estilo = estilo.applymap(destaca_presenca, subset=['DIAS NA OBRA'])
            styled = estilo

            st.dataframe(styled, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum dado encontrado para o mês selecionado.")

# --------------------- ABA 3: DETALHAMENTO ---------------------
with tab_detalhe:
    with st.container(border=True):
        secao_titulo("📋", "Visão Detalhada dos Registros (Linha por Linha)")
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
