## 1. Navegação compartilhada

- [x] 1.1 Generalizar `Sidebar` em `dashboard.py` para aceitar `active: str = "Início"` em vez do item ativo fixo, verificando que o Dashboard continua destacando "Início" ao chamar `Sidebar(active="Início")`.
- [x] 1.2 Apontar o item "Pacientes" do menu para a rota real `/pacientes` (antes `#pacientes`), verificando o `href` gerado.

## 2. Tela Pacientes

- [x] 2.1 Criar `patients.py` com `MOCK_PATIENTS` (nome, CPF, telefone, status) separada da composição visual, verificando que os campos são compatíveis com uma futura fonte real.
- [x] 2.2 Implementar `PatientsState` com busca (`search`) e paginação (`page`), com computed vars `filtered_patients`, `total_pages`, `page_numbers` e `paginated_patients`, verificando que buscar reseta a página para 1.
- [x] 2.3 Compor a tela com `Sidebar(active="Pacientes")`, `Topbar()`, título "Pacientes", campo de busca com placeholder "Buscar paciente" e tabela com colunas Nome, CPF, Telefone, Status, verificando a ordem das colunas e a ausência de bordas pesadas entre linhas.
- [x] 2.4 Implementar o badge de status com cor condicional (verde-menta translúcido/texto azul para "ativo", cor distinta para "inativo"), verificando a mudança de cor conforme o valor.
- [x] 2.5 Implementar a paginação com setas anterior/próxima (desabilitadas nos limites) e números de página, destacando a página atual com borda azul `#05589F`, verificando a navegação entre páginas.
- [x] 2.6 Registrar a rota `/pacientes` em `ProjetoCl_nicaCardiologia.py`, verificando que a página é acessível.

## 3. Validação

- [x] 3.1 Executar `reflex compile --dry` e corrigir erros de componentes, estado ou rotas.
- [x] 3.2 Subir o servidor (`reflex run --env prod --single-port`) e verificar que `GET /pacientes` retorna 200 e o HTML inclui "Pacientes" e "Buscar paciente", sem erros no log.
- [ ] 3.3 Verificar visualmente a tela Pacientes em um navegador (desktop e mobile) e comparar com o protótipo do Figma linkado na proposta, confirmando cores, tipografia e espaçamento — não realizado nesta change por falta de ferramenta de browser no ambiente.
