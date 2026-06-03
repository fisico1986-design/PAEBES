import streamlit as st
import pandas as pd

st.title("PAEBES Dashboard")

st.sidebar.write("Upload de Arquivos")
file1 = st.sidebar.file_uploader("Boletim", type="csv")
file2 = st.sidebar.file_uploader("Diagnostico", type="csv")

if file1 and file2:
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    st.write(df1)
    st.write(df2)
else:
    st.write("Aguardando arquivos")
