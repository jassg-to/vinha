# e-Vinha

Aplicação web de gestão de operações de centro espírita, desenvolvida para o [Grupo de Estudo Espírita Joanna de Angelis](https://jassg.ca).

## Pré-requisitos

- [Node.js](https://nodejs.org/) 22+
- [Python](https://python.org/) 3.14+
- [uv](https://docs.astral.sh/uv/) (gerenciador de pacotes Python)
- Um projeto [Firebase](https://firebase.google.com/) com Firestore habilitado (modo Native)

## Configuração

1. Clone o repositório e copie o arquivo de ambiente:

   ```bash
   cp .env.example .env
   ```

2. Preencha um segredo JWT aleatório e a URL do frontend no `.env`.

3. Baixe uma chave de service account do Firebase no console (Configurações do Projeto > Contas de Serviço > Gerar Nova Chave Privada) e salve como `backend/service-account.json`. Este arquivo está no gitignore.

4. Instale as dependências:

   ```bash
   cd backend && uv sync
   cd frontend && npm install
   ```

5. Rode ambos os servidores de desenvolvimento (para com Ctrl+C):

   ```powershell
   .\dev.ps1
   ```

   Ou rode individualmente em terminais separados:

   ```bash
   # Backend (porta 8080)
   cd backend && uv run uvicorn evinha.main:app --port 8080 --reload

   # Frontend (porta 5173)
   cd frontend && npm run dev
   ```

6. Abra http://localhost:5173 no navegador. A primeira pessoa a fazer login se torna admin automaticamente.

## Permissões

Pessoas são armazenadas no Firestore. Cada pessoa tem uma flag de admin e roles por seção. As quatro seções são: **Biblioteca**, **Livraria**, **Campanhas** e **Reservas**. Cada seção suporta três níveis de role: **Leitura** (somente consulta), **Edição** (criar/modificar/excluir) e **Gestão** (controle total). Admins ignoram todas as verificações de seção.

Admins podem gerenciar pessoas e atribuir permissões em `/admin`.

## Internacionalização

A interface suporta português (pt-BR) e inglês (en-CA). O idioma é detectado automaticamente a partir das configurações do navegador (padrão: pt-BR) e pode ser alterado manualmente pelo seletor de idioma. Os arquivos de tradução ficam em `frontend/src/lib/i18n/`.

## Licença

[Affero General Public License 3.0](LICENSE)
