from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import csv
from io import StringIO
from typing import Any

import reflex as rx

from ProjetoCl_nicaCardiologia import api
from ProjetoCl_nicaCardiologia.auth import AuthState


MENU_ITEMS = (
    ("Início", "/dashboard", "/home.svg"),
    ("Pacientes", "/pacientes", "/user.svg"),
    ("Agendamentos", "/agendamento", "/calendar.svg"),
    ("Prescrições", "/prescricoes", "/prescription.svg"),
    ("Médicos", "/medicos", "/doctor.svg"),
    ("Convênio", "/convenio", "/card.svg"),
    ("Exames", "/exames", "/exam.svg"),
)

MONTHS = (
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
)
WEEKDAYS = ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")
LIST_KEYS = ("items", "itens", "data", "result", "results", "agendamentos", "pagamentos_pendentes", "faturamento_por_convenio")


def _extrair_lista(data: Any) -> list[Any]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in LIST_KEYS:
            if isinstance(data.get(key), list):
                return data[key]
        for key in ("data", "result", "results"):
            if isinstance(data.get(key), dict):
                try:
                    return _extrair_lista(data[key])
                except api.ApiError:
                    pass
    raise api.ApiError(api.UNEXPECTED_RESPONSE_MESSAGE)


def periodo_datas(data_selecionada: date, visualizacao: str) -> tuple[date, date]:
    if visualizacao == "Semana":
        inicio = data_selecionada - timedelta(days=data_selecionada.weekday())
        return inicio, inicio + timedelta(days=6)
    if visualizacao == "Mês":
        inicio = data_selecionada.replace(day=1)
        proximo_mes = (inicio.replace(day=28) + timedelta(days=4)).replace(day=1)
        return inicio, proximo_mes - timedelta(days=1)
    return data_selecionada, data_selecionada


def timestamp_inicio(data: date) -> int:
    return int(datetime.combine(data, time.min).astimezone().timestamp() * 1000)


def timestamp_fim(data: date) -> int:
    return int(datetime.combine(data + timedelta(days=1), time.min).astimezone().timestamp() * 1000) - 1


