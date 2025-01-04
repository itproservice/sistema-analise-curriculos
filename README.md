# cv-analyser
Aqui está um modelo para o arquivo **`README.md`** baseado no contexto do seu projeto:

---

# **Sistema de Análise de Currículos**

![Streamlit](https://img.shields.io/badge/Streamlit-Powered-blue)  
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)  
![License](https://img.shields.io/badge/license-MIT-green)

## **Descrição**
O **Sistema de Análise de Currículos** é uma aplicação interativa desenvolvida em **Streamlit** que permite:
- Carregar currículos armazenados no Google Drive.
- Analisar automaticamente os currículos para extrair informações-chave.
- Exibir uma classificação baseada em critérios como habilidades, educação e pontuação (score).
- Facilitar o gerenciamento e a visualização de detalhes completos dos candidatos.

Este projeto é ideal para equipes de recrutamento que precisam processar e analisar currículos rapidamente.

---

## **Funcionalidades**
- **Atualização de Arquivos**: Faz o download dos currículos armazenados no Google Drive.
- **Nova Análise**: Processa os currículos para gerar insights.
- **Classificação**: Exibe uma tabela interativa com os candidatos e suas pontuações.
- **Detalhes Complementares**: Visualização de informações detalhadas de cada currículo.
- **Download de Currículos**: Permite baixar os currículos processados diretamente no formato PDF.

---

## **Demonstração**

### **Acesse o App Online**
👉 [Sistema de Análise de Currículos - Link Aqui](https://share.streamlit.io/seu_usuario/seu_repositorio/main/app.py)

---

## **Como Rodar o Projeto Localmente**

### **Pré-requisitos**
- Python 3.8 ou superior instalado.
- Bibliotecas listadas no arquivo `requirements.txt`.

### **Instruções**
1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o aplicativo:
   ```bash
   streamlit run app.py
   ```

4. Acesse no navegador:
   ```
   http://localhost:8501
   ```

---

## **Configuração do Google Drive**

Para utilizar a funcionalidade de download de currículos, é necessário:
1. Criar credenciais no Google Cloud para ativar a API do Google Drive.
2. Adicionar os arquivos `token.json` e `credentials.json` no diretório do projeto.
3. Configurar o `FOLDER_ID` no código para apontar para a pasta correta.

---

## **Estrutura do Projeto**

```
.
├── app.py               # Arquivo principal do Streamlit
├── analise.py           # Lógica de análise dos currículos
├── drive/
│   ├── download_cv.py   # Download de arquivos do Google Drive
├── database/
│   ├── AnalyzeDatabase  # Gerenciamento do banco de dados
├── requirements.txt     # Dependências do projeto
├── README.md            # Documentação do projeto
└── token.json           # Credenciais para Google Drive (não incluso no repositório público)
```

---

## **Contribuindo**

Contribuições são bem-vindas!  
Siga os passos abaixo para colaborar:
1. Faça um fork do repositório.
2. Crie uma branch para sua feature:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça o commit das alterações:
   ```bash
   git commit -m "Descrição da minha feature"
   ```
4. Envie a branch para o GitHub:
   ```bash
   git push origin minha-feature
   ```
5. Abra um Pull Request.

---

## **Licença**
Este projeto está licenciado sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## **Contato**
📧 **Email:** seu-email@exemplo.com  
🔗 **LinkedIn:** [Seu Perfil](https://linkedin.com/in/seu-perfil)  
🌐 **Portfólio:** [Seu Portfólio](https://seu-portfolio.com)

---

Se precisar de ajustes ou personalizações neste modelo, é só avisar! 😊
