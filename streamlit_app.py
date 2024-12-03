import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt


file_path = r'data/PIB_18.11.xlsx' 
df = pd.read_excel(file_path)

# Renomear colunas pra facilitar o uso
df.rename(columns={
    "Produto Interno Bruto per capita, \na preços correntes\n(R$ 1,00)": "PIB_per_capita",
    "Valor adicionado bruto da Agropecuária, \na preços correntes\n(R$ 1.000)": "Agropecuária",
    "Valor adicionado bruto da Indústria,\na preços correntes\n(R$ 1.000)": "Indústria",
    "Valor adicionado bruto dos Serviços,\na preços correntes \n- exceto Administração, defesa, educação e saúde públicas e seguridade social\n(R$ 1.000)": "Serviços",
    "Valor adicionado bruto da Administração, defesa, educação e saúde públicas e seguridade social, \na preços correntes\n(R$ 1.000)": "Administração",
    "Valor adicionado bruto total, \na preços correntes\n(R$ 1.000)": "PIB_total"
}, inplace=True)

st.set_page_config(layout="wide", page_title="Evolução do PIB per capita", page_icon="📊")
st.title("Impacto da Pandemia no PIB da Região Metropolitana de Belo Horizonte")
st.sidebar.header("Filtros")

# Filtro de municípios
municipios = sorted(df["Nome do Município"].unique())
municipios.insert(0, "Todos")  # Adicionar a opção "Todos"
municipios_selecionados = st.sidebar.multiselect(
    "Selecione os municípios:",
    options=municipios,
    default="Todos"
)

# Filtro de intervalo de anos
ano_min, ano_max = int(df["Ano"].min()), int(df["Ano"].max())
anos_selecionados = st.sidebar.slider(
    "Selecione o intervalo de anos:",
    min_value=ano_min,
    max_value=ano_max,
    value=(ano_min, ano_max)
)

# Filtro para selecionar os setores que devem aparecer no gráfico
setores_disponiveis = ["Agropecuária", "Indústria", "Serviços", "Administração"]
setores_selecionados = st.sidebar.multiselect(
    "Selecione os setores econômicos para o gráfico:",
    options=setores_disponiveis,
    default=setores_disponiveis  
)




if "Todos" in municipios_selecionados and len(municipios_selecionados) == 1:
    df_filtrado = df[
        (df["Ano"] >= anos_selecionados[0]) & 
        (df["Ano"] <= anos_selecionados[1])
    ]
    exibir_municipios = False
else:
    df_filtrado = df[
        (df["Nome do Município"].isin(municipios_selecionados)) & 
        (df["Ano"] >= anos_selecionados[0]) & 
        (df["Ano"] <= anos_selecionados[1])
    ]
    exibir_municipios = True

col1, col2, col3 = st.columns([1,1,1])
with col1:
    pib_per_capita_medio = df_filtrado["PIB_per_capita"].mean()

    st.metric(
        label="PIB per capita médio (todo o período)",
        value=f"R$ {pib_per_capita_medio:,.2f}",
    )






# Verificar se há dados após os filtros/ Grafico PIB
if df_filtrado.empty:
    st.warning("Nenhum dado disponível para os filtros selecionados.")
else:
    fig = go.Figure()

    if exibir_municipios:
        for municipio in df_filtrado["Nome do Município"].unique():
            municipio_data = df_filtrado[df_filtrado["Nome do Município"] == municipio]
            fig.add_trace(
                go.Scatter(
                    x=municipio_data["Ano"],
                    y=municipio_data["PIB_per_capita"],
                    mode="lines",
                    name=municipio
                )
            )

    media_df = df_filtrado.groupby("Ano")[["PIB_per_capita"]].mean().reset_index()
    fig.add_trace(
        go.Scatter(
            x=media_df["Ano"],
            y=media_df["PIB_per_capita"],
            mode="lines",
            line=dict(dash="dash", color="black"),
            name="Média"
        )
    )

    fig.update_layout(
        title="Evolução do PIB per capita (R$)",
        xaxis_title="Ano",
        yaxis_title="PIB per capita (R$)",
        legend_title="Legenda",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)




