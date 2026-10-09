## Context

O frame **TELA AGENDAMENTO** (Figma `26:135`) mede 1440×1024 com posicionamento absoluto e dimensões grandes (sidebar de 337px, textos de 20–30px). Uma primeira implementação fiel aos px do Figma, com sidebar e topbar próprias, ficou visualmente maior e inconsistente com Dashboard e Pacientes. Esta versão mantém do Figma a estrutura, as cores e os textos, mas adota a escala e o layout das telas existentes. O Figma não define variáveis/tokens; as cores coincidem com `openspec/design-system.md`.

## Goals / Non-Goals

**Goals:**
- Consistência visual com Pacientes e Dashboard: mesmos `Sidebar`/`Topbar`, mesmo fundo, largura de conteúdo, card branco e estilo de título.
- Preservar do Figma: seletor Dia/Semana/Mês, barra da data, grade de horários, blocos de atendimento e de intervalo, paginação, textos e cores.
- Sem rolagem horizontal e conteúdo que encolhe em janelas menores.
- Isolar dados mockados e funções `carregar_...` para futura troca por API.

**Non-Goals:**
- Reproduzir os px absolutos do Figma; visualizações Semana e Mês; criação/edição de agendamentos; backend; rotas dinâmicas.
- Alterar Dashboard e Pacientes além do href do item "Agendamentos"; padronizar as telas conforme o Figma (change futura).

## Decisions

### Escala das telas existentes em vez dos px do Figma (decidido)

| Elemento | Referência nas telas existentes | Aplicação em Agendamentos |
| --- | --- | --- |
| Navegação | `Sidebar(active=...)`, `Topbar()` de `dashboard.py` | `Sidebar(active="Agendamentos")` e `Topbar()`; sem componentes próprios |
| Página | `patients.py`: fundo `#F8FCFD`, coluna `max_width=960px`, `spacing="6"`, card branco (`padding 1.5rem`, raio 20px, sombra `0 8px 24px rgba(5,88,159,0.08)`) | idêntico |
| Título | Poppins `2.1rem`, 600, `#05589F` | idêntico ao "Pacientes" |
| Horários | texto do nome na tabela de Pacientes (Inter 600, `#05589F`, tamanho padrão) | mesmo estilo, largura fixa de 58px como no Dashboard |
| Textos dos blocos | textos secundários da tabela (`0.9rem`) | Inter 600 `0.9rem`, `#05589F` |
| Seletor Dia/Semana/Mês | pílulas do Figma (Dia `rgba(5,88,159,0.4)`, demais `rgba(106,158,204,0.2)`) | pílulas de `0.95rem` com `padding 0.4rem 1.25rem`, à direita do título |
| Barra da data | pílula do Figma (`rgba(106,158,204,0.2)`, texto `#6A9ECC`) | largura 100% da coluna, texto `1.1rem` alinhado à direita, como no frame |
| Blocos | pílulas translúcidas do Figma (30% de opacidade) | tamanho pelo conteúdo (`padding 0.35rem 1rem`, raio 20px); intervalos com largura mínima `9rem` |
| Paginação | setas e caixas do Figma | setas `chevron-left/right` de 18px como em Pacientes e caixas quadradas de `2rem` com borda 1px `#05589F` e fundo `rgba(217,217,217,0.2)` |

Componentes de navegação próprios (`sidebar_agendamento()`/`topbar_agendamento()`) e os SVGs baixados do Figma foram removidos; o menu usa os ícones existentes em `assets/`. As diferenças de sidebar/topbar entre Figma e app ficam para a change futura de padronização.

### Layout

- Raiz: `rx.hstack` como em `patients.py` (`Sidebar` + coluna de conteúdo), com `on_mount` chamando `carregar_dados`.
- A coluna de conteúdo tem `width="100%"`, `max_width="960px"` e `min_width="0"`, então ocupa a largura disponível até 960px e encolhe em janelas menores.
- Cada horário é uma linha do card (`min_height 3rem`) com o horário à esquerda e, se houver, o bloco ao lado; os textos dos blocos quebram em vez de cortar (`max_width="100%"`).
- O cabeçalho (título + seletor) usa `wrap="wrap"` para não estourar em janelas estreitas.

### Estado

`AgendamentoState` mantém `visualizacao: str = "Dia"`, `pagina: int = 1`, `data_agenda`, `horarios` e `agenda`. `carregar_agenda()`, `carregar_horarios()` e `carregar_data_agenda()` (funções de módulo) são o único ponto a trocar por API; o evento `carregar_dados` os chama em `on_mount`. `linhas_agenda` (computed var) junta horários e atendimentos; o campo `cor` do mock (`azul`/`verde`/`limao`) define o fundo do bloco. `data_exibida` gera "Sáb, 26 de setembro de 2026" a partir de `data_agenda` com `WEEKDAYS`/`MONTHS` de `dashboard.py`, calculando o dia da semana.

### Decisões sobre pontos ambíguos do Figma (confirmadas)

1. **Data**: o frame mostra "Seg, 26 de setembro de 2026", mas 26/09/2026 é sábado; o texto é gerado da data do estado, com o dia da semana calculado (resulta "Sáb").
2. **Cor dos blocos**: azul (Daiane, Kauan) e verde (Iuri, Rhonalds) sem regra explícita; o mock tem um campo `cor` por bloco reproduzindo o frame.
3. **Paginação, Semana e Mês**: apenas trocam o estado (`pagina`, `visualizacao`); a grade continua a mesma grade diária. A paginação não tem estilo de página ativa nem de desabilitado, pois o frame não os define.

## Risks / Trade-offs

- [Risk] O layout deixa de ser pixel-idêntico ao Figma. -> Mitigation: decisão explícita de consistência com as telas existentes; a padronização conforme o Figma será uma change própria.
- [Risk] O `Topbar` compartilhado não encolhe abaixo de ~1000px (o botão "Dr. Roberto" causa ~8px de rolagem horizontal, igual em Pacientes). -> Mitigation: fora do escopo desta change (não altera telas prontas); a verificação de "sem rolagem horizontal" cobre 1280, 1366 e 1920px.
- [Risk] Os dicts responsivos `{"base": ..., "md": ...}` usados nas telas existentes geram CSS inválido no Reflex 0.9.11 (o hstack raiz copia esse padrão, então nenhuma tela empilha em telas pequenas). -> Mitigation: mantido igual a Pacientes por consistência; corrigir na change de padronização com `rx.breakpoints`.
