# Utiliza a imagem oficial do Python como base
FROM python:3.10-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia o arquivo de requirements para o container
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos do projeto para o container
COPY . .

# Define a variável de ambiente para o Flask
ENV FLASK_APP=app.py

# Expõe a porta 9001 para acessar a aplicação
EXPOSE 9001

# Comando para rodar o Flask no container
CMD ["flask", "run", "--host=0.0.0.0", "--port=9001"]