setores = ["Agropecuária", "Indústria", "Serviços", "Administração"]

for setor in setores:
    df[setor + "_pct"] = df[setor] / df["PIB_total"] * 100

if "Todos" in municipios_selecionados and len(municipios_selecionados) == 1:
    df_filtrado = df[
        (df["Ano"] >= anos_selecionados[0]) & 
        (df["Ano"] <= anos_selecionados[1])
    ]
    exibir_municipios = False
else:
    df_filtrado = df[
        (df["Nome do Município"].isin(municipios_selecionados)) & 
        (df["Ano"] >= anos_selecionados[0]) & 
        (df["Ano"] <= anos_selecionados[1])
    ]
    exibir_municipios = True



# Grafico de contribuição dos setores


fig = go.Figure()

if exibir_municipios:
    for setor in setores_selecionados:
        for municipio in df_filtrado["Nome do Município"].unique():
            municipio_data = df_filtrado[df_filtrado["Nome do Município"] == municipio]
            fig.add_trace(
                go.Scatter(
                    x=municipio_data["Ano"],
                    y=municipio_data[setor + "_pct"],
                    mode="lines",
                    name=f"{setor} - {municipio}"
                )
            )

media_df = df_filtrado.groupby("Ano")[[setor + "_pct" for setor in setores_selecionados]].mean().reset_index()

# Cores diferentes para cada setor
cores_medias = ["blue", "green", "red", "orange", "purple", "brown", "pink"]  # Adicione cores conforme necessário

for i, setor in enumerate(setores_selecionados):
    cor = cores_medias[i % len(cores_medias)]  # Para evitar erros, usa o índice modular no caso de muitos setores
    fig.add_trace(
        go.Scatter(
            x=media_df["Ano"],
            y=media_df[setor + "_pct"],
            mode="lines",
            line=dict(dash="dash", color=cor),
            name=f"Média - {setor}"
        )
    )

fig.update_layout(
    title="Contribuição dos Setores Econômicos ao PIB Total (%)",
    xaxis_title="Ano",
    yaxis_title="Contribuição ao PIB (%)",
    legend_title="Setores/Municípios",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)



# Gráfico de categorias importantes

colunas_interesse = [
    "Atividade com maior valor adicionado bruto",
    "Atividade com segundo maior valor adicionado bruto",
    "Atividade com terceiro maior valor adicionado bruto",
]



# Combinar todos os valores das colunas de interesse em uma única lista
valores_unicos = df_filtrado[colunas_interesse].stack().dropna().astype(str).tolist()

# Contar a frequência de cada valor único
frequencia_valores = pd.Series(valores_unicos).value_counts().reset_index()
frequencia_valores.columns = ['Categoria', 'Frequência']

# Criar o gráfico de barras
fig = px.bar(
    frequencia_valores,
    x="Frequência",
    y="Categoria",
    orientation='h',
    title="Recorrência da representatividade de setores da Econômia",
    labels={"Frequência": "Quantidade de Ocorrências", "Categoria": "Categoria"}
)

fig.update_layout(
    yaxis={'categoryorder': 'total ascending'},  # Ordenar de forma decrescente
    template="plotly_white"
)

# Exibir o gráfico no Streamlit
st.plotly_chart(fig, use_container_width=True)


st.write("")
# Filtro para selecionar colunas
colunas_disponiveis = df.columns.tolist()
colunas_selecionadas = st.multiselect(
    "Selecione as colunas que deseja visualizar:",
    options=colunas_disponiveis,
    default=[]
)
st.write("")
# Exibir a tabela com as colunas selecionadas
if colunas_selecionadas:
    df_exibido = df_filtrado[colunas_selecionadas]
    st.write("Tabela com colunas selecionadas:")
    st.dataframe(df_exibido)
else:
    st.warning("Selecione pelo menos uma coluna para visualizar a tabela.")