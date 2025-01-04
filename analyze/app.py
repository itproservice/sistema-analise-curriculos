import os
import time  # Adicionado para suportar delays
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

# Define os caminhos para autenticação e download
TOKEN_PATH = "token.json"
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")
FOLDER_ID = "1Kg_krUauUwMEHVeR9vWEj1-4eqHT-qEc"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, "drive", "curriculos")


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


def load_resume_details(resum_id):
    """Carrega os detalhes do resumo do currículo."""
    return database.get_resum_by_id(resum_id)


def display_resume_details(selected_candidates):
    """Exibe os detalhes complementares dos currículos selecionados."""
    if not selected_candidates.empty:
        for _, candidate in selected_candidates.iterrows():
            st.markdown(f"## Detalhes do Currículo - {candidate.get('Nome')}")

            resum_id = candidate.get("Resum ID")
            if resum_id:
                resum_data = load_resume_details(resum_id)
                if resum_data:
                    st.markdown("### Análise Detalhada")
                    st.markdown(resum_data.get("content", "Não disponível"))
                    st.markdown("### Avaliação")
                    st.markdown(resum_data.get("opnion", "Não disponível"))

                    with open(resum_data.get("file"), "rb") as pdf_file:
                        pdf_data = pdf_file.read()
                        st.download_button(
                            label=f"Download Currículo {candidate.get('Nome')}",
                            data=pdf_data,
                            file_name=f"{candidate.get('Nome')}.pdf",
                            mime="application/pdf",
                        )
                else:
                    st.warning(f"Resumo não encontrado para o ID {resum_id}.")
            st.divider()  # Adiciona uma linha divisória entre candidatos


def delete_files_resum(resums):
    """Deleta os arquivos PDF dos currículos."""
    for resum in resums:
        path = resum.get("file")
        if os.path.isfile(path):
            os.remove(path)


def run_download(progress_bar, status_text):
    """Executa o download dos arquivos e atualiza o progresso na thread principal."""
    downloaded_files = []
    try:
        for progress in range(0, 101, 20):
            progress_bar.progress(progress)
            #status_text.text(f"Downlaod dos PDFs: {progress}%")
            time.sleep(0.50)

        downloaded_files = download_files(TOKEN_PATH, CREDENTIALS_PATH, FOLDER_ID, DOWNLOAD_DIR)

        progress_bar.progress(100)
        status_text.text("Progresso downlaod dos PDFs: 100% - Concluído")

        if downloaded_files:
            st.success(f"Arquivos atualizados com sucesso: {len(downloaded_files)} arquivos baixados!")
        else:
            st.warning("Nenhum arquivo foi atualizado.")
    except Exception as e:
        st.error(f"Erro ao atualizar arquivos: {str(e)}")


def run_analysis(progress_bar, status_text):
    """Executa a análise dos currículos e atualiza o progresso na thread principal."""
    try:
        for progress in range(0, 101, 20):
            progress_bar.progress(progress)
            #status_text.text(f"Iniciar analise: {progress}%")
            time.sleep(0.1)

        results = analise_main()

        progress_bar.progress(100)
        status_text.text("Progresso: 100% - Concluído")

        if any(result and result.get("status") == "success" for result in results):
            st.success("Análise concluída com sucesso! Por favor, escolha a vaga no menu suspenso ao lado")
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
            job = database.get_job_by_name(option)
            resums = database.get_resums_by_job_id(job.get("id"))
            database.delete_all_resums_by_job_id(job.get("id"))
            database.delete_all_analysis_by_job_id(job.get("id"))
            delete_files_resum(resums)
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

        if not selected_candidates.empty:
            st.subheader("Detalhes dos Candidatos Selecionados")
            display_resume_details(selected_candidates)
else:
    st.info("Selecione uma vaga para visualizar os candidatos.")
