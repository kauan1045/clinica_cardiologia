## MODIFIED Requirements

### Requirement: Sinalizar status do exame com badge colorido
O status de cada exame SHALL ser exibido em um badge (pílula) próprio da tela Exames, com o mesmo formato do badge de status compartilhado, cuja cor muda conforme o valor (Pendente, Concluído ou Cancelado), sem alterar os badges das demais telas.

#### Scenario: Exame está pendente
- **WHEN** o status do exame é "Pendente"
- **THEN** o badge exibe fundo amarelo-limão translúcido (`#DCED6D` a 30%) e cantos totalmente arredondados, com texto em azul `#05589F`

#### Scenario: Exame está concluído
- **WHEN** o status do exame é "Concluído"
- **THEN** o badge exibe fundo verde-menta translúcido (`#88E0C1` a 30%) e cantos totalmente arredondados, com texto em azul `#05589F`

#### Scenario: Exame está cancelado
- **WHEN** o status do exame é "Cancelado"
- **THEN** o badge exibe fundo vermelho translúcido (`#ED6D6D` a 30%) e cantos totalmente arredondados, com texto em azul `#05589F`