def _valor_texto(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("nome", "name", "nome_do_exame", "nome_completo", "email", "titulo"):
            if value.get(key):
                return str(value[key])
        return ""
    if value is None:
        return ""
    return str(value).strip()


def _nome_relacionado(value: Any) -> str:
    """Lê o nome da relação; um número isolado é um ID, não o nome da pessoa."""
    if isinstance(value, dict):
        for key in ("nome", "name", "nome_completo", "patient_name", "titulo"):
            nome = _nome_relacionado(value.get(key))
            if nome:
                return nome
        return ""
    if value is None or isinstance(value, bool):
        return ""
    nome = str(value).strip()
    return "" if nome.isdigit() else nome


def _id_relacao_paciente(item: dict[str, Any]) -> str:
    paciente = item.get("paciente") or item.get("Paciente") or item.get("patient")
    if isinstance(paciente, dict):
        identificador = paciente.get("id") or paciente.get("paciente_id")
        if identificador is not None:
            return str(identificador)
    for key in ("paciente_id", "id_paciente", "patient_id"):
        identificador = item.get(key)
        if identificador is not None and not isinstance(identificador, dict):
            return str(identificador)
    if paciente is not None and not isinstance(paciente, dict):
        bruto = str(paciente).strip()
        return bruto if bruto.isdigit() else ""
    return ""


def _interpretar_data(value: Any) -> datetime | None:
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            # Campos timestamp do Xano são normalmente enviados em milissegundos.
            seconds = value / 1000 if abs(value) > 10_000_000_000 else value
            return datetime.fromtimestamp(seconds).astimezone()
        if isinstance(value, str) and value.strip():
            raw = value.strip()
            if raw.isdigit():
                number = int(raw)
                return _interpretar_data(number)
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return parsed.astimezone() if parsed.tzinfo else parsed.astimezone()
    except (ValueError, OverflowError, OSError):
        return None
    return None


def normalizar_agendamento(
    item: dict[str, Any], pacientes_por_id: dict[str, str] | None = None
) -> dict[str, str]:
    raw_data = item.get("data_hora") or item.get("datahora") or item.get("data") or item.get("inicio") or item.get("start")
    when = _interpretar_data(raw_data)
    hora_avulsa = _valor_texto(item.get("horario") or item.get("hora"))
    if when and hora_avulsa:
        hora = hora_avulsa[:5]
    else:
        hora = when.strftime("%H:%M") if when else (hora_avulsa[:5] or "--:--")
    if when:
        data = f"{when.day} de {MONTHS[when.month - 1]} de {when.year}"
        chave_ordem = when.strftime("%Y-%m-%d %H:%M")
    else:
        data = _valor_texto(item.get("data_formatada") or item.get("data")) or "Data não informada"
        chave_ordem = f"{data} {hora}"

    paciente = (
        _nome_relacionado(item.get("paciente") or item.get("Paciente") or item.get("patient"))
        or _nome_relacionado(item.get("paciente_nome"))
        or _nome_relacionado(item.get("nome_paciente"))
        or _nome_relacionado(item.get("nome"))
        or (pacientes_por_id or {}).get(_id_relacao_paciente(item), "")
        or "Paciente não informado"
    )
    medico = (
        _valor_texto(item.get("medico"))
        or _valor_texto(item.get("medico_nome"))
        or _valor_texto(item.get("nome_medico"))
        or _valor_texto(item.get("profissional"))
        or "Profissional não informado"
    )
    especialidade = _valor_texto(item.get("especialidade") or item.get("exame"))
    detalhe = f"{medico} · {especialidade}" if especialidade else medico
    status = _valor_texto(item.get("status") or item.get("situacao")) or "Agendado"
    return {
        "id": str(item.get("id") or item.get("agendamento_id") or ""),
        "data": data,
        "hora": hora,
        "paciente": paciente,
        "detalhe": detalhe,
        "status": status.replace("_", " ").title(),
        "chave_ordem": chave_ordem,
    }


def normalizar_pagamento_pendente(item: dict[str, Any]) -> dict[str, str]:
    paciente = item.get("paciente") or item.get("Paciente") or {}
    convenio = item.get("convenio") or item.get("Convenio") or {}
    if not isinstance(paciente, dict):
        paciente = {}
    if not isinstance(convenio, dict):
        convenio = {}
    quando = _interpretar_data(item.get("data_hora") or item.get("agendamento_data_hora"))
    forma_original = _valor_texto(item.get("forma_pagamento"))
    formas = {
        "dinheiro": "Dinheiro",
        "cash": "Dinheiro",
        "cartao": "Cartão",
        "card": "Cartão",
        "convenio": "Convênio",
        "insurance": "Convênio",
    }
    forma_normalizada = (
        formas.get(forma_original.casefold().replace("é", "e").replace("ê", "e"), forma_original.title())
        if forma_original
        else ("Convênio" if convenio else "Não informada")
    )
    return {
        "paciente": _nome_relacionado(item.get("paciente_nome") or paciente) or "Paciente não informado",
        "data": quando.strftime("%d/%m/%Y %H:%M") if quando else "Data não informada",
        "forma": forma_normalizada,
        "convenio": _valor_texto(item.get("convenio_nome") or convenio) or "—",
        "status": _valor_texto(item.get("status_pagamento")) or "Pendente",
        "valor_pago": _formatar_moeda_centavos(item.get("valor_pago_centavos", item.get("valor_pago"))),
    }


def _formatar_numero(value: Any) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, bool):
        return "Sim" if value else "Não"
    try:
        numeric = float(value)
        if numeric.is_integer():
            return f"{int(numeric):,}".replace(",", ".")
        inteiro, decimal = f"{numeric:,.2f}".split(".")
        return f"{inteiro.replace(',', '.')},{decimal}"
    except (TypeError, ValueError):
        return str(value)


def _formatar_moeda_centavos(value: Any) -> str:
    """Converte valores inteiros de `valor_pago` (centavos no Xano) para reais pt-BR."""
    if value is None or value == "":
        return "—"
    try:
        reais = (Decimal(str(value)) / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError):
        return str(value)
    inteiro, centavos = f"{reais:,.2f}".split(".")
    return f"{inteiro.replace(',', '.')},{centavos}"


def _formatar_reais(value: Any) -> str:
    """Formata valores decimais do catálogo (já em reais) no padrão pt-BR."""
    if value is None or value == "":
        return "—"
    try:
        reais = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError):
        return str(value)
    inteiro, centavos = f"{reais:,.2f}".split(".")
    return f"{inteiro.replace(',', '.')},{centavos}"


