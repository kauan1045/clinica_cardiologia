## 1. Navegação

- [x] 1.1 Apontar o item "Médicos" de `MENU_ITEMS` em `dashboard.py` para `/medicos`, verificando o `href` gerado sem alterar o restante do Dashboard, de Pacientes e de Agendamentos.
- [x] 1.2 Registrar a rota `/medicos` em `ProjetoCl_nicaCardiologia.py`, sem rotas dinâmicas.

## 2. Estado e dados mockados

- [x] 2.1 Criar `medicos.py` com `carregar_medicos()` retornando 3 médicos mockados (nome, especialidade, CRM, status) separados da composição visual, verificando que os campos são compatíveis com uma futura fonte real.
- [x] 2.2 Implementar `MedicosState` com `search` e `page`, computed vars `filtered_medicos`, `total_pages`, `page_numbers` e `paginated_medicos`, e o evento `carregar_dados`, verificando que buscar reseta a página para 1.

## 3. Interface (escala das telas existentes)

- [x] 3.1 Compor a página com `Sidebar(active="Médicos")`, `Topbar()` e o mesmo layout de `patients.py` (fundo `#F8FCFD`, coluna `max_width="960px"` com `min_width="0"`, card branco).
- [x] 3.2 Compor o título "Médicos" com o mesmo estilo do título "Pacientes", o campo de busca "Buscar Médico" e o botão "+ Novo Médico" (pílula sem ação, com cursor pointer e hover discreto) na mesma linha.
- [x] 3.3 Compor a tabela com cabeçalho Nome, Especialidade, CRM e Status e linhas com os textos no mesmo estilo da tabela de Pacientes, sem cortes em janelas menores.
- [x] 3.4 Reutilizar `patient_status_badge` de `patients.py` para o status, verificando o badge verde-menta translúcido para "ativo".
- [x] 3.5 Implementar a paginação no mesmo padrão de Pacientes (setas e números, setas desabilitadas nos limites), dentro do card.

## 4. Validação

- [x] 4.1 Executar `reflex compile --dry` e confirmar que compila sem erros.
- [x] 4.2 Conferir a tela em 1280px, 1366px e 1920px, verificando via DevTools que não há rolagem horizontal (`scrollWidth == clientWidth`) e comparando o layout com Pacientes e com o frame do Figma; testar busca e hover do botão.
- [x] 4.3 Confirmar que Login, Dashboard, Pacientes e Agendamentos continuam respondendo e que o link "Médicos" do menu leva à nova tela.
