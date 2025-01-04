import os
import uuid
import time
import re
import logging
from helper import read_uploaded_file, format_cv
from database import AnalyzeDatabase
from ai import OpenAIClient
from models.resum import Resum
from models.file import File
from openai import RateLimitError
from models.analysis import Analysis
from helper import extract_data_analysis, get_pdf_paths

# Configuração do logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Instanciar a base de dados
database = AnalyzeDatabase()

# Instanciar o cliente AI
ai = OpenAIClient()

# Obter job pelo nome
job = database.get_job_by_name("Vaga de Assessor Legislativo")
if not job:
    logging.error("Job 'Vaga de Assessor Legislativo' não encontrado.")
    exit()

# Configurações
batch_size = 5  # Processar 5 currículos por vez
max_attempts = 5  # Máximo de tentativas por arquivo
base_wait_time = 5  # tempo de espera minimo

def extract_wait_time(error_message):
    """Extrai o tempo de espera da mensagem de erro da API."""
    match = re.search(r"Please try again in ([\d.]+)(s|m)", error_message)
    if match:
        wait_time = float(match.group(1))
        unit = match.group(2)
        if unit == "m":
            wait_time *= 60
        return wait_time
    return base_wait_time  # tempo de espera padrão se não encontrar tempo na mensagem


def process_cv(path, job):
    """Processa um único currículo."""
    for attempt in range(max_attempts):
        try:
            # Verificar se o arquivo já foi processado
            existing_resum = database.get_resum_by_file(path)
            if existing_resum:
                logging.info(f"Currículo {path} já foi processado. Pulando.")
                return None  # Indica que o currículo foi pulado

            content = read_uploaded_file(path)

            # Formatar o currículo
            formatted_content = format_cv(content)

            resum = ai.resume_cv(formatted_content)
            if resum is None:
                logging.error(f"Erro ao gerar resumo para {path}. Pulando arquivo")
                return None

            opnion = ai.generate_opnion(formatted_content, job)
            if opnion is None:
                logging.error(f"Erro ao gerar opiniao para {path}. Pulando arquivo")
                return None

            score = ai.generate_score(formatted_content, job)
            if score is None:
                logging.error(f"Erro ao gerar score para {path}. Pulando arquivo")
                return None

            resum_schema = Resum(
                id=str(uuid.uuid4()),
                job_id=job.get("id"),
                content=resum,
                file=str(path),
                opnion=opnion,
            )

            file_schema = File(
                file_id=str(uuid.uuid4()),
                job_id=job.get("id"),
            )

            analysis_schema = extract_data_analysis(
                resum, content, job.get("id"), resum_schema.id, score
            )

            # Inserir no banco de dados
            database.resums.insert(resum_schema.model_dump())
            database.analysis.insert(analysis_schema.model_dump())
            database.files.insert(file_schema.model_dump())

            logging.info(f"Currículo {path} processado com sucesso.")
            return {
                "status": "success",
                "path": path,
                "resum": resum,
                "opnion": opnion,
                "score": score,
            }  # Indica que o processamento foi bem-sucedido
        except RateLimitError as e:
            wait_time = extract_wait_time(str(e))
            logging.warning(
                f"Rate limit atingido ao processar {path}. Tentativa {attempt + 1}/{max_attempts}. Aguardando {wait_time:.2f} segundos..."
            )
            time.sleep(wait_time)
        except Exception as e:
            logging.error(f"Erro inesperado ao processar {path} (tentativa {attempt + 1}/{max_attempts}): {e}")
            break  # se ocorrer algum outro erro, sair do loop
    else:
        logging.error(f"Falha ao processar {path} após {max_attempts} tentativas.")
        return {
            "status": "failed",
            "path": path,
            "error": f"Falha ao processar após {max_attempts} tentativas.",
        }

# Processar currículos em lotes
def main(batch_size=batch_size):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cv_paths = get_pdf_paths(os.path.join(current_dir, "drive", "curriculos"))
    if not cv_paths:
      logging.warning("Nenhum currículo encontrado no diretório 'drive/curriculos'.")
      return [] # retornar lista vazia
    results = []
    for i in range(0, len(cv_paths), batch_size):
        batch = cv_paths[i:i + batch_size]
        batch_results = []
        for path in batch:
            batch_results.append(process_cv(path, job))
            time.sleep(1) # espera 1 segundo entre os processamentos
        results.extend(batch_results)
    logging.info("Processamento de currículos concluído.")
    return results

if __name__ == "__main__":
    results = main()

    # Você pode adicionar mais lógica aqui para tratar os resultados, se necessário.
    # Exemplo:
    for result in results:
         if result and result.get("status") == "success":
            logging.info(f"Currículo {result.get('path')} processado com sucesso.")
         elif result and result.get("status") == "failed":
             logging.error(f"Erro ao processar o currículo {result.get('path')}: {result.get('error')}")
         else:
             logging.info(f"Currículo pulado: {result.get('path')}")