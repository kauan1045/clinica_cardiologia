## MODIFIED Requirements

### Requirement: Sinalizar status do convênio com badge colorido
O status de cada convênio SHALL ser exibido com o badge de status compartilhado (pílula), cuja cor muda conforme o valor.

#### Scenario: Convênio está ativo
- **WHEN** o status do convênio é "ativo"
- **THEN** o badge exibe fundo verde-menta translúcido e cantos totalmente arredondados, com texto em azul `#05589F`

#### Scenario: Convênio está inativo
- **WHEN** o status do convênio é "inativo"
- **THEN** o badge exibe um estilo neutro (cinza), visualmente distinto do usado para "ativo"
