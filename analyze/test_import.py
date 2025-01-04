import sys
import os
print("Caminho do projeto:", os.path.dirname(os.path.abspath(__file__)))
print("Caminhos de importação:", sys.path)
try:
   from drive.authenticate import authenticate_drive
   print("Importação realizada com sucesso!")
except ModuleNotFoundError as e:
   print("Erro na importação:", e)