## 1. Navegação

- [x] 1.1 Apontar o item "Agendamentos" de `MENU_ITEMS` em `dashboard.py` para `/agendamento`, verificando o `href` gerado sem alterar o restante do Dashboard e de Pacientes.
- [x] 1.2 Registrar a rota `/agendamento` em `ProjetoCl_nicaCardiologia.py`, sem rotas dinâmicas.

## 2. Estado e dados mockados

- [x] 2.1 Criar `agendamento.py` com dados mockados (horários 08:00–14:30, 4 atendimentos, 4 intervalos, data da agenda) separados da composição visual.
- [x] 2.2 Implementar `AgendamentoState` com `visualizacao` (Dia/Semana/Mês, padrão "Dia"), `pagina` (1 a 4), funções isoladas `carregar_agenda`, `carregar_horarios`, `carregar_data_agenda` e o evento `carregar_dados`, verificando que trocar a fonte não exige alterar a composição visual.
- [x] 2.3 Implementar `data_exibida` a partir de `data_agenda` com o dia da semana calculado ("Sáb, 26 de setembro de 2026") e `linhas_agenda` juntando horários e atendimentos.
- [x] 2.4 Implementar os eventos de troca de visualização e de navegação de página (setas e números limitados a 1–4, sem estilo desabilitado, pois o frame não o define).

## 3. Interface (escala das telas existentes)

- [x] 3.1 Compor a página com `Sidebar(active="Agendamentos")`, `Topbar()` e o mesmo layout de `patients.py` (fundo `#F8FCFD`, coluna `max_width="960px"` com `min_width="0"`, card branco), removendo `sidebar_agendamento()`/`topbar_agendamento()` e os SVGs do Figma.
- [x] 3.2 Compor o título "Agendamentos" com o mesmo estilo do título "Pacientes" e o seletor Dia/Semana/Mês (pílulas, Dia selecionado) à direita, com quebra de linha em janelas estreitas.
- [x] 3.3 Compor a barra da data (pílula `rgba(106,158,204,0.2)`, texto `#6A9ECC` alinhado à direita) ocupando a largura da coluna.
- [x] 3.4 Compor a grade de horários (mesmo estilo do nome na tabela de Pacientes) com blocos de atendimento (`#6A9ECC`/`#88E0C1` a 30%) e de intervalo (`#DCED6D` a 30%), textos em `0.9rem` sem cortes.
- [x] 3.5 Compor a paginação (setas `chevron` como em Pacientes e caixas 1–4 com borda 1px `#05589F` e fundo `rgba(217,217,217,0.2)`) dentro do card.

## 4. Validação

- [x] 4.1 Executar `reflex compile --dry` e confirmar que compila sem erros.
- [x] 4.2 Conferir a tela em 1280px, 1366px e 1920px, verificando via DevTools que não há rolagem horizontal (`scrollWidth == clientWidth`) e comparando o layout com Pacientes.
- [x] 4.3 Confirmar que Login, Dashboard e Pacientes continuam respondendo e que o link "Agendamentos" do menu leva à nova tela.
