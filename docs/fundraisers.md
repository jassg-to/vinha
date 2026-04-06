# Campanhas

Campanhas são eventos recorrentes de alimentação (ex: feijoada mensal) onde pessoas fazem pedidos para consumo no local ou para levar. O sistema gerencia o ciclo completo: configuração do evento e cardápio, recebimento de pedidos, registro de pagamentos e operações no dia do evento (check-in, cozinha, caixa).

## Permissões

O acesso às campanhas é controlado por roles de seção. Admins ignoram todas as verificações.

| Role | Pode fazer |
|------|------------|
| **Leitura** | Ver eventos, pedidos e resumos (somente consulta) |
| **Edição** | Tudo que Leitura pode, mais: criar/editar pedidos, registrar pagamentos, fazer check-in, editar o cardápio |
| **Gestão** | Tudo que Edição pode, mais: criar eventos, editar detalhes do evento, alterar status do evento |

## Ciclo de vida do evento

Cada evento passa por quatro status:

```
Rascunho → Aberta → Dia do Evento → Encerrada
```

Gestores podem avançar ou reverter o status a qualquer momento pelo painel do evento.

- **Rascunho** — Configuração do evento. Definir nome, data, descrição e itens do cardápio. Pedidos já podem ser criados nesta fase.
- **Aberta** — Reservas abertas. Esta é a fase principal onde os pedidos chegam. As visualizações de Cozinha e Caixa ficam disponíveis.
- **Dia do Evento** — O evento está acontecendo. A equipe usa a Cozinha para ver o que preparar e o Caixa para receber pagamentos e fazer check-in.
- **Encerrada** — Evento finalizado. O painel mostra o resumo financeiro final.

## Configurando um evento

1. Acesse **Campanhas** no painel.
2. Clique em **Nova Campanha**, insira nome e data, depois clique em **Criar Campanha**.
3. Você será direcionado à página de **Editar Campanha**. Preencha:
   - **Detalhes do evento** — Nome, data e descrição opcional.
   - **Itens do cardápio** — Cada item tem um nome, uma categoria (Refeição, Bebida, Sobremesa, Outro) e uma ou mais **variantes**. Variantes permitem oferecer o mesmo item em formatos diferentes com preços diferentes. Por exemplo, "Feijoada Tradicional" pode ter uma variante "Regular" a $25 e uma variante "Pote" a $18. Itens sem variante significativa usam uma única variante "padrão".
4. Clique em **Salvar Cardápio** para salvar.

Editores podem atualizar o cardápio a qualquer momento (útil para adições no dia, como sobremesas doadas).

## Fazendo pedidos

1. No painel do evento, clique em **Novo Pedido**.
2. **Cliente** — Comece a digitar um nome. Se a pessoa já fez pedidos antes, aparecerá no dropdown (selecione para preencher nome e telefone automaticamente). Caso contrário, digite nome e telefone manualmente; um novo registro de pessoa é criado automaticamente.
3. **Tipo** — Escolha No local ou Para levar.
4. **Status** — Escolha Confirmado (padrão) ou Em consulta. Use Em consulta quando a conversa ainda está em andamento mas você quer anotar os detalhes até o momento.
5. **Itens** — Use os botões +/- para definir quantidades de cada variante do cardápio. O total atualiza em tempo real.
6. **Observações** — Texto livre opcional (ex: "bem apimentado", "alergia a amendoim").
7. Clique em **Salvar Pedido**.

### Status dos pedidos

| Status | Significado |
|--------|-------------|
| **Em consulta** | Conversa em andamento, detalhes podem estar incompletos. Não contabilizado nos totais da cozinha. |
| **Confirmado** | Pedido confirmado. Contabilizado nos totais da cozinha. |
| **Presente** | Cliente chegou ao evento. |
| **Não compareceu** | Cliente não apareceu. |
| **Cancelado** | Pedido foi cancelado. |

O status pode ser alterado na página de detalhe do pedido usando os botões de ação (Confirmar, Registrar presença, Não compareceu, Cancelar).

## Pagamentos

Pagamentos são registrados na **página de detalhe do pedido**. A seção de pagamento mostra:

- O total pago até o momento e o saldo pendente.
- Uma lista de pagamentos registrados com forma, valor, quem registrou e um link para Remover.
- Um formulário para adicionar novo pagamento: insira o valor (pré-preenchido com o saldo restante) e selecione a forma (Dinheiro, Square, E-transfer ou Doação).

Pagamentos parciais são suportados — registre quantos pagamentos forem necessários até o saldo zerar.

## Visualizações do dia do evento

Otimizadas para celulares e tablets usados pela equipe durante o evento. Ambas atualizam automaticamente a cada 30 segundos.

### Cozinha

Mostra cards grandes para cada variante do cardápio com contagens divididas por **No local**, **Para levar** e **Total**. Só conta pedidos com status Confirmado ou Presente (exclui Em consulta, Cancelado e Não compareceu).

Acesso: qualquer pessoa com pelo menos acesso de Leitura.

### Caixa

Mostra todos os pedidos ativos (exclui cancelados, não compareceu e em consulta) em layout de cards. Cada card mostra:

- Nome, badge de status, tipo do pedido
- Resumo dos itens
- Total, valor pago e saldo pendente
- Botão de **Registrar presença** (se ainda não registrado)
- **Botões de pagamento rápido** — botões de um toque para Dinheiro, Square e E-transfer que pagam o saldo total restante em um clique. Para pagamentos parciais ou outros métodos, toque na seta (→) para ir à página completa do pedido.

Acesso: Edição e acima.

## Painel do evento

O painel do evento (`/fundraisers/{eventId}`) é o hub principal. Mostra:

- **Cards de resumo** — Total de pedidos, total de refeições, receita, valor recebido e saldo pendente.
- **Filtros** — Filtrar a lista de pedidos por status, tipo (no local/para levar) e situação de pagamento (pago/pendente).
- **Tabela de pedidos** — Mostra nome, telefone, tipo, itens, total, valor pago e status. Clique em qualquer linha para abrir o detalhe do pedido. No celular, pedidos são exibidos como cards em vez de tabela.
- **Botões de ação** — Avançar/reverter status (gestores), Novo Pedido, Cozinha, Caixa, Editar Campanha e Voltar às campanhas.

## Pessoas

O sistema mantém um diretório simples de pessoas (clientes) com nome e telefone. Pessoas são criadas automaticamente quando um novo pedido é feito com um nome desconhecido. Ao criar pedidos seguintes, digitar no campo de cliente busca pessoas existentes para seleção rápida.

Pessoas são compartilhadas entre todos os eventos — alguém que fez pedido em janeiro aparecerá na busca ao criar um pedido em março.
