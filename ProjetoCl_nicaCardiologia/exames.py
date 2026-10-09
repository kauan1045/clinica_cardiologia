from typing import Any, ClassVar

import reflex as rx

from ProjetoCl_nicaCardiologia import api
from ProjetoCl_nicaCardiologia.auth import AuthState
from ProjetoCl_nicaCardiologia.cadastros import (
    CadastroState,
    celula_responsiva,
    cabecalho_coluna,
    campo,
    campo_input,
    campo_select,
    converter_numero,
    formatar_valor,
    mensagem_erro,
    modal_cadastro,
    numero_json,
    tela_cadastro,
    texto,
)


STATUS_EXAME = ["Ativo", "Inativo"]


class ExamesState(CadastroState, rx.State):
    ENDPOINT: ClassVar[str] = "/exame"
    NOME_LISTA: ClassVar[str] = "os exames"
    VAZIO: ClassVar[str] = "Nenhum exame cadastrado"
    VAZIO_BUSCA: ClassVar[str] = "Nenhum exame encontrado para a busca"

    form_nome: str = ""
    form_tipo: str = ""
    form_valor: str = ""
    form_duracao_minutos: str = ""
    form_prazo_resultado_dias: str = ""
    form_status: str = "Ativo"
    editando_id: str = ""

    @rx.event
    def set_form_nome(self, value: str):
        self.form_nome = value

    @rx.event
    def set_form_tipo(self, value: str):
        self.form_tipo = value

    @rx.event
    def set_form_valor(self, value: str):
        self.form_valor = value

    @rx.event
    def set_form_duracao_minutos(self, value: str):
        self.form_duracao_minutos = value

    @rx.event
    def set_form_prazo_resultado_dias(self, value: str):
        self.form_prazo_resultado_dias = value

    @rx.event
    def set_form_status(self, value: str):
        self.form_status = value

    def _normalizar(self, item: dict[str, Any]) -> dict[str, str]:
        status = texto(campo(item, "status", "Status"))
        return {
            "id": texto(campo(item, "id", "exame_id")),
            "nome": texto(campo(item, "nome_do_exame", "nome", "name")),
            "tipo": texto(campo(item, "tipo_exame", "tipo", "type")),
            "valor": formatar_valor(campo(item, "valor_do_exame_por_repasse", "valor", "valor_repasse")),
            "duracao": texto(campo(item, "duracao_minutos", "duracao", "tempo_minutos")),
            "prazo_resultado": texto(campo(item, "prazo_resultado_dias", "prazo_resultado", "tempo_resultado_dias")),
            "status": status[:1].upper() + status[1:].lower(),
        }

    def _validar(self) -> tuple[dict[str, Any] | None, str]:
        nome = self.form_nome.strip()
        tipo = self.form_tipo.strip()
        if (
            not nome
            or not tipo
            or not self.form_valor.strip()
            or not self.form_duracao_minutos.strip()
            or not self.form_prazo_resultado_dias.strip()
        ):
            return None, "Preencha nome do exame, tipo, valor de repasse, duração e prazo do resultado."
        valor = converter_numero(self.form_valor)
        if valor is None or valor < 0:
            return None, "Informe um valor de repasse válido (ex.: 150,00)."
        try:
            duracao_minutos = int(self.form_duracao_minutos)
        except ValueError:
            return None, "Informe a duração em minutos usando um número inteiro."
        if not 1 <= duracao_minutos <= 1440:
            return None, "A duração do exame deve ficar entre 1 e 1440 minutos."
        try:
            prazo_resultado_dias = int(self.form_prazo_resultado_dias)
        except ValueError:
            return None, "Informe o prazo do resultado em dias inteiros."
        if not 1 <= prazo_resultado_dias <= 365:
            return None, "O prazo do resultado deve ficar entre 1 e 365 dias."
        if self.form_status not in STATUS_EXAME:
            return None, "Selecione o status do exame."
        payload = {
            "nome_do_exame": nome,
            "tipo_exame": tipo,
            "valor_do_exame_por_repasse": numero_json(valor),
            "duracao_minutos": duracao_minutos,
            "prazo_resultado_dias": prazo_resultado_dias,
            "status": self.form_status,
        }
        return payload, ""

    def _limpar_formulario(self) -> None:
        self.editando_id = ""
        self.form_nome = ""
        self.form_tipo = ""
        self.form_valor = ""
        self.form_duracao_minutos = ""
        self.form_prazo_resultado_dias = ""
        self.form_status = "Ativo"

    @rx.event
    def editar(self, exame_id: str):
        exame = next((item for item in self.itens if item.get("id") == exame_id), None)
        if exame is None:
            self.erro_lista = "Não encontrei esse exame na lista. Atualize a página e tente novamente."
            return
        self.editando_id = exame_id
        self.form_nome = exame.get("nome", "")
        self.form_tipo = exame.get("tipo", "")
        self.form_valor = exame.get("valor", "")
        self.form_duracao_minutos = exame.get("duracao", "")
        self.form_prazo_resultado_dias = exame.get("prazo_resultado", "")
        self.form_status = exame.get("status", "Ativo") or "Ativo"
        self.erro_form = ""
        self.modal_aberto = True

    @rx.event
    async def salvar(self, form_data: dict[str, Any]):
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
        metodo = "PUT" if self.editando_id else "POST"
        endpoint = f"/exame/{int(self.editando_id)}" if self.editando_id else self.ENDPOINT
        try:
            await api.request(metodo, endpoint, token=token, json=payload)
        except api.SessionExpired:
            self.salvando = False
            self.modal_aberto = False
            yield AuthState.sessao_expirada
            return
        except (ValueError, api.ApiError) as error:
            self.salvando = False
            if isinstance(error, api.ApiError):
                self.erro_form = mensagem_erro(error, "atualizar" if self.editando_id else "cadastrar")
            else:
                self.erro_form = "O ID do exame não é válido. Atualize a lista e tente novamente."
            return

        atualizando = bool(self.editando_id)
        self.salvando = False
        self.modal_aberto = False
        self._limpar_formulario()
        self.carregando = True
        yield rx.toast.success(
            "Exame atualizado com sucesso." if atualizando else "Exame cadastrado com sucesso.",
            position="top-center",
        )
        evento = await self._buscar()
        if evento:
            yield evento


