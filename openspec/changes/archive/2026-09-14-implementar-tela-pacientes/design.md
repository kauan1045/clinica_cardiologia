## Context

`Sidebar` e `Topbar` já existem como funções de componente dentro de `ProjetoCl_nicaCardiologia/dashboard.py`, com `Sidebar` destacando "Início" de forma fixa. Não há camada de backend/banco de dados; o Dashboard usa dados mockados em estruturas Python simples. Ver `proposal.md` para a motivação.

## Goals / Non-Goals

**Goals:**

- Reutilizar `Sidebar`/`Topbar` sem duplicar código, permitindo que cada tela informe qual item do menu está ativo.
- Implementar busca e paginação client-side sobre uma lista mockada, com estrutura pronta para trocar por uma API depois.
- Seguir exatamente a paleta e tipografia do design system CardioVida já usadas no Dashboard.

**Non-Goals:**

- Cadastro/edição de paciente, integração real com back-end/banco de dados e perfil detalhado do paciente (fora de escopo, conforme a proposta).
- Alterar o comportamento do Dashboard além de tornar o item ativo da Sidebar configurável.

## Decisions

### Generalizar `Sidebar` em vez de duplicá-la

`Sidebar` passa a aceitar um parâmetro `active: str` (default `"Início"`, preservando o comportamento atual do Dashboard sem alterações no call site). A tela Pacientes importa `Sidebar`/`Topbar` de `dashboard.py` e chama `Sidebar(active="Pacientes")`.

Alternativa considerada: copiar `Sidebar` para um componente específico da tela Pacientes. Rejeitada por violar o critério de aceite "reutiliza Sidebar e Topbar sem duplicar código" e por criar duas fontes de verdade para o menu.

### Estado de busca/paginação em `PatientsState`

Um único `rx.State` (`PatientsState`) mantém `search` e `page`; `filtered_patients`, `total_pages`, `page_numbers` e `paginated_patients` são computed vars (`@rx.var`) derivadas da lista mockada `MOCK_PATIENTS`. Buscar reseta `page` para 1.

Alternativa considerada: filtrar/paginar no cliente via JavaScript puro. Rejeitada porque foge do modelo de estado do Reflex já usado no projeto (ex.: `State` do login) e complicaria a futura troca por uma chamada real ao back-end.

### Dados mockados isolados e substituíveis

`MOCK_PATIENTS` é uma tupla de dicts (`name`, `cpf`, `phone`, `status`) definida em `patients.py`, separada da composição visual - mesmo padrão já usado em `APPOINTMENTS` no Dashboard. Trocar por uma API futura significa substituir apenas a fonte usada por `filtered_patients`.

### Badge de status e paginação

Reaproveita o padrão visual de badge "pill" já usado no Dashboard (`status_badge`), mas com uma função própria (`patient_status_badge`) porque os valores/cores ("ativo"/"inativo") são diferentes dos usados em atendimentos ("confirmado"/"aguardando"). A paginação usa ícones `chevron-left`/`chevron-right` da biblioteca Lucide já disponível via `rx.icon`, evitando adicionar novos assets SVG.

## Risks / Trade-offs

- [Risk] Generalizar `Sidebar` pode quebrar o Dashboard se o default mudar. -> Mitigation: manter `active: str = "Início"` como valor padrão e chamar explicitamente `Sidebar(active="Início")` no Dashboard.
- [Risk] Paginação/busca client-side sobre uma lista mockada pode não refletir o comportamento de uma API paginada no servidor (ex.: contagem total, latência). -> Mitigation: isolar a lógica em computed vars substituíveis e deixar explícito no proposal que a integração real é um passo futuro.
- [Risk] Sem ferramenta de browser neste ambiente, a conferência visual pixel-a-pixel com o Figma depende de validação manual. -> Mitigation: validar compilação (`reflex compile --dry`) e renderização via servidor local, e registrar como tarefa manual pendente.

## Migration Plan

1. Generalizar `Sidebar` (parâmetro `active`) e atualizar o Dashboard para chamá-la explicitamente com `active="Início"`.
2. Adicionar `patients.py` com estado, dados mockados e composição visual da tela.
3. Registrar a rota `/pacientes` em `ProjetoCl_nicaCardiologia.py`.
4. Validar compilação e renderização; quando o back-end de pacientes existir, substituir `MOCK_PATIENTS` por uma fonte real em uma change separada.