def _somar_pagamentos_centavos(agendamentos: list[dict[str, Any]]) -> Decimal | None:
    """Calcula o faturamento a partir dos pagamentos individuais da agenda (Xano guarda centavos)."""
    total = Decimal("0")
    encontrou_valor = False
    for item in agendamentos:
        valor = _primeiro_valor_definido(item.get("valor_pago"), item.get("valor_pago_centavos"))
        if valor is None:
            continue
        try:
            total += Decimal(str(valor))
            encontrou_valor = True
        except (InvalidOperation, TypeError, ValueError):
            continue
    return total if encontrou_valor else None


def _primeiro_valor_definido(*valores: Any) -> Any:
    return next((valor for valor in valores if valor is not None and valor != ""), None)


def _calcular_repasse_exames(agendamentos: list[dict[str, Any]], exames: list[dict[str, Any]]) -> Decimal | None:
    """Soma o valor em reais do catálogo para cada agendamento que referencia um exame."""
    por_id: dict[str, Decimal] = {}
    por_nome: dict[str, Decimal] = {}
    for exame in exames:
        valor = _primeiro_valor_definido(
            exame.get("valor_do_exame_por_repasse"),
            exame.get("valor"),
            exame.get("valor_repasse"),
        )
        try:
            valor_decimal = Decimal(str(valor))
        except (InvalidOperation, TypeError, ValueError):
            continue
        identificador = exame.get("id") or exame.get("exame_id")
        nome = _valor_texto(exame.get("nome_do_exame") or exame.get("nome") or exame.get("name"))
        if identificador is not None:
            por_id[str(identificador)] = valor_decimal
        if nome:
            por_nome[nome.casefold()] = valor_decimal

    total = Decimal("0")
    encontrou_exame = False
    for agendamento in agendamentos:
        exame = (
            agendamento.get("exame")
            or agendamento.get("exame_id")
            or agendamento.get("id_exame")
            or agendamento.get("exame_nome")
            or agendamento.get("nome_exame")
        )
        identificador = ""
        nome = ""
        valor_embutido: Any = None
        if isinstance(exame, dict):
            identificador = str(exame.get("id") or exame.get("exame_id") or "")
            nome = _valor_texto(exame.get("nome_do_exame") or exame.get("nome") or exame.get("name"))
            valor_embutido = exame.get("valor_do_exame_por_repasse")
        elif exame is not None:
            texto_exame = str(exame).strip()
            if texto_exame.isdigit():
                identificador = texto_exame
            else:
                nome = texto_exame

        valor = None
        if valor_embutido is not None:
            try:
                valor = Decimal(str(valor_embutido))
            except (InvalidOperation, TypeError, ValueError):
                pass
        if valor is None and identificador:
            valor = por_id.get(identificador)
        if valor is None and nome:
            valor = por_nome.get(nome.casefold())
        if valor is not None:
            total += valor
            encontrou_exame = True
    return total if encontrou_exame else None


def _data_legivel(data: date) -> str:
    return f"{WEEKDAYS[data.weekday()]}, {data.day} de {MONTHS[data.month - 1]} de {data.year}"


