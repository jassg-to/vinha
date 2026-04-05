# e-Vinha — Operações de Centro Espírita

## Estrutura do Projeto

Monorepo com frontend SvelteKit e backend FastAPI.

```
frontend/   — SPA SvelteKit (Svelte 5, Tailwind v4, adapter-static)
backend/    — API async FastAPI (Python, gerenciado com uv)
```

## Servidores de Desenvolvimento

Ambos de uma vez (para com Ctrl+C):

```powershell
.\dev.ps1
```

Ou individualmente:

```bash
# Backend (porta 8080)
cd backend && uv run -m uvicorn evinha.main:app --port 8080 --reload

# Frontend (porta 5173)
cd frontend && npm run dev
```

## Convenções Principais

- **Somente Svelte 5 runes**: Usar `$state`, `$derived`, `$effect`. Nunca usar a sintaxe reativa antiga `$:`.
- **Tailwind CSS v4**: Configuração nativa em CSS via `@import "tailwindcss"` e `@theme` no `app.css`. Sem `tailwind.config.js`.
- **Dependências do backend**: Gerenciadas pelo `uv` via `pyproject.toml`. Nunca usar pip ou requirements.txt diretamente.
- **Todos os endpoints do backend são async.**
- **Auth**: Firebase Auth SDK no frontend (login com Google), verificado no backend com `firebase_admin.auth.verify_id_token()`. Sessão gerenciada via JWT customizado em cookies httpOnly. Nunca usar localStorage para tokens de auth. Login usa `signInWithRedirect` em produção e `signInWithPopup` em localhost (redirect não funciona em localhost por causa do particionamento de storage de terceiros do navegador).
- **Banco de dados**: Firestore via Firebase Admin SDK (somente backend). Todo acesso ao Firestore passa pela API FastAPI — nunca diretamente pelo frontend. A chave da service account fica em `backend/service-account.json` (no gitignore).
- **Permissões**: Flag de admin + roles por seção. Seções: `library`, `book_store`, `fundraisers`, `bookings`. Roles por seção: `viewer`, `editor`, `manager` (em ordem de privilégio). Usar `require_admin` ou `require_section(section, min_role)` de `evinha.auth.dependencies` para proteger endpoints. Admins ignoram todas as verificações de seção.
- **Dados de pessoas**: Armazenados na coleção `users` do Firestore, indexados por email. Upsert em cada login. Permissões são embutidas no JWT e entram em vigor no próximo login após um admin alterá-las.
- **i18n**: Usa `svelte-i18n`. Traduções ficam em `frontend/src/lib/i18n/{locale}.json`. Envolver todas as strings visíveis com `$_('key')`. O locale do navegador é detectado automaticamente; pt-BR é o padrão.
    - Para português, não usar estruturas com gênero definido, reformular para tirar o gênero da frase, ex: "Boas vindas" em vez de "Bem vindo(a)" ou "Escrito por" em vez de "Autor(a)".
- **Licença**: AGPL-3.0. A página de login inclui um link para o código-fonte para conformidade.

## Automação de Navegador

Um servidor MCP do Firefox DevTools está configurado para este projeto (`firefox-devtools`). Permite interagir com um navegador Firefox — navegar páginas, clicar elementos, tirar screenshots, inspecionar o console, ler requisições de rede e executar JavaScript.

- Adicionar com: `claude mcp add firefox-devtools npx @padenot/firefox-devtools-mcp`
- Servidor de dev do frontend roda em `http://localhost:5173`
- Usar `take_snapshot` para obter UIDs de elementos antes de clicar/preencher
