import streamlit as st
from dados import df

st.set_page_config(layout="wide", page_title="COVID PIB BH", page_icon="📍")
st.title("Consequências da COVID-19 no PIB da região metropolitana de Belo Horizonte")


municipios = sorted(df["Nome do Município"].unique())
municipios.insert(0, "Todos")
municipio_selecionado = st.multiselect(
        "Selecione os municípios:",
        options=municipios,
        default="Todos")

if "Todos" in municipio_selecionado or not municipio_selecionado:
    df_filtrado = df
else:
    df_filtrado = df[df["Nome do Município"].isin(municipio_selecionado)]



st.dataframe(df_filtrado)
