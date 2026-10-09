## 1. Navegação

- [x] 1.1 Apontar o item "Convênio" de `MENU_ITEMS` em `dashboard.py` para `/convenio`, verificando o `href` gerado sem alterar o restante do Dashboard, de Pacientes, de Agendamentos e de Médicos.
- [x] 1.2 Registrar a rota `/convenio` em `ProjetoCl_nicaCardiologia.py`, sem rotas dinâmicas.

## 2. Estado e dados mockados

- [x] 2.1 Criar `convenio.py` com `carregar_convenios()` retornando 5 convênios mockados (nome, registro ANS, cobertura, pacientes vinculados, status) separados da composição visual, mantendo o registro ANS como texto para preservar zeros à esquerda.
- [x] 2.2 Implementar `ConvenioState` com `search` e `page`, computed vars `filtered_convenios`, `total_pages`, `page_numbers` e `paginated_convenios`, e o evento `carregar_dados`, verificando que buscar reseta a página para 1.

## 3. Interface (escala das telas existentes)

- [x] 3.1 Compor a página com `Sidebar(active="Convênio")`, `Topbar()` e o mesmo layout de `medicos.py` (fundo `#F8FCFD`, coluna `max_width="960px"` com `min_width="0"`, card branco).
- [x] 3.2 Compor o título "Convênio" com o mesmo estilo do título "Médicos", o campo de busca "Buscar Convênio" e o botão "+ Novo Convênio" (pílula sem ação, com cursor pointer e hover discreto, igual ao "+ Novo Médico") na mesma linha.
- [x] 3.3 Compor a tabela com cabeçalho Nome, Registro ANS, Cobertura, Pacientes vinculados e Status no mesmo estilo do cabeçalho de Pacientes, com larguras relativas que evitem rolagem horizontal e cortes.
- [x] 3.4 Reutilizar `patient_status_badge` de `patients.py` para o status, verificando o badge verde-menta para "ativo" e o badge cinza para "inativo".
- [x] 3.5 Implementar a paginação no mesmo padrão de Pacientes e Médicos (setas e números derivados dos dados, setas desabilitadas nos limites), dentro do card.

## 4. Validação

- [x] 4.1 Executar `reflex compile --dry` e `openspec validate implementar-tela-convenio --strict`, confirmando que ambos passam sem erros.
- [ ] 4.2 Executar `reflex run`, conferir a tela em 1280px, 1366px e 1920px, verificando que não há rolagem horizontal (`scrollWidth == clientWidth`) e comparando o layout com Médicos e com o frame do Figma; testar busca e hover do botão.
- [x] 4.3 Confirmar que Login, Dashboard, Pacientes, Agendamentos e Médicos continuam respondendo e que o link "Convênio" do menu leva à nova tela.
