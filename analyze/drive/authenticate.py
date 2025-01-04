import os
import logging
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def authenticate_drive(token_path, credentials_path):
    """Autentica o Google Drive API."""
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/drive']  # Define o escopo de acesso

    # Verificar se o arquivo de credenciais existe
    if not os.path.exists(credentials_path):
        logging.error(f"Arquivo de credenciais não encontrado ou inacessível: {credentials_path}")
        raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {credentials_path}")

    # Verificar se existe um token válido
    if os.path.exists(token_path):
        try:
            logging.info(f"Lendo o token de: {token_path}")
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)  # Usando o escopo definido
        except Exception as e:
            logging.warning(f"Erro ao ler o token: {e}, tentando a autenticação via credentials")
    # Caso o token seja inválido ou não exista
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.info("Token expirado, tentando atualizar...")
            try:
                creds.refresh(Request())
            except Exception as e:
               logging.error(f"Erro ao atualizar o token {e}")
               logging.info("Realizando autenticação via credenciais novamente")
               if not os.path.exists(credentials_path):
                    logging.error(f"Arquivo de credenciais não encontrado ou inacessível: {credentials_path}")
                    raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {credentials_path}")
               logging.info(f"Procurando arquivo de credenciais em: {credentials_path}")
               try:
                  flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                  creds = flow.run_local_server(port=0)
                  logging.info("Autenticação via credenciais realizada com sucesso!")
               except Exception as e:
                  logging.error(f"Erro ao realizar autenticação via credenciais: {e}")
                  raise e
        else:
             # Autenticar com credenciais
            logging.info(f"Procurando arquivo de credenciais em: {credentials_path}")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES) # Usando o escopo definido
                creds = flow.run_local_server(port=0)
                logging.info("Autenticação via credenciais realizada com sucesso!")
            except Exception as e:
                logging.error(f"Erro ao realizar autenticação via credenciais: {e}")
                raise e
        # Salvar o token para futuras utilizações
        try:
           with open(token_path, 'w') as token:
                logging.info(f"Salvando o token em: {token_path}")
                token.write(creds.to_json())
        except Exception as e:
            logging.error(f"Erro ao salvar o token: {e}")
            raise e

    return creds