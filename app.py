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
                
                df_proj = df_diag_filtrado.copy()](#)

