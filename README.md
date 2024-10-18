
# SIGWeb Dashboard

Este repositório contém o código para o **SIGWeb Dashboard**, uma plataforma voltada para o acompanhamento do processo de revisão de lotes no Subproduto 1 do projeto 'Enfrentando as violências contra as mulheres no Estado do Ceará: Proposições e tecnologias sociais em políticas públicas'. O dashboard permite visualizar rapidamente a distribuição das revisões realizadas e não realizadas, acompanhar a evolução diária por meio de gráficos, além de filtrar dados por município e conferir o desempenho individual de cada revisor, detalhando a área revisada e a porcentagem de revisão.

## Funcionalidades Principais

- **Visualização de Revisões**: Distribuição das revisões realizadas e não realizadas.
- **Acompanhamento da Evolução Diária**: Gráficos que mostram a evolução do número de lotes revisados ao longo do tempo.
- **Filtros por Município**: Filtragem de dados por município para acompanhar as revisões locais.
- **Desempenho Individual dos Revisores**: Detalhamento da área revisada e porcentagem de revisão para cada revisor.

## Tecnologias Utilizadas

- **Flask**: Framework para desenvolvimento web em Python, utilizado para criar a API e as rotas do dashboard.
- **PostgreSQL**: Sistema de banco de dados relacional utilizado para armazenar e gerenciar os dados de revisão de lotes.
- **Leaflet**: Biblioteca JavaScript para visualização de mapas interativos.
- **HTML/CSS/JavaScript**: Tecnologias usadas para criar a interface de usuário do dashboard.
- **Python**: Linguagem principal utilizada no backend.
- **Docker**: Plataforma que facilita a criação, o gerenciamento e a execução de aplicativos em contêineres. É utilizado para garantir que o ambiente de desenvolvimento e produção sejam consistentes, facilitando a implantação e a escalabilidade do sistema.

## Requisitos de Sistema

Para rodar o projeto localmente, certifique-se de ter os seguintes requisitos instalados:

- **Python 3.9+**
- **PostgreSQL**

## Como Configurar o Projeto Localmente

1. Clone este repositório:

   ```bash
   git clone https://github.com/hudjinn/sigweb_dashboard.git
   ```

2. Navegue até o diretório do projeto:

   ```bash
   cd sigweb_dashboard
   ```

3. Configure o banco de dados PostgreSQL e as variáveis de ambiente no arquivo `.env`. Exemplo de variáveis de ambiente:

   ```bash
    DB_HOST=""
    DB_PORT="5432"
    DB_NAME=""
    DB_USER=""
    DB_PASSWORD=""
   ```

4. Inicie os containeres

   ```bash
   docker compose up -d --build
   ```

   O dashboard estará acessível em `http://localhost:9001`.

## Estrutura do Projeto

```bash
sigweb_dashboard/
├── app/                # Contém a lógica do aplicativo Flask
│   ├── templates/      # Templates HTML
│   ├── static/         # Arquivos estáticos (CSS, JS, imagens)
├── .env                # Arquivo de configuração de variáveis de ambiente
├── README.md           # Este arquivo
├── requirements.txt    # Lista de dependências do projeto
└── app.py              # Ponto de entrada para executar o aplicativo
```
