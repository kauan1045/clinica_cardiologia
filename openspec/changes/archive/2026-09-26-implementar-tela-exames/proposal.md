## Why

A clínica precisa consultar os exames solicitados no CardioVida. As telas de Login, Dashboard, Pacientes, Agendamentos, Médicos e Convênio já existem, mas o item "Exames" do menu ainda aponta para uma âncora (`#exames`); esta change implementa a tela Exames conforme o frame **Exames** (Figma, node `31:467`, 1440×1024), seguindo a escala visual e o layout das telas já implementadas.

## What Changes

- Criar a tela Exames (rota `/exames`) com título "Exames", campo de busca (placeholder "Buscar paciente ou exame"), botão "+ Novo Exame" (apenas visual) e tabela com as colunas Paciente, Tipo de Exame, Médico Solicitante, Data e Status, exibindo 5 exames mockados.
- Reutilizar `Sidebar(active="Exames")`, `Topbar()` e o mesmo layout de página das telas Pacientes, Médicos e Convênio (fundo, largura máxima, card branco, estilo de título), sem componentes próprios de navegação.
- Criar um badge de status próprio da tela (`exame_status_badge`), no mesmo formato de pílula do badge de Pacientes, com três valores: Pendente (amarelo-limão `#DCED6D` a 30%), Concluído (verde-menta `#88E0C1` a 30%) e Cancelado (vermelho `#ED6D6D` a 30%), todos com texto `#05589F`, conforme o Figma. Os badges existentes não são alterados.
- Reutilizar o mesmo padrão de paginação e de cabeçalho de tabela de Pacientes.
- Apontar o item "Exames" do menu para a nova rota `/exames`.
- Usar dados mockados isolados em `ExamesState`, com função `carregar_exames` separada para permitir a troca futura por chamadas à API (Xano).
- Tamanhos seguem a escala das telas existentes (rem e larguras relativas), e não os px absolutos do Figma.
- O texto do Figma "Buscar Paciente ou exame" é normalizado para "Buscar paciente ou exame".

## Capabilities

### New Capabilities
- `exames`: Listagem de exames da clínica (paciente, tipo de exame, médico solicitante, data e status), com busca por paciente e tipo de exame e paginação, reaproveitando a navegação e o layout compartilhados.

### Modified Capabilities
- `dashboard-inicio`: o item "Exames" do menu lateral compartilhado passa a apontar para a tela Exames implementada.

## Impact

- Adiciona `ProjetoCl_nicaCardiologia/exames.py` (tela, `ExamesState`, badge de status, dados mockados).
- Afeta `ProjetoCl_nicaCardiologia/dashboard.py` apenas em `MENU_ITEMS` (href `#exames` → `/exames`) e `ProjetoCl_nicaCardiologia.py` (registro da rota `/exames`). Não altera `patients.py`, `medicos.py`, `convenio.py` nem `agendamento.py`.
- Não adiciona assets, dependências, backend, autenticação, nem cadastro/edição de exames (o botão "+ Novo Exame" não tem ação).
