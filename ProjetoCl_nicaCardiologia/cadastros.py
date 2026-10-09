"""Base compartilhada das telas de cadastro integradas ao Xano (listar e incluir)."""

import re
from datetime import date, datetime, timezone
from typing import Any, ClassVar

import reflex as rx

from ProjetoCl_nicaCardiologia import api
from ProjetoCl_nicaCardiologia.auth import AuthState
from ProjetoCl_nicaCardiologia.dashboard import Sidebar, Topbar


PAGE_SIZE = 5
SUCESSO_CADASTRO = "Cadastrado com sucesso"
LIST_KEYS = ("items", "itens", "data", "result", "results")


# ---------------------------------------------------------------- formatação


def campo(item: dict[str, Any], *chaves: str) -> Any:
    """Primeiro valor não vazio entre as chaves; tolera nomes diferentes vindos da API."""
    for chave in chaves:
        valor = item.get(chave)
        if valor is not None and valor != "":
            return valor
    return None


def texto(valor: Any) -> str:
    return "" if valor is None else str(valor).strip()


def so_digitos(valor: Any) -> str:
    return re.sub(r"\D", "", texto(valor))


def mascara_cpf(valor: Any) -> str:
    """Máscara progressiva 000.000.000-00 enquanto o usuário digita."""
    d = so_digitos(valor)[:11]
    if len(d) <= 3:
        return d
    if len(d) <= 6:
        return f"{d[:3]}.{d[3:]}"
    if len(d) <= 9:
        return f"{d[:3]}.{d[3:6]}.{d[6:]}"
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


def formatar_cpf(valor: Any) -> str:
    return mascara_cpf(valor) if len(so_digitos(valor)) == 11 else texto(valor)


def mascara_telefone(valor: Any) -> str:
    """Máscara progressiva (00) 0000-0000 / (00) 00000-0000."""
    d = so_digitos(valor)[:11]
    if not d:
        return ""
    if len(d) <= 2:
        return f"({d}"
    if len(d) <= 6:
        return f"({d[:2]}) {d[2:]}"
    corte = 7 if len(d) == 11 else 6
    return f"({d[:2]}) {d[2:corte]}-{d[corte:]}"


def formatar_telefone(valor: Any) -> str:
    return mascara_telefone(valor) if len(so_digitos(valor)) in (10, 11) else texto(valor)


def formatar_data(valor: Any) -> str:
    """Aceita `AAAA-MM-DD`, data/hora ISO ou timestamp em ms do Xano; devolve DD/MM/AAAA."""
    if valor is None or valor == "":
        return ""
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        try:
            return datetime.fromtimestamp(valor / 1000, tz=timezone.utc).strftime("%d/%m/%Y")
        except (OverflowError, OSError, ValueError):
            return texto(valor)
    bruto = texto(valor)
    try:
        return date.fromisoformat(bruto[:10]).strftime("%d/%m/%Y")
    except ValueError:
        return bruto


def converter_numero(valor: Any) -> float | None:
    """Converte "1.234,56", "150.5", "R$ 10" ou "15%" em número; None se inválido."""
    bruto = texto(valor).replace("R$", "").replace("%", "").replace(" ", "")
    if not bruto:
        return None
    if "," in bruto:
        bruto = bruto.replace(".", "").replace(",", ".")
    try:
        return float(bruto)
    except ValueError:
        return None


def _numero_br(numero: float, casas: int) -> str:
    return f"{numero:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_valor(valor: Any) -> str:
    numero = converter_numero(valor) if not isinstance(valor, (int, float)) else float(valor)
    return texto(valor) if numero is None else _numero_br(numero, 2)


def formatar_percentual(valor: Any) -> str:
    numero = converter_numero(valor) if not isinstance(valor, (int, float)) else float(valor)
    if numero is None:
        return texto(valor)
    if numero == int(numero):
        return f"{_numero_br(numero, 0)}%"
    return f"{_numero_br(numero, 2).rstrip('0').rstrip(',')}%"