class DashboardState(rx.State):
    data_atual: str = _data_legivel(date.today())
    filtro_data_inicio: str = date.today().replace(day=1).isoformat()
    filtro_data_fim: str = date.today().isoformat()
    carregando: bool = True
    erro_indicadores: str = ""
    erro_agenda: str = ""
    erro_exames: str = ""
    total_consultas: str = "—"
    total_exames: str = "—"
    total_laudos_enviados: str = "—"
    contador_laudos_disponivel: bool = False
    repasse_exames_periodo: str = "—"
    faturamento_periodo: str = "—"
    novos_pacientes: str = "—"
    faturamento_por_convenio: list[dict[str, str]] = []
    pagamentos_pendentes: list[dict[str, str]] = []
    total_pagamentos_pendentes: str = "—"
    proximos_atendimentos: list[dict[str, str]] = []

    @rx.var
    def convenios_sem_valor(self) -> bool:
        return any(item.get("valor") == "—" for item in self.faturamento_por_convenio)

    @rx.event
    def set_filtro_data_inicio(self, value: str):
        self.filtro_data_inicio = value

    @rx.event
    def set_filtro_data_fim(self, value: str):
        self.filtro_data_fim = value

    def _csv_dashboard(self) -> str:
        inicio = date.fromisoformat(self.filtro_data_inicio)
        fim = date.fromisoformat(self.filtro_data_fim)
        linhas = [
            ["Indicador", "Valor"],
            ["Período inicial", inicio.strftime("%d/%m/%Y")],
            ["Período final", fim.strftime("%d/%m/%Y")],
            ["Consultas no período", self.total_consultas],
            ["Exames no período", self.total_exames],
            ["Laudos enviados no período", self.total_laudos_enviados],
            ["Faturamento do período", self.faturamento_periodo],
            ["Novos pacientes no período", self.novos_pacientes],
            ["Repasse de exames no período", self.repasse_exames_periodo],
            ["Pagamentos pendentes no período", self.total_pagamentos_pendentes],
        ]
        linhas.extend(
            [f"Faturamento por convênio — {item['nome']}", item["valor"]]
            for item in self.faturamento_por_convenio
        )
        linhas.extend(
            [
                f"Pagamento pendente — {item['paciente']}",
                f"{item['data']}; forma: {item['forma']}; convênio: {item['convenio']}; valor já registrado: R$ {item['valor_pago']}",
            ]
            for item in self.pagamentos_pendentes
        )
        arquivo = StringIO(newline="")
        arquivo.write("\ufeff")
        csv.writer(arquivo, delimiter=";", lineterminator="\r\n").writerows(linhas)
        return arquivo.getvalue()

    @rx.event
    def exportar_csv(self):
        try:
            inicio = date.fromisoformat(self.filtro_data_inicio)
            fim = date.fromisoformat(self.filtro_data_fim)
        except ValueError:
            return rx.toast.error("Selecione um período válido antes de exportar.", position="top-center")
        if fim < inicio:
            return rx.toast.error("A data final precisa ser igual ou posterior à data inicial.", position="top-center")
        return rx.download(
            data=self._csv_dashboard(),
            filename=f"dashboard-{inicio.isoformat()}-a-{fim.isoformat()}.csv",
            mime_type="text/csv;charset=utf-8",
        )

    @rx.event
    async def carregar_dados(self):
        self.carregando = True
        self.erro_indicadores = ""
        self.erro_agenda = ""
        self.erro_exames = ""
        self.repasse_exames_periodo = "—"
        self.pagamentos_pendentes = []
        self.total_pagamentos_pendentes = "—"
        try:
            inicio_periodo = date.fromisoformat(self.filtro_data_inicio)
            fim_periodo = date.fromisoformat(self.filtro_data_fim)
        except ValueError:
            self.carregando = False
            self.erro_indicadores = "Informe as datas inicial e final do período."
            return
        if fim_periodo < inicio_periodo:
            self.carregando = False
            self.erro_indicadores = "A data final precisa ser igual ou posterior à data inicial."
            return
        self.data_atual = f"Indicadores de {inicio_periodo.strftime('%d/%m/%Y')} a {fim_periodo.strftime('%d/%m/%Y')}"
        yield

        token = (await self.get_state(AuthState)).obter_token()
        if not token:
            self.carregando = False
            yield AuthState.sessao_expirada
            return

        try:
            dados = await api.request(
                "GET",
                "/dashboard",
                token=token,
                params={
                    "data_inicio": timestamp_inicio(inicio_periodo),
                    "data_fim": timestamp_fim(fim_periodo),
                },
            )
            if not isinstance(dados, dict):
                raise api.ApiError(api.UNEXPECTED_RESPONSE_MESSAGE)
            self.total_consultas = _formatar_numero(dados.get("total_consultas"))
            self.total_exames = _formatar_numero(dados.get("total_exames"))
            total_laudos = dados.get("total_laudos_enviados")
            self.contador_laudos_disponivel = total_laudos is not None
            self.total_laudos_enviados = _formatar_numero(total_laudos)
            valor_faturamento = _formatar_moeda_centavos(
                dados.get("faturamento_periodo", dados.get("faturamento_dia"))
            )
            self.faturamento_periodo = f"R$ {valor_faturamento}" if valor_faturamento != "—" else "—"
            valor_repasse = dados.get("repasse_exames_periodo")
            self.repasse_exames_periodo = _formatar_reais(valor_repasse) if valor_repasse is not None else "—"
            self.novos_pacientes = _formatar_numero(dados.get("novos_pacientes"))
            total_pendentes = dados.get("total_pagamentos_pendentes")
            self.total_pagamentos_pendentes = _formatar_numero(total_pendentes)
            pendentes = dados.get("pagamentos_pendentes") or []
            if isinstance(pendentes, dict):
                pendentes = _extrair_lista(pendentes)
            self.pagamentos_pendentes = [
                normalizar_pagamento_pendente(item)
                for item in pendentes
                if isinstance(item, dict)
            ] if isinstance(pendentes, list) else []
            convenios = dados.get("faturamento_por_convenio") or []
            self.faturamento_por_convenio = [
                {
                    "nome": _valor_texto(item.get("convenio") or item.get("nome") or item.get("convenio_nome")) or "Convênio",
                    "valor": _formatar_moeda_centavos(
                        _primeiro_valor_definido(item.get("faturamento"), item.get("valor"), item.get("total"))
                    ),
                }
                for item in convenios
                if isinstance(item, dict)
            ] if isinstance(convenios, list) else []
        except api.SessionExpired:
            self.carregando = False
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.erro_indicadores = error.message
            self.total_consultas = self.total_exames = self.total_laudos_enviados = self.faturamento_periodo = self.novos_pacientes = "—"
            self.contador_laudos_disponivel = False
            self.faturamento_por_convenio = []
            self.pagamentos_pendentes = []
            self.total_pagamentos_pendentes = "—"

        try:
            data = await api.request(
                "GET",
                "/agendamento",
                token=token,
                params={"data_inicio": timestamp_inicio(date.today()), "data_fim": timestamp_fim(date.today())},
            )
            itens = _extrair_lista(data)
            normalized = [normalizar_agendamento(item) for item in itens if isinstance(item, dict)]
            self.proximos_atendimentos = sorted(normalized, key=lambda item: item["chave_ordem"])[:6]
        except api.SessionExpired:
            self.carregando = False
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.erro_agenda = error.message
            self.proximos_atendimentos = []
            self.repasse_exames_periodo = "—"

        self.carregando = False


