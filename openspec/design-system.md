# Design System CardioVida

## Objetivo

Este documento define os padrões visuais compartilhados da aplicação CardioVida. Novas telas e changes devem reutilizar esta paleta e manter os significados semânticos das cores.

## Paleta de cores

| Nome | Hex | Uso |
| --- | --- | --- |
| Azul Cobalto | `#05589F` | Cor principal para fontes. |
| Azul Médio | `#6A9ECC` | Cor de apoio para fontes. |
| Verde Limão | `#DCED6D` | Usar somente em ícones que sinalizam informações importantes. |
| Azul Bebê | `#A7D8F0` | Superfícies, fundos e detalhes de apoio. |
| Verde | `#88E0C1` | Superfícies e elementos de apoio. |
| Verde Sálvia | `#4A7A69` | Cor do logo, cor secundária e fonte. |
| Vermelho de Status | `#ED6D6D` | Status e alertas. |
| Branco | `#FFFFFF` | Fundo, superfícies e contraste. |

## Logo e ícone

O logo/ícone de referência da aplicação é `assets/bi_heart-pulse.svg`. Telas que exibem a marca CardioVida devem usar esse asset e preservar sua proporção sem distorção.

## Tipografia

A aplicação usa Google Fonts carregadas globalmente pelo `rxconfig.py`:

- **Poppins**, peso SemiBold `600`, em `64px`: nome do logo CardioVida e títulos ou textos informativos grandes.
- **Inter**, peso SemiBold `600`, em `24px`: legendas, textos explicativos e demais textos secundários em todas as telas.

Novas telas devem manter essas famílias, pesos e papéis tipográficos, ajustando apenas o tamanho de forma responsiva quando necessário para preservar a legibilidade.

## Regras de uso

- Aplicar a paleta em toda a aplicação, não apenas na tela de login.
- Usar o Verde Limão exclusivamente em ícones de informação importante; não usar como cor geral de texto, fundo ou botão.
- Usar o Vermelho de Status para estados de erro, alerta ou status, mantendo o texto associado para não depender apenas da cor.
- Manter contraste suficiente entre texto e superfície e preservar a legibilidade em layouts responsivos.
- Novas changes devem consultar este documento antes de definir cores ou substituir o logo.