def numero_json(numero: float) -> int | float:
    return int(numero) if numero == int(numero) else numero


def data_nascimento_valida(valor: str) -> str | None:
    """Devolve a data em AAAA-MM-DD se for válida (de 1900 até hoje)."""
    try:
        data = date.fromisoformat(valor.strip())
    except ValueError:
        return None
    if data.year < 1900 or data > date.today():
        return None
    return data.isoformat()


def mensagem_erro(error: api.ApiError, acao: str, dica: str = "Verifique os dados e tente novamente.") -> str:
    """Mensagem em português; as mensagens do Xano (em inglês) não são exibidas cruas."""
    status = error.status
    if status is None or status >= 500:
        return error.message
    if status == 403:
        return f"Você não tem permissão para {acao}."
    detalhe = error.message.lower()
    if any(chave in detalhe for chave in ("duplicate", "unique", "already")):
        return "Já existe um cadastro com esses dados."
    return f"Não foi possível {acao}. {dica}"


# --------------------------------------------------------------------- estado


class CadastroState(rx.State, mixin=True):
    """Lista vinda da API (busca pelo filtro `busca`, paginação local) e modal de inclusão."""

    ENDPOINT: ClassVar[str] = ""
    LIST_ENDPOINT: ClassVar[str] = ""  # quando a listagem usa outra rota (ex.: /lista_medico)
    NOME_LISTA: ClassVar[str] = "os registros"
    VAZIO: ClassVar[str] = "Nenhum registro cadastrado"
    VAZIO_BUSCA: ClassVar[str] = "Nenhum registro encontrado para a busca"

    itens: list[dict[str, str]] = []
    search: str = ""
    page: int = 1
    carregando: bool = True
    erro_lista: str = ""
    modal_aberto: bool = False
    salvando: bool = False
    erro_form: str = ""

    # Implementados por cada tela.
    def _normalizar(self, item: dict[str, Any]) -> dict[str, str]:
        raise NotImplementedError

    def _validar(self) -> tuple[dict[str, Any] | None, str]:
        raise NotImplementedError

    def _limpar_formulario(self) -> None:
        raise NotImplementedError

    async def _buscar(self):
        """Busca a lista na API; devolve o evento de sessão expirada, se for o caso."""
        termo = self.search.strip()
        token = (await self.get_state(AuthState)).obter_token()
        try:
            data = await api.request("GET", self.LIST_ENDPOINT or self.ENDPOINT, token=token, params={"busca": termo} if termo else None)
            lista = _extrair_lista(data)
            self.itens = [self._normalizar(item) for item in lista if isinstance(item, dict)]
            self.erro_lista = ""
        except api.SessionExpired:
            self.carregando = False
            return AuthState.sessao_expirada
        except api.ApiError as error:
            self.itens = []
            self.erro_lista = mensagem_erro(error, f"carregar {self.NOME_LISTA}", "Tente novamente.")
        self.page = min(self.page, self.total_pages)
        self.carregando = False
        return None

    @rx.event
    async def carregar_dados(self):
        self.carregando = True
        self.erro_lista = ""
        yield
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.event
    async def set_search(self, value: str):
        self.search = value
        self.page = 1
        self.carregando = True
        yield
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.event
    def go_to_page(self, page: int):
        self.page = page

    @rx.event
    def prev_page(self):
        if self.page > 1:
            self.page -= 1

    @rx.event
    def next_page(self):
        if self.page < self.total_pages:
            self.page += 1

    @rx.event
    def abrir_modal(self):
        self._limpar_formulario()
        self.erro_form = ""
        self.modal_aberto = True

    @rx.event
    def fechar_modal(self):
        if not self.salvando:
            self.modal_aberto = False
            self.erro_form = ""

    @rx.event
    def alterar_modal(self, aberto: bool):
        if not aberto and not self.salvando:
            self.modal_aberto = False
            self.erro_form = ""

    @rx.event
    async def salvar(self, form_data: dict[str, Any]):
        # Os campos são controlados pelo estado; o form só dispara o envio (inclusive com Enter).
        if self.salvando:
            return
        payload, erro = self._validar()
        if payload is None:
            self.erro_form = erro
            return

        self.salvando = True
        self.erro_form = ""
        yield
        token = (await self.get_state(AuthState)).obter_token()
        try:
            await api.request("POST", self.ENDPOINT, token=token, json=payload)
        except api.SessionExpired:
            self.salvando = False
            self.modal_aberto = False
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.salvando = False
            self.erro_form = mensagem_erro(error, "cadastrar")
            return

        self.salvando = False
        self.modal_aberto = False
        self._limpar_formulario()
        self.carregando = True
        yield rx.toast.success(SUCESSO_CADASTRO, position="top-center")
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.var
    def total_pages(self) -> int:
        return max(1, -(-len(self.itens) // PAGE_SIZE))

    @rx.var
    def page_numbers(self) -> list[int]:
        return list(range(1, self.total_pages + 1))

    @rx.var
    def pagina_itens(self) -> list[dict[str, str]]:
        start = (self.page - 1) * PAGE_SIZE
        return self.itens[start : start + PAGE_SIZE]

    @rx.var
    def mensagem_vazia(self) -> str:
        return self.VAZIO_BUSCA if self.search.strip() else self.VAZIO


def _extrair_lista(data: Any) -> list[Any]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for chave in LIST_KEYS:
            if isinstance(data.get(chave), list):
                return data[chave]
    raise api.ApiError(api.UNEXPECTED_RESPONSE_MESSAGE)


# ----------------------------------------------------------------- componentes


def botao_novo(rotulo: str, on_click: Any) -> rx.Component:
    return rx.el.button(
        rotulo,
        type="button",
        on_click=on_click,
        style={
            "border": "none",
            "borderRadius": "9999px",
            "padding": "0.55rem 1.4rem",
            "cursor": "pointer",
            "fontFamily": "Inter",
            "fontSize": "0.95rem",
            "fontWeight": "600",
            "color": "#05589F",
            "background": "rgba(5,88,159,0.4)",
            "whiteSpace": "nowrap",
            "&:hover": {"background": "rgba(5,88,159,0.5)"},
        },
    )


def _page_button(state: type[CadastroState], page_number: rx.Var[int]) -> rx.Component:
    is_active = state.page == page_number
    return rx.button(
        rx.text(page_number.to_string(), font_family="Inter", font_size="0.9rem", font_weight="600"),
        on_click=state.go_to_page(page_number),
        variant="ghost",
        color=rx.cond(is_active, "#05589F", "#6A9ECC"),
        background="transparent",
        border=rx.cond(is_active, "2px solid #05589F", "2px solid transparent"),
        border_radius="9999px",
        min_width="2.5rem",
        height="2.5rem",
        padding="0",
    )


def paginacao(state: type[CadastroState]) -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon(tag="chevron-left", size=18),
            aria_label="Página anterior",
            on_click=state.prev_page,
            disabled=state.page <= 1,
            variant="ghost",
            color="#05589F",
            border_radius="9999px",
            padding="0.5rem",
        ),
        rx.foreach(state.page_numbers, lambda numero: _page_button(state, numero)),
        rx.button(
            rx.icon(tag="chevron-right", size=18),
            aria_label="Próxima página",
            on_click=state.next_page,
            disabled=state.page >= state.total_pages,
            variant="ghost",
            color="#05589F",
            border_radius="9999px",
            padding="0.5rem",
        ),
        spacing="2",
        align="center",
        justify="center",
        width="100%",
        padding_top="1.5rem",
    )


