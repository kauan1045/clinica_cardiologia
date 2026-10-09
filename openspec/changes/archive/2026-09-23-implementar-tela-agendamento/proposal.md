## Why

A clínica precisa visualizar a agenda do dia com os atendimentos e intervalos organizados por horário. As telas de Login, Dashboard e Pacientes já existem, mas o item "Agendamentos" do menu ainda aponta para uma âncora (`#agendamentos`); esta change implementa a tela Agendamentos com a estrutura, as cores e os textos do frame **TELA AGENDAMENTO** (Figma, node `26:135`), seguindo a escala visual e o layout das telas já implementadas.

## What Changes

- Criar a tela Agendamentos (rota `/agendamento`) com título "Agendamentos", seletor de visualização Dia / Semana / Mês (Dia selecionado), barra com a data por extenso, grade de horários de 30 em 30 minutos (08:00 a 14:30) com blocos de atendimento e de "Intervalo", e paginação numérica (1 a 4).
- Reutilizar `Sidebar(active="Agendamentos")` e `Topbar()` de `dashboard.py` e o mesmo layout de página da tela Pacientes (fundo, largura máxima, card branco, estilo de título), sem componentes próprios de navegação.
- Apontar o item "Agendamentos" do menu para a nova rota `/agendamento`.
- Usar dados mockados isolados em um `AgendamentoState`, com funções `carregar_...` separadas para permitir a troca futura por chamadas à API (Xano).
- Tamanhos seguem a escala das telas existentes (rem e larguras relativas), e não os px absolutos do Figma.

## Capabilities

### New Capabilities
- `agendamento`: Visualização da agenda da clínica em grade diária por horário, com atendimentos, intervalos, seletor de visualização e paginação.

### Modified Capabilities
- `dashboard-inicio`: o item "Agendamentos" do menu lateral compartilhado passa a apontar para a tela Agendamentos implementada.

## Impact

- Adiciona `ProjetoCl_nicaCardiologia/agendamento.py` (tela, `AgendamentoState`, dados mockados).
- Afeta `ProjetoCl_nicaCardiologia/dashboard.py` apenas em `MENU_ITEMS` (href `#agendamentos` → `/agendamento`) e `ProjetoCl_nicaCardiologia.py` (registro da rota `/agendamento`).
- Não adiciona assets, dependências, backend, autenticação, criação/edição de agendamentos nem as visualizações Semana e Mês (apenas o controle aparece, como no frame).
- A padronização de todas as telas conforme as dimensões do Figma fica para uma change separada.
