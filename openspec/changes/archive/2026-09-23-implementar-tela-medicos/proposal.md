## Why

A clínica precisa consultar os médicos cadastrados no CardioVida. As telas de Login, Dashboard, Pacientes e Agendamentos já existem, mas o item "Médicos" do menu ainda aponta para uma âncora (`#medicos`); esta change implementa a tela Médicos conforme o frame **Médicos** (Figma, node `29:271`, 1440×1024), seguindo a escala visual e o layout das telas já implementadas.

## What Changes

- Criar a tela Médicos (rota `/medicos`) com título "Médicos", campo de busca (placeholder "Buscar Médico"), botão "+ Novo Médico" (apenas visual) e tabela com as colunas Nome, Especialidade, CRM e Status, exibindo 3 médicos mockados.
- Reutilizar `Sidebar(active="Médicos")`, `Topbar()` e o mesmo layout de página da tela Pacientes (fundo, largura máxima, card branco, estilo de título), sem componentes próprios de navegação.
- Reutilizar o badge de status de Pacientes (`patient_status_badge`) e o mesmo padrão de paginação.
- Apontar o item "Médicos" do menu para a nova rota `/medicos`.
- Usar dados mockados isolados em `MedicosState`, com função `carregar_medicos` separada para permitir a troca futura por chamadas à API (Xano).
- Tamanhos seguem a escala das telas existentes (rem e larguras relativas), e não os px absolutos do Figma.

## Capabilities

### New Capabilities
- `medicos`: Listagem de médicos da clínica (nome, especialidade, CRM e status), com busca e paginação, reaproveitando a navegação e o layout compartilhados.

### Modified Capabilities
- `dashboard-inicio`: o item "Médicos" do menu lateral compartilhado passa a apontar para a tela Médicos implementada.

## Impact

- Adiciona `ProjetoCl_nicaCardiologia/medicos.py` (tela, `MedicosState`, dados mockados).
- Afeta `ProjetoCl_nicaCardiologia/dashboard.py` apenas em `MENU_ITEMS` (href `#medicos` → `/medicos`) e `ProjetoCl_nicaCardiologia.py` (registro da rota `/medicos`). Não altera `patients.py` nem `agendamento.py`.
- Não adiciona assets, dependências, backend, autenticação, nem cadastro/edição de médicos (o botão "+ Novo Médico" não tem ação).
