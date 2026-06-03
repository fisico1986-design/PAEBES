import streamlit as st
import pandas as pd

st.set_page_config(page_title="PAEBES", layout="wide")
st.title("PAEBES Dashboard")

boletim = st.file_uploader("1. Boletim (CSV)", type=["csv"])
diagnostico = st.file_uploader("2. Diagnóstico (CSV)", type=["csv"])

if boletim and diagnostico:
    df_b = pd.read_csv(boletim)
    df_d = pd.read_csv(diagnostico)
    
    df_b['ALUNO'] = df_b['ALUNO'].str.strip().str.upper()
    df_d['ALUNO'] = df_d['ALUNO'].str.strip().str.upper()
    
    alunos = df_b['ALUNO'].unique()
    df_d = df_d[df_d['ALUNO'].isin(alunos)]
    
    st.write("### Métricas")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Alunos", len(df_b))
    col2.metric("Nota Média", f"{df_b['NOTA'].mean():.1f}")
    col3.metric("Prof. Média", f"{df_d['PROFICIENCIA'].mean():.0f}")
    col4.metric("Em Risco", len(df_d[df_d['NIVEL'] == 'CRÍTICO']))
    
    st.write("### Dados")
    st.dataframe(df_d)
    
    st.download_button("Download", df_d.to_csv(index=False), "dados.csv")
else:
    st.info("Faça upload dos 2 arquivos CSV na barra lateral")
