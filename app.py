import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="PAEBES Dashboard", layout="wide")

st.title("🎯 Sistema de Análise PAEBES")
st.markdown("---")

# Sidebar
st.sidebar.header("📁 Carga de Dados")
st.sidebar.markdown("**Arquivos obrigatórios:**")

arquivo_boletim = st.sidebar.file_uploader("Boletim Trimestral (CSV)", type=["csv"], key="boletim")
arquivo_diagnostico = st.sidebar.file_uploader("Diagnóstico PAEBES (CSV)", type=["csv"], key="diag")

st.sidebar.markdown("**Complementares:**")
arquivo_historico = st.sidebar.file_uploader("Histórico (opcional)", type=["csv"], key="hist")
arquivo_matriz = st.sidebar.file_uploader("Matriz (opcional)", type=["csv"], key="matriz")

# Processamento
if arquivo_boletim and arquivo_diagnostico:
    try:
        df_boletim = pd.read_csv(arquivo_boletim)
        df_diag = pd.read_csv(arquivo_diagnostico)
        
        # Limpeza
        df_boletim['ALUNO'] = df_boletim['ALUNO'].str.strip().str.upper()
        df_diag['ALUNO'] = df_diag['ALUNO'].str.strip().str.upper()
        
        # Filtragem
        alunos_ativos = df_boletim['ALUNO'].unique()
        df_diag = df_diag[df_diag['ALUNO'].isin(alunos_ativos)]
        
        # Dashboard
        st.header("📊 Painel de Controle")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👥 Alunos", len(df_boletim))
        col2.metric("📈 Nota Média", f"{df_boletim['NOTA'].mean():.1f}")
        col3.metric("🎯 Profic. Média", f"{df_diag['PROFICIENCIA'].mean():.0f}")
        col4.metric("⚠️ Em Risco", len(df_diag[df_diag['NIVEL'] == 'CRÍTICO']))
        
        st.markdown("---")
        
        # Menu de análises
        opcao = st.radio("Selecione a análise:", 
            ["Projeção de Proficiência", "Calibração e Risco", "Detalhes dos Alunos"])
        
        st.markdown("---")
        
        # ANÁLISE 1
        if opcao == "Projeção de Proficiência":
            st.subheader("🔮 Classificação de Proficiência")
            
            def categorizar(v):
                if pd.isna(v): return "Sem dados"
                if v < 200: return "Abaixo do Básico"
                if v < 250: return "Básico"
                if v < 300: return "Proficiente"
                return "Avançado"
            
            df_diag['CATEGORIA'] = df_diag['PROFICIENCIA'].apply(categorizar)
            
            # Resumo
            st.write("**Distribuição de Alunos:**")
            dist = df_diag['CATEGORIA'].value_counts()
            st.bar_chart(dist)
            
            # Tabela
            st.write("**Detalhes:**")
            st.dataframe(df_diag[['ALUNO', 'PROFICIENCIA', 'CATEGORIA']], use_container_width=True, hide_index=True)
            
            st.success("✅ Análise concluída!")
        
        # ANÁLISE 2
        elif opcao == "Calibração e Risco":
            st.subheader("⚙️ Calibragem do Modelo")
            
            df_merge = df_boletim.merge(df_diag[['ALUNO', 'PROFICIENCIA', 'NIVEL']], on='ALUNO', how='inner')
            df_merge['GAP'] = df_merge['PROFICIENCIA'] - (df_merge['NOTA'] * 10)
            
            col1, col2 = st.columns(2)
            col1.metric("Gap Médio", f"{df_merge['GAP'].mean():.1f}")
            col2.metric("Risco Médio", f"{df_merge['GAP'].abs().mean():.1f}")
            
            altos_risco = df_merge[df_merge['GAP'].abs() > 50]
            
            if len(altos_risco) > 0:
                st.warning(f"⚠️ {len(altos_risco)} alunos com desvio crítico")
                st.dataframe(altos_risco[['ALUNO', 'NOTA', 'PROFICIENCIA', 'GAP']], use_container_width=True, hide_index=True)
            else:
                st.success("✅ Nenhum desvio crítico detectado!")
            
            st.write("**Correlação: Nota vs Proficiência**")
            st.scatter_chart(df_merge.set_index('ALUNO')[['NOTA', 'PROFICIENCIA']])
        
        # ANÁLISE 3
        else:
            st.subheader("📋 Detalhes Completos")
            
            df_final = df_boletim.merge(df_diag, on='ALUNO', how='inner')
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            
            csv = df_final.to_csv(index=False)
            st.download_button("📥 Baixar Dados (CSV)", csv, f"paebes_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
        st.markdown("---")
        st.markdown("<div style='text-align:center; color:#888;'>PAEBES Dashboard v2.1</div>", unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")

else:
    st.warning("👋 Faça upload dos arquivos na barra lateral para começar!")
    
    with st.expander("📖 Ver exemplo de formato"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Boletim.csv:**")
            exemplo_boletim = pd.DataFrame({
                'ALUNO': ['João Silva', 'Maria Santos'],
                'NOTA': [8.5, 7.2],
                'TURMA': ['6A', '6A']
            })
            st.dataframe(exemplo_boletim, hide_index=True)
        
        with col2:
            st.write("**Diagnóstico.csv:**")
            exemplo_diag = pd.DataFrame({
                'ALUNO': ['João Silva', 'Maria Santos'],
                'PROFICIENCIA': [285, 240],
                'NIVEL': ['Proficiente', 'Básico']
            })
            st.dataframe(exemplo_diag, hide_index=True)
