import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Dashboard Pedagógico PAEBES",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Sistema de Análise Preditiva PAEBES v2.0"}
)

st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 Sistema de Análise Preditiva e Recomposição - PAEBES")
st.markdown("---")

if "processed_data" not in st.session_state:
    st.session_state.processed_data = {
        "df_boletim": None,
        "df_diag": None,
        "df_historico": None,
        "df_matriz": None,
        "alunos_ativos": None,
        "dados_processados": False
    }

st.sidebar.header("📁 Carga de Dados (Inputs)")

col1, col2 = st.sidebar.columns([1, 1])

with col1:
    st.subheader("Obrigatórios")
    arquivo_boletim = st.file_uploader("1️⃣ Boletim Trimestral", type=["csv"], key="boletim")
    arquivo_diagnostico = st.file_uploader("2️⃣ Diagnóstico PAEBES", type=["csv"], key="diag")

with col2:
    st.subheader("Complementares")
    arquivo_historico = st.file_uploader("3️⃣ Histórico (opcional)", type=["csv"], key="hist")
    arquivo_matriz = st.file_uploader("4️⃣ Matriz (opcional)", type=["csv"], key="matriz")

@st.cache_data
def validar_colunas(df, arquivo_tipo):
    colunas_requeridas = {
        "boletim": {"ALUNO", "NOTA", "TURMA"},
        "diagnostico": {"ALUNO", "PROFICIENCIA", "NIVEL"},
    }
    
    requeridas = colunas_requeridas.get(arquivo_tipo, set())
    presente = set(df.columns)
    
    faltando = requeridas - presente
    if faltando:
        return False, f"Faltando: {', '.join(faltando)}"
    return True, "OK"

@st.cache_data
def processar_dados(df_boletim, df_diag):
    df_boletim_proc = df_boletim.copy()
    df_diag_proc = df_diag.copy()
    
    df_boletim_proc['ALUNO'] = df_boletim_proc['ALUNO'].str.strip().str.upper()
    df_diag_proc['ALUNO'] = df_diag_proc['ALUNO'].str.strip().str.upper()
    
    alunos_ativos = df_boletim_proc['ALUNO'].unique()
    df_diag_filtrado = df_diag_proc[df_diag_proc['ALUNO'].isin(alunos_ativos)]
    
    return df_boletim_proc, df_diag_filtrado, alunos_ativos

def calcular_metricas(df_boletim, df_diag):
    return {
        "total_alunos": len(df_boletim),
        "media_notas": df_boletim.get("NOTA", pd.Series()).mean(),
        "media_proficiencia": df_diag.get("PROFICIENCIA", pd.Series()).mean(),
        "alunos_risco": len(df_diag[df_diag.get("NIVEL", "") == "CRÍTICO"])
    }

