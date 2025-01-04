import re
import uuid
import os
import fitz
import logging
from io import StringIO
from models.analysis import Analysis
import spacy
from spacy.lang.pt.stop_words import STOP_WORDS
from unidecode import unidecode
from nltk.tokenize import word_tokenize

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Carregar o modelo do spaCy para português
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
   logging.warning("Modelo do spaCy não encontrado, baixando...")
   spacy.cli.download("pt_core_news_sm")
   nlp = spacy.load("pt_core_news_sm")

def get_pdf_paths(folder_path):
    """Lista todos os arquivos PDF em um dado diretório."""
    pdf_paths = []
    try:
        if not os.path.exists(folder_path):
            logging.warning(f"Diretório não encontrado: {folder_path}")
            return pdf_paths
        for file_name in os.listdir(folder_path):
          if file_name.lower().endswith(".pdf"):
             pdf_paths.append(os.path.join(folder_path, file_name))
    except Exception as e:
         logging.error(f"Erro ao listar arquivos PDF em {folder_path}: {e}", exc_info=True)
    return pdf_paths

def read_uploaded_file(file_path):
  """Lê e extrai o texto de um arquivo PDF."""
  text = ""
  try:
     with fitz.open(file_path) as pdf:
         for page in pdf:
             text += page.get_text()
  except Exception as e:
      logging.error(f"Erro ao ler o arquivo PDF {file_path}: {e}", exc_info=True)
      return ""
  return text

def format_cv(text):
    """Remove stop words, pontuações, etc, e coloca o texto em caixa baixa."""
    try:
        if not text:
            logging.warning("O texto do currículo está vazio.")
            return ""
        doc = nlp(text)
        tokens = [
            token.lemma_.lower()
            for token in doc
            if token.is_alpha and not token.is_stop
        ]
        formatted_text = " ".join(tokens)
        formatted_text = unidecode(formatted_text) # remove acentos
        return formatted_text
    except Exception as e:
        logging.error(f"Erro ao formatar texto do currículo: {e}", exc_info=True)
        return ""

def extract_data_analysis(resum_cv, original_cv, job_id, resum_id, score) -> Analysis:
    secoes_dict = {
        "id": str(uuid.uuid4()),
        "job_id": job_id,
        "resum_id": resum_id,
        "name": "",
        "skills": [],
        "education": [],
        "languages": [],
        "score": score,
    }

    name_patterns = [
        r"(?:##\s*Nome Completo\s*|Nome Completo\s*\|\s*Valor\s*\|\s*\S*\s*\|\s*|##\s*Nome\s*|Nome\s*|:\s*)([A-ZÀ-Úa-zà-ú\s\.\'\-]+)(?:$|\n)",
        r"nome\s*completo\s*[:\s-]*([\w\s\.\'\-]+)",
        r"nome\s*[:\s-]*([\w\s\.\'\-]+)",
         r"([A-ZÀ-Úa-zà-ú\s\.\'\-]+)(?:$|\n)"
    ]

    def clean_string(string: str) -> str:
        return re.sub(r"[\*\-]+", "", string).strip()
    
    found_name = False
    for pattern in name_patterns:
        match = re.search(pattern, resum_cv)
        if match:
            name = clean_string(match.group(1)).strip()
            if name and not name.isdigit() and name:
                secoes_dict["name"] = name
                found_name = True
                break
        
    if not found_name:
        for pattern in name_patterns:
            match = re.search(pattern, original_cv)
            if match:
                name = clean_string(match.group(1)).strip()
                if name and not name.isdigit() and name:
                  secoes_dict["name"] = name
                  found_name = True
                  break
    
    if not found_name:
      secoes_dict["name"] = "Nome não encontrado"

    patterns = {
        "skills": r"## Habilidades\s*([\s\S]*?)(?=##|$)",
        "education": r"## Educação\s*([\s\S]*?)(?=##|$)",
        "languages": r"## Idiomas\s*([\s\S]*?)(?=##|$)",
        "salary_expectation": r"## Pretensão Salarial\s*([\s\S]*?)(?=##|$)",
    }
    
    for secao, pattern in patterns.items():
        match = re.search(pattern, resum_cv)
        if match:
            secoes_dict[secao] = [
                clean_string(item) for item in match.group(1).split("\n") if item.strip()
            ]
        else:
             if secao in ["skills", "education", "languages"]:
                secoes_dict[secao] = []

    # Validação para garantir que nenhuma seção obrigatória esteja vazia
    for key in ["name", "education", "skills"]:
        if not secoes_dict[key] or (
            isinstance(secoes_dict[key], list) and not any(secoes_dict[key])
        ):
            if key == "name":
                secoes_dict[key] = "Nome não encontrado"
            else:
                secoes_dict[key] = []

    return Analysis(**secoes_dict)