def exame_status_badge(status: rx.Var[str]) -> rx.Component:
    return rx.text(
        status,
        color="#05589F",
        background=rx.match(
            status,
            ("Ativo", "rgba(136,224,193,0.3)"),
            ("Inativo", "rgba(154,164,178,0.25)"),
            "rgba(154,164,178,0.25)",
        ),
        padding="0.3rem 0.9rem",
        border_radius="9999px",
        font_family="Inter",
        font_size="0.8rem",
        font_weight="600",
        width="fit-content",
    )


def exames_table_header() -> rx.Component:
    return rx.hstack(
        cabecalho_coluna("Nome do exame", "20%"),
        cabecalho_coluna("Tipo", "15%"),
        cabecalho_coluna("Valor de repasse (R$)", "15%"),
        cabecalho_coluna("Duração", "10%"),
        cabecalho_coluna("Prazo do resultado", "13%"),
        cabecalho_coluna("Status", "15%"),
        cabecalho_coluna("Ações", "12%"),
        width="100%",
        padding="0 0.5rem 0.75rem",
        display=rx.breakpoints(initial="none", md="flex"),
        border_bottom="1px solid #E6F2F7",
        box_sizing="border-box",
    )


def exame_row(exame: rx.Var[dict[str, str]]) -> rx.Component:
    return rx.hstack(
        celula_responsiva("Nome do exame", rx.text(exame["nome"], color="#05589F", font_family="Inter", font_weight="600"), "20%"),
        celula_responsiva("Tipo", rx.text(exame["tipo"], color="#38566B", font_family="Inter", font_size="0.9rem"), "15%"),
        celula_responsiva("Valor de repasse (R$)", rx.text(exame["valor"], color="#38566B", font_family="Inter", font_size="0.9rem"), "15%"),
        celula_responsiva("Duração", rx.text(rx.cond(exame["duracao"] != "", exame["duracao"] + " min", "—"), color="#38566B", font_family="Inter", font_size="0.9rem"), "10%"),
        celula_responsiva("Prazo do resultado", rx.text(rx.cond(exame["prazo_resultado"] != "", exame["prazo_resultado"] + " dias", "—"), color="#38566B", font_family="Inter", font_size="0.9rem"), "13%"),
        celula_responsiva(
            "Status",
            rx.box(
                rx.cond(
                    exame["status"] != "",
                    exame_status_badge(exame["status"]),
                    rx.text("—", color="#38566B", font_family="Inter", font_size="0.9rem"),
                ),
            ),
            "15%",
        ),
        celula_responsiva(
            "Ações",
            rx.button(
                "Editar",
                on_click=ExamesState.editar(exame["id"]),
                variant="outline",
                color="#05589F",
                border_radius="9999px",
                size="2",
                disabled=exame["id"] == "",
            ),
            "12%",
        ),
        width="100%",
        padding="0.85rem 0.5rem",
        align="start",
        flex_wrap=rx.breakpoints(initial="wrap", md="nowrap"),
        spacing=rx.breakpoints(initial="2", md="0"),
        border_bottom="1px solid #EEF4F7",
        box_sizing="border-box",
    )


def novo_exame_modal() -> rx.Component:
    return modal_cadastro(
        ExamesState,
        rx.cond(ExamesState.editando_id != "", "Editar Exame", "Novo Exame"),
        campo_input("Nome do exame", ExamesState.form_nome, ExamesState.set_form_nome, obrigatorio=True, placeholder="Ex.: Ecocardiograma"),
        campo_input("Tipo", ExamesState.form_tipo, ExamesState.set_form_tipo, obrigatorio=True, placeholder="Ex.: Imagem"),
        campo_input(
            "Valor de repasse (R$)",
            ExamesState.form_valor,
            ExamesState.set_form_valor,
            obrigatorio=True,
            placeholder="0,00",
            input_mode="decimal",
        ),
        campo_input(
            "Duração do exame (minutos)",
            ExamesState.form_duracao_minutos,
            ExamesState.set_form_duracao_minutos,
            obrigatorio=True,
            placeholder="Ex.: 30",
            input_mode="numeric",
        ),
        campo_input(
            "Prazo para resultado (dias corridos)",
            ExamesState.form_prazo_resultado_dias,
            ExamesState.set_form_prazo_resultado_dias,
            obrigatorio=True,
            placeholder="Ex.: 7",
            input_mode="numeric",
        ),
        campo_select("Status", STATUS_EXAME, ExamesState.form_status, ExamesState.set_form_status, obrigatorio=True),
        texto_botao=rx.cond(ExamesState.editando_id != "", "Atualizar exame", "Salvar exame"),
    )


def exames() -> rx.Component:
    return tela_cadastro(
        ExamesState,
        ativo="Exames",
        titulo="Catálogo de Exames",
        subtitulo="Exames oferecidos pela clínica e valores de repasse.",
        busca="Buscar exame",
        botao="+ Novo Exame",
        cabecalho=exames_table_header(),
        linha=exame_row,
        modal=novo_exame_modal(),
    )