def _aviso_lista(*children: rx.Component) -> rx.Component:
    return rx.vstack(*children, width="100%", align="center", spacing="3", padding="2.5rem 0.5rem")


def corpo_lista(state: type[CadastroState], linha: Any) -> rx.Component:
    """Linhas da tabela com os estados de carregando, erro e lista vazia."""
    return rx.cond(
        state.carregando,
        _aviso_lista(
            rx.spinner(size="3", color="#05589F"),
            rx.text("Carregando...", color="#6A9ECC", font_family="Inter", font_size="0.95rem", font_weight="600"),
        ),
        rx.cond(
            state.erro_lista != "",
            _aviso_lista(
                rx.hstack(
                    rx.icon(tag="circle-alert", size=18, color="#ED6D6D"),
                    rx.text(state.erro_lista, color="#05589F", font_family="Inter", font_size="0.95rem", font_weight="600"),
                    align="center",
                    spacing="2",
                ),
                rx.button(
                    "Tentar novamente",
                    on_click=state.carregar_dados,
                    variant="ghost",
                    color="#05589F",
                    font_family="Inter",
                    font_weight="600",
                    border_radius="9999px",
                ),
            ),
            rx.cond(
                state.itens.length() == 0,
                _aviso_lista(
                    rx.text(state.mensagem_vazia, color="#6A9ECC", font_family="Inter", font_size="0.95rem", font_weight="600"),
                ),
                rx.vstack(
                    rx.vstack(rx.foreach(state.pagina_itens, linha), spacing="3", width="100%"),
                    paginacao(state),
                    spacing="4",
                    width="100%",
                ),
            ),
        ),
    )


