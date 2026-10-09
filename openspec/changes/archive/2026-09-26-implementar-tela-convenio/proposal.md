## Why

A clínica precisa consultar os convênios aceitos no CardioVida. As telas de Login, Dashboard, Pacientes, Agendamentos e Médicos já existem, mas o item "Convênio" do menu ainda aponta para uma âncora (`#convenio`); esta change implementa a tela Convênio conforme o frame **Convênio** (Figma, node `31:374`, 1440×1024), seguindo a escala visual e o layout das telas já implementadas.

## What Changes

- Criar a tela Convênio (rota `/convenio`) com título "Convênio", campo de busca (placeholder "Buscar Convênio"), botão "+ Novo Convênio" (apenas visual) e tabela com as colunas Nome, Registro ANS, Cobertura, Pacientes vinculados e Status, exibindo 5 convênios mockados.
- Reutilizar `Sidebar(active="Convênio")`, `Topbar()` e o mesmo layout de página das telas Pacientes e Médicos (fundo, largura máxima, card branco, estilo de título), sem componentes próprios de navegação.
- Reutilizar o badge de status de Pacientes (`patient_status_badge`) e o mesmo padrão de paginação e de cabeçalho de tabela.
- Apontar o item "Convênio" do menu para a nova rota `/convenio`.
- Usar dados mockados isolados em `ConvenioState`, com função `carregar_convenios` separada para permitir a troca futura por chamadas à API (Xano).
- Tamanhos seguem a escala das telas existentes (rem e larguras relativas), e não os px absolutos do Figma.
- O texto do Figma "Buscar Médico" no campo de busca é tratado como erro do protótipo; o placeholder correto é "Buscar Convênio".

## Capabilities

### New Capabilities
- `convenio`: Listagem de convênios da clínica (nome, registro ANS, cobertura, pacientes vinculados e status), com busca e paginação, reaproveitando a navegação e o layout compartilhados.

### Modified Capabilities
- `dashboard-inicio`: o item "Convênio" do menu lateral compartilhado passa a apontar para a tela Convênio implementada.

## Impact

- Adiciona `ProjetoCl_nicaCardiologia/convenio.py` (tela, `ConvenioState`, dados mockados).
- Afeta `ProjetoCl_nicaCardiologia/dashboard.py` apenas em `MENU_ITEMS` (href `#convenio` → `/convenio`) e `ProjetoCl_nicaCardiologia.py` (registro da rota `/convenio`). Não altera `patients.py`, `medicos.py` nem `agendamento.py`.
- Não adiciona assets, dependências, backend, autenticação, nem cadastro/edição de convênios (o botão "+ Novo Convênio" não tem ação).