def Sidebar(active: str = "Início") -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.image(src="/bi_heart-pulse.svg", alt="Logo CardioVida", width="42px", height="42px"),
            rx.heading("CardioVida", font_family="Poppins", font_size="1.35rem", color=rx.color_mode_cond("#05589F", "#9BD8FF")),
            spacing="2",
            align="center",
            padding_bottom=rx.breakpoints(initial="1rem", md="2rem"),
        ),
        rx.vstack(
            *[
                rx.cond(
                    AuthState.rotas_permitidas.contains(href),
                    rx.link(
                        rx.hstack(
                            rx.image(src=icon, alt="", width="22px", height="22px"),
                            rx.text(label, font_family="Inter", font_size="0.95rem", font_weight="600"),
                            spacing="3",
                            align="center",
                        ),
                        href=href,
                        color=rx.color_mode_cond("#05589F", "#9BD8FF"),
                        width=rx.breakpoints(initial="auto", md="100%"),
                        padding="0.75rem 1rem",
                        border_radius="12px",
                        background=rx.color_mode_cond("#A7D8F0" if label == active else "transparent", "#1D3B53" if label == active else "transparent"),
                        _hover={"background": rx.color_mode_cond("rgba(167,216,240,0.55)", "#22364A")},
                    ),
                )
                for label, href, icon in MENU_ITEMS
            ],
            spacing="2",
            width="100%",
            flex_direction=rx.breakpoints(initial="row", md="column"),
            flex_wrap=rx.breakpoints(initial="wrap", md="nowrap"),
        ),
        rx.spacer(),
        rx.el.button(
            rx.hstack(
                rx.icon(tag="log-out", size=22),
                rx.text("Sair", font_family="Inter", font_size="0.95rem", font_weight="600"),
                spacing="3",
                align="center",
            ),
            type="button",
            aria_label="Sair",
            on_click=AuthState.sair,
            style={
                "width": "100%",
                "padding": "0.75rem 1rem",
                "border": "none",
                "borderRadius": "12px",
                "background": "transparent",
                "color": rx.color_mode_cond("#05589F", "#9BD8FF"),
                "cursor": "pointer",
                "textAlign": "left",
                "&:hover": {"background": rx.color_mode_cond("rgba(167,216,240,0.4)", "#22364A")},
            },
        ),
        rx.text("CardioVida", color="#6A9ECC", font_family="Inter", font_size="0.75rem"),
        width=rx.breakpoints(initial="100%", md="250px"),
        height=rx.breakpoints(initial="auto", md="100vh"),
        min_height=rx.breakpoints(initial="auto", md="100vh"),
        position=rx.breakpoints(initial="relative", md="sticky"),
        top="0",
        align_self="flex-start",
        overflow_y="auto",
        flex_shrink="0",
        padding=rx.breakpoints(initial="1rem", md="2rem 1.25rem 1.25rem"),
        background=rx.color_mode_cond("rgba(167,216,240,0.57)", "#111C29"),
        align="stretch",
        spacing="3",
    )