if arquivo_boletim and arquivo_diagnostico:
    try:
        df_boletim = pd.read_csv(arquivo_boletim)
        df_diag = pd.read_csv(arquivo_diagnostico)
        
        valid_boletim, msg_boletim = validar_colunas(df_boletim, "boletim")
        valid_diag, msg_diag = validar_colunas(df_diag, "diagnostico")
        
        if not valid_boletim or not valid_diag:
            st.error(f"❌ Erro: Boletim: {msg_boletim} | Diagnóstico: {msg_diag}")
        else:
            df_boletim_proc, df_diag_filtrado, alunos_ativos = processar_dados(df_boletim, df_diag)
            
            st.session_state.processed_data = {
                "df_boletim": df_boletim_proc,
                "df_diag": df_diag_filtrado,
                "alunos_ativos": alunos_ativos,
                "dados_processados": True
            }
            
            if arquivo_historico:
                st.session_state.processed_data["df_historico"] = pd.read_csv(arquivo_historico)
            if arquivo_matriz:
                st.session_state.processed_data["df_matriz"] = pd.read_csv(arquivo_matriz)
            
            st.header("📊 Painel de Controle Pedagógico")
            
            metricas = calcular_metricas(df_boletim_proc, df_diag_filtrado)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("👥 Total de Alunos", metricas["total_alunos"])
            col2.metric("📈 Média de Notas", f"{metricas['media_notas']:.1f}")
            col3.metric("🎯 Proficiência Média", f"{metricas['media_proficiencia']:.1f}")
            col4.metric("⚠️ Alunos em Risco", metricas["alunos_risco"])
            
            st.markdown("---")
            
            opcao_analise = st.selectbox(
                "📋 Selecione a análise:",
                [
                    "-- Escolha uma --",
                    "1. Projeção de Proficiência PAEBES",
                    "2. Relatório de Calibração",
                    "3. Gerador de Atividades"
                ]
            )
            
            st.markdown("---")
            
            if opcao_analise == "1. Projeção de Proficiência PAEBES":
                st.subheader("🔮 Classificação Estimada de Proficiência")
                
                df_proj = df_diag_filtrado.copy()
                
                if "PROFICIENCIA" in df_proj.columns:
                    def categorizar(v):
                        if pd.isna(v): return "Sem dados"
                        if v < 200: return "🔴 Abaixo do Básico"
                        if v < 250: return "🟡 Básico"
                        if v < 300: return "🟢 Proficiente"
                        return "🟣 Avançado"
                    
                    df_proj["CATEGORIA"] = df_proj["PROFICIENCIA"].apply(categorizar)
                    
                    tab1, tab2, tab3 = st.tabs(["📊 Resumo", "📋 Detalhes", "📈 Gráficos"])
                    
                    with tab1:
                        dist = df_proj["CATEGORIA"].value_counts()
                        st.dataframe(dist)
                        fig = px.pie(values=dist.values, names=dist.index, title="Distribuição")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tab2:
                        st.dataframe(df_proj[["ALUNO", "PROFICIENCIA", "CATEGORIA"]], use_container_width=True)
                    
                    with tab3:
                        df_top = df_proj.sort_values("PROFICIENCIA", ascending=False).head(20)
                        fig = px.bar(df_top, x="PROFICIENCIA", y="ALUNO", orientation="h", title="Top 20")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    st.success("✅ Análise concluída!")
            
            elif opcao_analise == "2. Relatório de Calibração":
                st.subheader("⚙️ Calibragem do Modelo")
                
                df_calib = df_boletim_proc.merge(
                    df_diag_filtrado[["ALUNO", "PROFICIENCIA", "NIVEL"]],
                    on="ALUNO", how="inner"
                )
                
                if "NOTA" in df_calib.columns and "PROFICIENCIA" in df_calib.columns:
                    df_calib["GAP"] = df_calib["PROFICIENCIA"] - (df_calib["NOTA"] * 10)
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Gap Médio", f"{df_calib['GAP'].mean():.1f}")
                    c2.metric("Risco Médio", f"{df_calib['GAP'].abs().mean():.1f}")
                    
                    altos_risco = df_calib[df_calib['GAP'].abs() > 50]
                    if len(altos_risco) > 0:
                        st.warning(f"⚠️ {len(altos_risco)} alunos com desvio crítico")
                        st.dataframe(altos_risco[["ALUNO", "NOTA", "PROFICIENCIA", "GAP"]], use_container_width=True)
                    
                    fig = px.scatter(df_calib, x="NOTA", y="PROFICIENCIA", title="Correlação", color="NIVEL" if "NIVEL" in df_calib else None)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.success("✅ Calibração concluída!")
            
            elif opcao_analise == "3. Gerador de Atividades":
                st.subheader("📝 Roteiros de Aprendizagem")
                
                if "NIVEL" in df_diag_filtrado.columns:
                    nivel = st.selectbox("Nível:", df_diag_filtrado["NIVEL"].unique())
                    alunos_gr = df_diag_filtrado[df_diag_filtrado["NIVEL"] == nivel]
                    
                    st.info(f"📌 {len(alunos_gr)} alunos no grupo '{nivel}'")
                    
                    if st.button("📥 Gerar Caderno"):
                        st.success("✅ Caderno gerado!")
                        st.balloons()
            
            st.markdown("---")
            st.subheader("💾 Exportar Dados")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv = df_boletim_proc.to_csv(index=False)
                st.download_button("📥 Boletim (CSV)", csv, f"boletim_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
            
            with col2:
                csv = df_diag_filtrado.to_csv(index=False)
                st.download_button("📥 Diagnóstico (CSV)", csv, f"diagnostico_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
            
            with col3:
                rel = f"RELATÓRIO - {datetime.now().strftime('%d/%m/%Y')}\n\nTotal: {metricas['total_alunos']} | Média: {metricas['media_notas']:.2f}"
                st.download_button("📥 Relatório (TXT)", rel, f"relatorio_{datetime.now().strftime('%Y%m%d')}.txt", "text/plain")
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")

else:
    st.warning("👋 Bem-vindo!")
    st.markdown("""
    ### Faça upload de:
    1. **Boletim Trimestral** (obrigatório)
    2. **Diagnóstico PAEBES** (obrigatório)
    
    **Formato esperado:** CSV com headers correspondentes
    """)
    
    with st.expander("📖 Ver exemplo"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Boletim:**")
            st.dataframe(pd.DataFrame({"ALUNO": ["João", "Maria"], "NOTA": [8.5, 7.2], "TURMA": ["6A", "6A"]}), hide_index=True)
        with col2:
            st.write("**Diagnóstico:**")
            st.dataframe(pd.DataFrame({"ALUNO": ["João", "Maria"], "PROFICIENCIA": [285, 240], "NIVEL": ["Proficiente", "Básico"]}), hide_index=True)

st.markdown("---")
st.markdown("<div style='text-align:center; color:#888; font-size:0.85em;'>PAEBES Dashboard v2.0</div>", unsafe_allow_html=True)