def campo_input(rotulo: str, value: rx.Var, on_change: Any, obrigatorio: bool = False, **props: Any) -> rx.Component:
    return rx.vstack(
        rx.text(f"{rotulo}{' *' if obrigatorio else ''}", color="#05589F", font_family="Inter", font_size="0.9rem", font_weight="600"),
        rx.input(
            value=value,
            on_change=on_change,
            aria_label=rotulo,
            size="3",
            radius="large",
            color="#05589F",
            font_family="Inter",
            width="100%",
            style={"border": "1px solid #A7D8F0", "boxShadow": "none"},
            **props,
        ),
        spacing="1",
        width="100%",
    )


def campo_select(rotulo: str, opcoes: list[str], value: rx.Var, on_change: Any, obrigatorio: bool = False) -> rx.Component:
    return rx.vstack(
        rx.text(f"{rotulo}{' *' if obrigatorio else ''}", color="#05589F", font_family="Inter", font_size="0.9rem", font_weight="600"),
        rx.select(
            opcoes,
            value=value,
            on_change=on_change,
            aria_label=rotulo,
            size="3",
            radius="large",
            width="100%",
        ),
        spacing="1",
        width="100%",
    )


def modal_cadastro(
    state: type[CadastroState],
    titulo: Any,
    *campos: rx.Component,
    texto_botao: Any = "Salvar",
) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.dialog.title(titulo, color="#05589F", font_family="Poppins", font_size="1.5rem", font_weight="600", margin="0"),
                    rx.dialog.description(
                        "Campos com * são obrigatórios.",
                        color="#6A9ECC",
                        font_family="Inter",
                        font_size="0.9rem",
                    ),
                    *campos,
                    rx.cond(
                        state.erro_form != "",
                        rx.hstack(
                            rx.icon(tag="circle-alert", size=18, color="#ED6D6D", flex_shrink="0"),
                            rx.text(state.erro_form, color="#05589F", font_family="Inter", font_size="0.9rem", font_weight="600"),
                            align="center",
                            spacing="2",
                            width="100%",
                            padding="0.6rem 0.9rem",
                            border_radius="12px",
                            background="rgba(237,109,109,0.15)",
                            role="alert",
                        ),
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancelar",
                            type="button",
                            on_click=state.fechar_modal,
                            disabled=state.salvando,
                            variant="outline",
                            color="#05589F",
                            font_family="Inter",
                            font_weight="600",
                            border_radius="9999px",
                            size="3",
                            style={"boxShadow": "inset 0 0 0 1px #A7D8F0"},
                        ),
                        rx.button(
                            texto_botao,
                            type="submit",
                            loading=state.salvando,
                            background="#05589F",
                            color="#FFFFFF",
                            font_family="Inter",
                            font_weight="600",
                            border_radius="9999px",
                            size="3",
                            _hover={"background": "#4A7A69"},
                        ),
                        justify="end",
                        spacing="3",
                        width="100%",
                        padding_top="0.5rem",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=state.salvar,
                reset_on_submit=False,
            ),
            width="calc(100vw - 2rem)",
            max_width="480px",
            border_radius="20px",
            padding=rx.breakpoints(initial="1.25rem", md="1.75rem"),
            box_sizing="border-box",
        ),
        open=state.modal_aberto,
        on_open_change=state.alterar_modal,
    )


