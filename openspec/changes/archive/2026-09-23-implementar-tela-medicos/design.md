## Context

O frame **Médicos** (Figma `29:271`) mede 1440×1024 com posicionamento absoluto: sidebar e topbar iguais às do frame de Agendamentos (com "Médicos" ativo), título "Médicos" (Poppins 32px), busca "Buscar Médico" (pílula 333×49), botão "+ Novo Médico" (pílula 176×37), barra de cabeçalho da tabela (1057×58) com Nome / Especialidade / CRM / Status, 3 linhas de médicos com badge "ativo" (`#88E0C1` a 30%, 180×34) e paginação 1–4. O Figma não define variáveis/tokens; as cores coincidem com `openspec/design-system.md`. Seguindo a decisão tomada em Agendamentos, o layout adota a escala e os componentes das telas existentes, e não os px do Figma.

## Goals / Non-Goals

**Goals:**
- Consistência visual com Pacientes: mesmos `Sidebar`/`Topbar`, fundo, coluna de 960px, card branco, título, badge de status e paginação.
- Preservar do Figma a estrutura, as cores e os textos.
- Sem rolagem horizontal e conteúdo que encolhe em janelas menores.
- Dados mockados isolados em `carregar_medicos()` para futura troca por API.

**Non-Goals:**
- Reproduzir os px absolutos do Figma; cadastro/edição de médicos (o botão "+ Novo Médico" é só visual); backend; rotas dinâmicas.
- Alterar Dashboard, Pacientes e Agendamentos além do href do item "Médicos".

## Decisions

### Reutilização e escala

| Elemento | Referência nas telas existentes | Aplicação em Médicos |
| --- | --- | --- |
| Navegação | `Sidebar(active=...)`, `Topbar()` de `dashboard.py` | `Sidebar(active="Médicos")` e `Topbar()` |
| Página | `patients.py`: fundo `#F8FCFD`, coluna `max_width=960px`, `spacing="6"`, card branco | idêntico |
| Título | Poppins `2.1rem`, 600, `#05589F` | idêntico ao "Pacientes" |
| Busca | campo de busca de Pacientes (ícone `search`, pílula com borda `#A7D8F0`, `max_width 420px`) com placeholder "Buscar Médico" | idêntico, filtrando por nome, especialidade e CRM |
| Botão "+ Novo Médico" | pílula do Figma (fundo `rgba(5,88,159,0.4)`, texto `#05589F`) | pílula sem ação, com cursor pointer e leve escurecimento no hover, à direita da linha da busca |
| Badge de status | `patient_status_badge` de `patients.py` | importado, sem duplicar |
| Paginação | `pagination()`/`page_button()` de Pacientes | mesmo padrão, com estado próprio (`MedicosState`) |

`patients.py` não é alterado: a paginação de Pacientes está acoplada a `PatientsState`, então o padrão é reescrito em `medicos.py` com `MedicosState`; o badge é importado.

### Estado e dados

`MedicosState` mantém `search` e `page`; `filtered_medicos`, `total_pages`, `page_numbers` e `paginated_medicos` são computed vars derivadas de `carregar_medicos()` (função de módulo, único ponto a trocar por API), com `PAGE_SIZE = 5`. O mock traz os 3 médicos do frame:

| Nome | Especialidade | CRM | Status |
| --- | --- | --- | --- |
| Dr. Felipe Costa | Ecocardiografia | 12345SP | ativo |
| Dra. Juliana Almeida | Cardiologista | 67890SP | ativo |
| Dr. Marcelo Cavalcante | Cardiologista | 00098SP | ativo |

### Pontos ambíguos do Figma (confirmados)

1. **Paginação com 3 médicos**: o frame mostra 4 caixas numeradas (1–4) quadradas, mas há apenas 3 linhas; Pacientes usa números circulares derivados dos dados. Decisão: derivar as páginas dos dados (3 médicos → 1 página), com o estilo de Pacientes.
2. **Cabeçalho da tabela**: o frame usa uma barra em pílula translúcida com rótulos em `#05589F`; Pacientes usa texto simples em `#6A9ECC`. Decisão: o cabeçalho de Pacientes, para consistência.
3. **Botão "+ Novo Médico"**: sem equivalente em Pacientes; decisão: pílula do Figma (`rgba(5,88,159,0.4)`, texto `#05589F`), sem ação, com cursor pointer e hover discreto (`rgba(5,88,159,0.5)`, levemente mais escuro).

## Risks / Trade-offs

- [Risk] O layout deixa de ser pixel-idêntico ao Figma. -> Mitigation: decisão explícita de consistência (mesma de Agendamentos); a padronização conforme o Figma será uma change própria.
- [Risk] O `Topbar` compartilhado não encolhe abaixo de ~1000px (o botão "Dr. Roberto" causa ~8px de rolagem horizontal, igual em Pacientes e Agendamentos). -> Mitigation: fora do escopo; a verificação de "sem rolagem horizontal" cobre 1280, 1366 e 1920px.
- [Risk] Os dicts responsivos `{"base": ..., "md": ...}` do layout raiz geram CSS inválido no Reflex 0.9.11 (nenhuma tela empilha em telas pequenas). -> Mitigation: mantido igual às outras telas; corrigir na change de padronização com `rx.breakpoints`.
