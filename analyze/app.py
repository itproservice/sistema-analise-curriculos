import os
import json
import time
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from database import AnalyzeDatabase
from drive.download_cv import download_files
from analise import main as analise_main

# Inicializa a base de dados
database = AnalyzeDatabase()

# Configura a página do Streamlit com layout largo e título "Recrutador"
st.set_page_config(layout="wide", page_title="Recrutador", page_icon=":brain:")

# Carregar configurações sensíveis de variáveis de ambiente ou arquivos locais
def load_config():
    """Carrega configurações sensíveis de variáveis de ambiente ou arquivos."""
    config = {}

    # Carregar DB_JSON
    if "DB_JSON" in st.secrets:
        config["db"] = {
            "jobs": json.loads(st.secrets["DB_JSON"]["jobs"]),
            "resums": json.loads(st.secrets["DB_JSON"]["resums"]),
            "analysis": json.loads(st.secrets["DB_JSON"]["analysis"]),
            "files": json.loads(st.secrets["DB_JSON"]["files"]),
        }
    else:
        st.error("DB_JSON não configurado nos Secrets.")

    # Carregar TOKEN_JSON
    if "TOKEN_JSON" in st.secrets:
        config["token"] = st.secrets["TOKEN_JSON"]
    else:
        st.error("TOKEN_JSON não configurado nos Secrets.")

    # Carregar ENV_VARS
    config["openai_api_key"] = st.secrets.get("ENV_VARS", {}).get("OPENAI_API_KEY", None)
    if not config["openai_api_key"]:
        st.warning("OPENAI_API_KEY não configurado nos Secrets.")

    return config

# Configurações do projeto
CONFIG = load_config()


def load_data(option):
    """Carrega os dados da base de dados e retorna o DataFrame."""
    if option:
        job = database.get_job_by_name(option)
        data = database.get_analysis_by_job_id(job.get("id"))
        df = pd.DataFrame(
            data if data else {},
            columns=["name", "education", "skills", "languages", "score", "resum_id", "id"],
        )
        df.rename(
            columns={
                "name": "Nome",
                "education": "Educação",
                "skills": "Habilidades",
                "languages": "Idiomas",
                "score": "Score",
                "resum_id": "Resum ID",
                "id": "ID",
            },
            inplace=True,
        )
        return df
    return pd.DataFrame()


def display_table(df):
    """Exibe a tabela interativa com AgGrid."""
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    if not df.empty:
        gb.configure_column("Score", header_name="Score", sort="desc")
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    grid_options = gb.build()
    response = AgGrid(
        df,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme="streamlit",
    )
    selected_rows = response.get("selected_rows", [])
    return pd.DataFrame(selected_rows)


def display_chart(df):
    """Exibe o gráfico de barras com os scores dos candidatos."""
    if not df.empty:
        st.subheader("Classificação dos Candidatos")
        st.bar_chart(df, x="Nome", y="Score", color="Nome", horizontal=True)


def delete_files_resum(resums):
    """Deleta os arquivos PDF dos currículos."""
    for resum in resums:
        path = resum.get("file")
        if os.path.isfile(path):
            os.remove(path)


def run_download(progress_bar, status_text):
    """Executa o download dos arquivos e atualiza o progresso."""
    try:
        for progress in range(0, 101, 20):
            progress_bar.progress(progress)
            status_text.text(f"Progresso do download: {progress}%")
            time.sleep(0.5)

        downloaded_files = download_files(CONFIG["token"], "credentials.json", "folder_id", "curriculos")
        progress_bar.progress(100)
        status_text.text("Progresso do download: 100% - Concluído")

        if downloaded_files:
            st.success(f"Arquivos atualizados com sucesso: {len(downloaded_files)} arquivos baixados!")
        else:
            st.warning("Nenhum arquivo foi atualizado.")
    except Exception as e:
        st.error(f"Erro ao atualizar arquivos: {str(e)}")


def run_analysis(progress_bar, status_text):
    """Executa a análise dos currículos e atualiza o progresso."""
    try:
        for progress in range(0, 101, 20):
            progress_bar.progress(progress)
            status_text.text(f"Progresso da análise: {progress}%")
            time.sleep(0.5)

        results = analise_main()
        progress_bar.progress(100)
        status_text.text("Progresso da análise: 100% - Concluído")

        if any(result and result.get("status") == "success" for result in results):
            st.success("Análise concluída com sucesso! Escolha a vaga no menu suspenso ao lado.")
        else:
            st.warning("Nenhuma análise foi realizada ou houve falhas.")
    except Exception as e:
        st.error(f"Erro ao realizar análise: {str(e)}")


def create_sidebar_actions():
    """Cria as ações da barra lateral com progresso exibido."""
    with st.sidebar:
        st.header("Ações")

        if st.button("Atualizar Arquivos", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            run_download(progress_bar, status_text)

        if st.button("Nova Análise", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            run_analysis(progress_bar, status_text)

        if option and st.button("Limpar Análise", use_container_width=True):
            database.clear_all_data()
            st.warning("Análises e arquivos foram limpos!")


# Interface principal
st.title("Sistema de Análise de Currículos")

option = st.selectbox(
    "Escolha a vaga:",
    [job.get("name") for job in database.jobs.all()],
    index=None,
)

create_sidebar_actions()

if option:
    with st.container():
        display_chart(df := load_data(option))
        st.subheader("Lista de Candidatos")
        selected_candidates = display_table(df)
else:
    st.info("Selecione uma vaga para visualizar os candidatos.")