def campo_busca(state: type[CadastroState], placeholder: str) -> rx.Component:
    return rx.hstack(
        rx.icon(tag="search", size=18, color="#6A9ECC"),
        rx.input(
            placeholder=placeholder,
            aria_label=placeholder,
            value=state.search,
            on_change=state.set_search,
            debounce_timeout=400,
            variant="soft",
            border="none",
            outline="none",
            background="transparent",
            color="#05589F",
            font_family="Inter",
            flex="1",
        ),
        width="100%",
        max_width="420px",
        align="center",
        spacing="3",
        padding="0.7rem 1.1rem",
        border="1px solid #A7D8F0",
        border_radius="9999px",
        background="#FFFFFF",
    )


def cabecalho_coluna(rotulo: str, largura: str) -> rx.Component:
    return rx.text(rotulo, width=largura, color="#6A9ECC", font_family="Inter", font_size="0.85rem", font_weight="600")


def celula_responsiva(rotulo: str, conteudo: rx.Component, largura: str) -> rx.Component:
    """Tabela desktop que vira célula identificada em telas estreitas."""
    return rx.vstack(
        rx.text(
            rotulo,
            display=rx.breakpoints(initial="block", md="none"),
            color="#6A9ECC",
            font_family="Inter",
            font_size="0.75rem",
            font_weight="600",
        ),
        conteudo,
        width=rx.breakpoints(initial="48%", md=largura),
        min_width="0",
        align="start",
        spacing="1",
    )


def tela_cadastro(
    state: type[CadastroState],
    *,
    ativo: str,
    titulo: str,
    busca: str,
    botao: str,
    cabecalho: rx.Component,
    linha: Any,
    modal: rx.Component,
    subtitulo: str = "",
    largura_maxima: str = "960px",
) -> rx.Component:
    """Layout comum das telas de cadastro (mesmo visual e escala de Pacientes)."""
    return rx.hstack(
        Sidebar(active=ativo),
        rx.vstack(
            Topbar(),
            rx.vstack(
                rx.heading(titulo, color="#05589F", font_family="Poppins", font_size=rx.breakpoints(initial="1.65rem", md="2.1rem"), font_weight="600"),
                rx.text(subtitulo, color="#6A9ECC", font_family="Inter", font_size="1rem", font_weight="600") if subtitulo else rx.fragment(),
                rx.hstack(
                    campo_busca(state, busca),
                    rx.spacer(),
                    botao_novo(botao, state.abrir_modal),
                    width="100%",
                    align="center",
                    wrap="wrap",
                ),
                spacing="4",
                align="start",
                width="100%",
            ),
            rx.box(
                rx.vstack(
                    cabecalho,
                    corpo_lista(state, linha),
                    spacing="4",
                    width="100%",
                ),
                width="100%",
                padding=rx.breakpoints(initial="1rem", md="1.75rem"),
                border_radius="20px",
                background="#FFFFFF",
                box_shadow="0 8px 24px rgba(5,88,159,0.08)",
                box_sizing="border-box",
            ),
            modal,
            spacing="6",
            align="start",
            width="100%",
            max_width=largura_maxima,
            min_width="0",
            padding=rx.breakpoints(initial="1rem", md="2rem 2.5rem", lg="2.25rem 3rem"),
            box_sizing="border-box",
        ),
        width="100%",
        min_height="100vh",
        background=rx.color_mode_cond("#F8FCFD", "#0B1220"),
        spacing="0",
        align="stretch",
        flex_direction=rx.breakpoints(initial="column", md="row"),
        on_mount=state.carregar_dados,
    )
