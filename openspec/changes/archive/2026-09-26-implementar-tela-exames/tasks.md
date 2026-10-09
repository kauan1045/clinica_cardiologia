## 1. Navegação

- [x] 1.1 Apontar o item "Exames" de `MENU_ITEMS` em `dashboard.py` para `/exames`, sem alterar o restante do Dashboard e das telas prontas.
- [x] 1.2 Registrar a rota `/exames` em `ProjetoCl_nicaCardiologia.py`, sem rotas dinâmicas.

## 2. Estado e dados mockados

- [x] 2.1 Criar `exames.py` com `carregar_exames()` retornando 5 exames mockados (paciente, tipo de exame, médico solicitante, data, status) separados da composição visual, com a data como texto `dd/mm/aaaa`.
- [x] 2.2 Implementar `ExamesState` com `search` e `page`, computed vars `filtered_exames`, `total_pages`, `page_numbers` e `paginated_exames`, e o evento `carregar_dados`; a busca filtra por paciente e tipo de exame e reseta a página para 1.

## 3. Interface (escala das telas existentes)

- [x] 3.1 Compor a página com `Sidebar(active="Exames")`, `Topbar()` e o mesmo layout de `convenio.py` (fundo `#F8FCFD`, coluna `max_width="960px"` com `min_width="0"`, card branco).
- [x] 3.2 Compor o título "Exames" com o mesmo estilo dos demais, o campo de busca "Buscar paciente ou exame" e o botão "+ Novo Exame" (igual ao "+ Novo Convênio": sem ação, cursor pointer e hover discreto) na mesma linha.
- [x] 3.3 Compor a tabela com cabeçalho Paciente, Tipo de Exame, Médico Solicitante, Data e Status no mesmo estilo do cabeçalho de Pacientes, com larguras relativas que evitem rolagem horizontal e cortes.
- [x] 3.4 Criar `exame_status_badge` em `exames.py` (pílula com o mesmo formato de `patient_status_badge`) com cores por status: Pendente `#DCED6D`, Concluído `#88E0C1` e Cancelado `#ED6D6D`, todas a 30%, e texto `#05589F`, sem alterar os badges existentes.
- [x] 3.5 Implementar a paginação no mesmo padrão das demais telas (setas e números derivados dos dados, setas desabilitadas nos limites), dentro do card.

## 4. Validação

- [x] 4.1 Executar `reflex compile --dry` e `openspec validate implementar-tela-exames --strict`, confirmando que ambos passam sem erros.
- [x] 4.2 Executar `reflex run` e conferir a tela em 1280px, 1366px e 1920px, sem rolagem horizontal e sem cortes, comparando o layout com Convênio e com o frame do Figma.
- [x] 4.3 Testar a busca (por paciente, por tipo de exame e sem resultado) e o hover do botão "+ Novo Exame".
- [x] 4.4 Confirmar que Login, Dashboard, Pacientes, Agendamentos, Médicos e Convênio continuam respondendo e que o link "Exames" do menu leva à nova tela.