def Topbar() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text("CardioVida", color=rx.color_mode_cond("#05589F", "#9BD8FF"), font_family="Poppins", font_size="1.1rem", font_weight="600"),
            rx.text("Gestão da clínica", color=rx.color_mode_cond("#6A9ECC", "#B8C7D6"), font_family="Inter", font_size="0.8rem"),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.button(
            rx.color_mode_cond("Tema escuro", "Tema claro"),
            on_click=rx.toggle_color_mode,
            aria_label="Alternar tema claro ou escuro",
            size="2",
            variant="soft",
            color_scheme="blue",
            border_radius="9999px",
            flex_shrink="0",
        ),
        rx.hstack(
            rx.image(src="/user.svg", alt="Perfil", width="26px", height="26px"),
            rx.text(
                AuthState.user_display_name,
                font_family="Inter",
                color=rx.color_mode_cond("#05589F", "#9BD8FF"),
                font_weight="600",
                max_width=rx.breakpoints(initial="125px", md="220px"),
                overflow="hidden",
                text_overflow="ellipsis",
                white_space="nowrap",
            ),
            spacing="2",
            align="center",
        ),
        width="100%",
        padding="0.8rem 1.1rem",
        border=rx.color_mode_cond("1px solid #E6F2F7", "1px solid #334155"),
        border_radius="22px",
        background=rx.color_mode_cond("#FFFFFF", "#182433"),
        box_shadow="0 4px 16px rgba(5,88,159,0.06)",
        align="center",
        spacing=rx.breakpoints(initial="2", md="4"),
        box_sizing="border-box",
    )


def status_badge(status: str) -> rx.Component:
    status_normalizado = status.lower()
    confirmado = (
        status_normalizado.contains("confirm")
        | status_normalizado.contains("realiz")
        | status_normalizado.contains("conclu")
    )
    return rx.text(
        status,
        color=rx.cond(confirmado, "#34785F", "#6A7800"),
        background=rx.cond(confirmado, "rgba(136,224,193,0.3)", "rgba(220,237,109,0.55)"),
        padding="0.3rem 0.7rem",
        border_radius="9999px",
        font_family="Inter",
        font_size="0.75rem",
        font_weight="600",
        white_space="nowrap",
    )


def appointment_row(appointment: rx.Var[dict[str, str]]) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(appointment["hora"], color="#05589F", font_family="Inter", font_weight="600"),
            rx.text(appointment["data"], color="#6A9ECC", font_family="Inter", font_size="0.72rem"),
            spacing="0",
            align="start",
            min_width="110px",
        ),
        rx.vstack(
            rx.text(appointment["paciente"], color="#05589F", font_family="Inter", font_weight="600"),
            rx.text(appointment["detalhe"], color="#6A9ECC", font_family="Inter", font_size="0.85rem"),
            spacing="1",
            align="start",
            min_width="0",
        ),
        rx.spacer(),
        status_badge(appointment["status"]),
        width="100%",
        padding="0.85rem 0",
        border_bottom="1px solid #E6F2F7",
        align="center",
        spacing="3",
        flex_wrap=rx.breakpoints(initial="wrap", md="nowrap"),
    )


def pending_payment_row(item: rx.Var[dict[str, str]]) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(item["paciente"], color="#05589F", font_family="Inter", font_weight="600"),
            rx.text(item["data"], color="#6A9ECC", font_family="Inter", font_size="0.8rem"),
            spacing="1",
            align="start",
            min_width="0",
            flex="1",
        ),
        rx.vstack(
            rx.text("Forma: " + item["forma"], color="#38566B", font_family="Inter", font_weight="600"),
            rx.text("Convênio: " + item["convenio"], color="#6A9ECC", font_family="Inter", font_size="0.8rem"),
            spacing="1",
            align="start",
            min_width="140px",
        ),
        rx.vstack(
            rx.text(item["status"], color="#7A4D00", font_family="Inter", font_weight="600"),
            rx.text("Valor já pago: R$ " + item["valor_pago"], color="#6A9ECC", font_family="Inter", font_size="0.8rem"),
            spacing="1",
            align="end",
            min_width="130px",
        ),
        width="100%",
        padding="0.8rem 0",
        border_bottom="1px solid #E6F2F7",
        align="center",
        spacing="3",
        flex_wrap=rx.breakpoints(initial="wrap", md="nowrap"),
    )


