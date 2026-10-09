## MODIFIED Requirements

### Requirement: Sinalizar status do médico com badge colorido
O status de cada médico SHALL ser exibido com o badge de status compartilhado (pílula), cuja cor muda conforme o valor.

#### Scenario: Médico está ativo
- **WHEN** o status do médico é "ativo"
- **THEN** o badge exibe fundo verde-menta translúcido e cantos totalmente arredondados, com texto em azul `#05589F`
