import os
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from .authenticate import authenticate_drive  # Importando a função de autenticação

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para baixar arquivos
def download_files(token_path, credentials_path, folder_id, download_path):
    try:
        logging.info(f"Iniciando o download de arquivos da pasta ID: {folder_id}")

        # Autenticar e construir o serviço
        creds = authenticate_drive(token_path=token_path, credentials_path=credentials_path)
        service = build('drive', 'v3', credentials=creds)

        # Listar arquivos
        results = service.files().list(
            q=f"'{folder_id}' in parents", fields="files(id, name)"
        ).execute()
        files = results.get('files', [])

        if not files:
            logging.warning("Nenhum arquivo encontrado na pasta especificada.")
            return []

        downloaded_files = []
        for file in files:
            file_id = file['id']
            file_name = file['name']
            logging.info(f"Baixando arquivo: {file_name} (ID: {file_id})")
            request = service.files().get_media(fileId=file_id)
            file_path = os.path.join(download_path, file_name) # caminho do arquivo corrigido
            os.makedirs(download_path, exist_ok=True)
            try:
              with open(file_path, 'wb') as f:
                  downloader = MediaIoBaseDownload(f, request)
                  done = False
                  while not done:
                      status, done = downloader.next_chunk()
                      logging.info(f"Download {int(status.progress() * 100)}% concluído.")
              downloaded_files.append(file_path)
            except Exception as e:
                 logging.error(f"Erro ao baixar arquivo {file_name} (ID: {file_id})", exc_info=True)
        logging.info(f"Download de arquivos concluído. Arquivos baixados em: {download_path}")
        return downloaded_files
    except Exception as e:
        logging.error("Erro ao executar a função download_files", exc_info=True)
        return []


if __name__ == "__main__":
    TOKEN_PATH = "token.json"
    CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "../credentials.json")
    FOLDER_ID = "1Kg_krUauUwMEHVeR9vWEj1-4eqHT-qEc"

    # Define o diretório "curriculos" dentro de "analyze"
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, "drive", "curriculos") # caminho do diretorio corrigido

    try:
      downloaded_files = download_files(TOKEN_PATH, CREDENTIALS_PATH, FOLDER_ID, DOWNLOAD_DIR)
      if downloaded_files:
        logging.info(f"Arquivos baixados com sucesso: {downloaded_files}")
      else:
        logging.warning("Nenhum arquivo foi baixado.")

    except Exception as e:
       logging.critical(f"Erro crítico ao baixar os arquivos {e}", exc_info=True)