def metric_card(title: str, value: rx.Var[str], color: str, icon: str) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(title, color="#4A7A69", font_family="Inter", font_size="0.9rem", font_weight="600"),
            rx.heading(value, color="#05589F", font_family="Poppins", font_size="2.25rem", line_height="1"),
            spacing="2",
            align="start",
        ),
        rx.spacer(),
        rx.icon(tag=icon, size=24, color="#05589F"),
        width="100%",
        align="center",
        padding="1.25rem",
        border_radius="18px",
        background=color,
        min_width="0",
    )


def dashboard() -> rx.Component:
    return rx.hstack(
        Sidebar(active="Início"),
        rx.vstack(
            Topbar(),
            rx.vstack(
                rx.text(DashboardState.data_atual, color="#6A9ECC", font_family="Inter", font_size="0.9rem", font_weight="600"),
                rx.heading(
                    rx.cond(AuthState.user_display_name != "Usuário", "Olá, " + AuthState.user_display_name, "Olá"),
                    color="#05589F",
                    font_family="Poppins",
                    font_size=rx.breakpoints(initial="1.65rem", md="2.1rem"),
                    font_weight="600",
                ),
                rx.text("Resumo atualizado com os dados da clínica", color="#6A9ECC", font_family="Inter", font_size="1rem", font_weight="600"),
                spacing="2",
                align="start",
                width="100%",
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("Data inicial", color="#38566B", font_family="Inter", font_weight="600"),
                    rx.input(
                        type="date",
                        value=DashboardState.filtro_data_inicio,
                        on_change=DashboardState.set_filtro_data_inicio,
                        aria_label="Data inicial dos indicadores",
                    ),
                    spacing="1",
                    align="start",
                    min_width=rx.breakpoints(initial="100%", sm="190px"),
                ),
                rx.vstack(
                    rx.text("Data final", color="#38566B", font_family="Inter", font_weight="600"),
                    rx.input(
                        type="date",
                        value=DashboardState.filtro_data_fim,
                        on_change=DashboardState.set_filtro_data_fim,
                        aria_label="Data final dos indicadores",
                    ),
                    spacing="1",
                    align="start",
                    min_width=rx.breakpoints(initial="100%", sm="190px"),
                ),
                rx.button(
                    "Aplicar período",
                    on_click=DashboardState.carregar_dados,
                    loading=DashboardState.carregando,
                    color_scheme="blue",
                    border_radius="9999px",
                ),
                rx.button(
                    "Exportar CSV",
                    on_click=DashboardState.exportar_csv,
                    variant="outline",
                    color_scheme="blue",
                    border_radius="9999px",
                ),
                width="100%",
                padding="1rem",
                border="1px solid #E6F2F7",
                border_radius="16px",
                background=rx.color_mode_cond("#FFFFFF", "#182433"),
                align=rx.breakpoints(initial="stretch", sm="end"),
                flex_wrap="wrap",
                spacing="3",
                box_sizing="border-box",
            ),
            rx.cond(
                DashboardState.erro_indicadores != "",
                rx.callout(DashboardState.erro_indicadores, icon="triangle_alert", color_scheme="red", width="100%"),
            ),
            rx.cond(
                DashboardState.erro_agenda != "",
                rx.callout("Não foi possível carregar os atendimentos de hoje: " + DashboardState.erro_agenda, icon="triangle_alert", color_scheme="red", width="100%"),
            ),
            rx.cond(
                DashboardState.erro_exames != "",
                rx.callout(DashboardState.erro_exames, icon="triangle_alert", color_scheme="red", width="100%"),
            ),
            rx.grid(
                metric_card("Consultas no período", DashboardState.total_consultas, "rgba(136,224,193,0.3)", "stethoscope"),
                metric_card("Exames no período", DashboardState.total_exames, "rgba(167,216,240,0.42)", "activity"),
                metric_card("Faturamento do período", DashboardState.faturamento_periodo, "rgba(220,237,109,0.35)", "banknote"),
                metric_card("Novos pacientes no período", DashboardState.novos_pacientes, "rgba(106,158,204,0.2)", "users"),
                rx.cond(
                    AuthState.perfil == "administrador",
                    metric_card("Laudos enviados no período", DashboardState.total_laudos_enviados, "rgba(136,224,193,0.3)", "file-check-2"),
                ),
                metric_card(
                    "Repasse de exames no período",
                    rx.cond(DashboardState.repasse_exames_periodo == "—", "—", "R$ " + DashboardState.repasse_exames_periodo),
                    "rgba(136,224,193,0.3)",
                    "activity",
                ),
                columns=rx.breakpoints(initial="1", sm="2", lg="3", xl="5"),
                spacing="4",
                width="100%",
            ),
            rx.cond(
                (AuthState.perfil == "administrador") & (DashboardState.contador_laudos_disponivel == False),
                rx.callout(
                    "O Xano ainda não retorna a contagem de laudos enviados. Inclua total_laudos_enviados em GET /dashboard.",
                    icon="info",
                    color_scheme="blue",
                    width="100%",
                ),
            ),
            rx.cond(
                DashboardState.faturamento_por_convenio.length() > 0,
                rx.vstack(
                    rx.heading("Faturamento por convênio", color="#05589F", font_family="Poppins", font_size="1.2rem"),
                    rx.cond(
                        DashboardState.convenios_sem_valor,
                        rx.box(
                            rx.text(
                                "O Xano retornou os nomes dos convênios sem os valores. Para contabilizar, GET /dashboard precisa devolver a soma de Agendamento.valor_pago agrupada por convenio_id.",
                                color="#7A2E0E",
                                font_family="Inter",
                                font_weight="600",
                                line_height="1.5",
                            ),
                            width="100%",
                            padding="0.75rem 1rem",
                            border="1px solid #D97706",
                            border_radius="12px",
                            background="#FFFAEB",
                            box_sizing="border-box",
                        ),
                    ),
                    rx.foreach(
                        DashboardState.faturamento_por_convenio,
                        lambda item: rx.hstack(
                            rx.text(item["nome"], color="#05589F", font_family="Inter", font_weight="600"),
                            rx.spacer(),
                            rx.text(
                                rx.cond(item["valor"] == "—", "Valor não retornado", "R$ " + item["valor"]),
                                color=rx.cond(item["valor"] == "—", "#7A2E0E", "#216E4E"),
                                font_family="Inter",
                                font_weight="600",
                            ),
                            width="100%",
                            padding_y="0.5rem",
                            border_bottom="1px solid #E6F2F7",
                        ),
                    ),
                    width="100%",
                    padding="1.25rem",
                    border_radius="18px",
                    background="#FFFFFF",
                    box_shadow="0 8px 24px rgba(5,88,159,0.08)",
                ),
            ),
            rx.cond(
                AuthState.perfil == "administrador",
                rx.vstack(
                    rx.hstack(
                        rx.heading("Pagamentos pendentes", color="#05589F", font_family="Poppins", font_size="1.2rem"),
                        rx.spacer(),
                        rx.text(DashboardState.total_pagamentos_pendentes + " no período", color="#6A9ECC", font_family="Inter", font_weight="600"),
                        width="100%",
                        align="center",
                        flex_wrap="wrap",
                    ),
                    rx.text("Pacientes com pagamento pendente e forma informada no agendamento.", color="#6A9ECC", font_family="Inter", font_size="0.9rem"),
                    rx.cond(
                        DashboardState.pagamentos_pendentes.length() > 0,
                        rx.vstack(rx.foreach(DashboardState.pagamentos_pendentes, pending_payment_row), width="100%", spacing="0"),
                        rx.text("Não há pagamentos pendentes neste período.", color="#6A9ECC", padding_y="1rem"),
                    ),
                    width="100%",
                    padding="1.25rem",
                    border_radius="18px",
                    background=rx.color_mode_cond("#FFFFFF", "#182433"),
                    box_shadow="0 8px 24px rgba(5,88,159,0.08)",
                ),
            ),
            rx.vstack(
                rx.hstack(
                    rx.heading("Atendimentos de hoje", color="#05589F", font_family="Poppins", font_size="1.25rem"),
                    rx.spacer(),
                    rx.link("Abrir agenda", href="/agendamento", color="#34785F", font_family="Inter", font_weight="600", text_decoration="underline"),
                    width="100%",
                    align="center",
                ),
                rx.cond(
                    DashboardState.carregando,
                    rx.text("Carregando dados da clínica...", color="#6A9ECC", padding_y="1rem"),
                    rx.cond(
                        DashboardState.proximos_atendimentos.length() > 0,
                        rx.vstack(rx.foreach(DashboardState.proximos_atendimentos, appointment_row), width="100%", spacing="0"),
                        rx.text("Não há atendimentos cadastrados para hoje.", color="#6A9ECC", padding_y="1rem"),
                    ),
                ),
                width="100%",
                padding="1.5rem",
                border_radius="20px",
                background="#FFFFFF",
                box_shadow="0 8px 24px rgba(5,88,159,0.08)",
            ),
            spacing="5",
            align="start",
            width="100%",
            max_width="1200px",
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
        on_mount=DashboardState.carregar_dados,
    )
