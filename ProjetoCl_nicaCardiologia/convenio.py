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
    converter_numero,
    formatar_percentual,
    mensagem_erro,
    modal_cadastro,
    numero_json,
    tela_cadastro,
    texto,
)


class ConvenioState(CadastroState, rx.State):
    ENDPOINT: ClassVar[str] = "/convenio"
    NOME_LISTA: ClassVar[str] = "os convênios"
    VAZIO: ClassVar[str] = "Nenhum convênio cadastrado"
    VAZIO_BUSCA: ClassVar[str] = "Nenhum convênio encontrado para a busca"

    form_nome: str = ""
    form_codigo: str = ""
    form_desconto: str = ""
    editando_id: str = ""
    convenio_remocao_id: str = ""
    removendo_convenio: bool = False
    erro_remocao: str = ""

    @rx.event
    def set_form_nome(self, value: str):
        self.form_nome = value

    @rx.event
    def set_form_codigo(self, value: str):
        self.form_codigo = value

    @rx.event
    def set_form_desconto(self, value: str):
        self.form_desconto = value

    def _normalizar(self, item: dict[str, Any]) -> dict[str, str]:
        # O código é texto: zeros à esquerda são preservados.
        return {
            "id": texto(campo(item, "id", "convenio_id")),
            "name": texto(campo(item, "nome", "name")),
            "codigo": texto(campo(item, "codigo", "código", "code")),
            "desconto": formatar_percentual(campo(item, "desconto", "discount")),
        }

    def _validar(self) -> tuple[dict[str, Any] | None, str]:
        nome = self.form_nome.strip()
        codigo = self.form_codigo.strip()
        if not nome or not codigo or not self.form_desconto.strip():
            return None, "Preencha nome, código e desconto."
        desconto = converter_numero(self.form_desconto)
        if desconto is None or not 0 <= desconto <= 100:
            return None, "Informe um desconto entre 0 e 100%."
        return {"nome": nome, "codigo": codigo, "desconto": numero_json(desconto)}, ""

    def _limpar_formulario(self) -> None:
        self.editando_id = ""
        self.form_nome = ""
        self.form_codigo = ""
        self.form_desconto = ""

    @rx.event
    def editar(self, convenio_id: str):
        convenio = next((item for item in self.itens if item.get("id") == convenio_id), None)
        if convenio is None:
            self.erro_lista = "Não encontrei esse convênio na lista. Atualize a página e tente novamente."
            return
        self.editando_id = convenio_id
        self.form_nome = convenio.get("name", "")
        self.form_codigo = convenio.get("codigo", "")
        self.form_desconto = convenio.get("desconto", "").replace("%", "")
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
        atualizando = bool(self.editando_id)
        if atualizando:
            try:
                payload["convenio_id"] = str(int(self.editando_id))
            except ValueError:
                self.erro_form = "O ID do convênio não é válido. Atualize a lista e tente novamente."
                return
        self.salvando = True
        self.erro_form = ""
        yield
        token = (await self.get_state(AuthState)).obter_token()
        try:
            await api.request(
                "PATCH" if atualizando else "POST",
                self.ENDPOINT,
                token=token,
                json=payload,
            )
        except api.SessionExpired:
            self.salvando = False
            self.modal_aberto = False
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.salvando = False
            self.erro_form = mensagem_erro(error, "atualizar" if atualizando else "cadastrar")
            return
        self.salvando = False
        self.modal_aberto = False
        self._limpar_formulario()
        self.carregando = True
        yield rx.toast.success("Convênio atualizado com sucesso." if atualizando else "Convênio cadastrado com sucesso.", position="top-center")
        evento = await self._buscar()
        if evento:
            yield evento

    @rx.event
    def solicitar_remocao(self, convenio_id: str):
        if convenio_id:
            self.convenio_remocao_id = convenio_id
            self.erro_remocao = ""

    @rx.event
    def cancelar_remocao(self):
        if not self.removendo_convenio:
            self.convenio_remocao_id = ""
            self.erro_remocao = ""

    @rx.event
    async def remover(self):
        if self.removendo_convenio or not self.convenio_remocao_id:
            return
        token = (await self.get_state(AuthState)).obter_token()
        if not token:
            self.convenio_remocao_id = ""
            yield AuthState.sessao_expirada
            return
        try:
            identificador = int(self.convenio_remocao_id)
        except ValueError:
            self.erro_remocao = "O ID do convênio não é válido. Atualize a lista e tente novamente."
            self.convenio_remocao_id = ""
            return
        self.removendo_convenio = True
        self.erro_remocao = ""
        yield
        try:
            await api.request("DELETE", self.ENDPOINT, token=token, json={"convenio_id": identificador})
        except api.SessionExpired:
            self.removendo_convenio = False
            self.convenio_remocao_id = ""
            yield AuthState.sessao_expirada
            return
        except api.ApiError as error:
            self.removendo_convenio = False
            if error.status == 409:
                self.erro_remocao = "Este convênio não pode ser excluído porque há agendamentos vinculados."
            else:
                self.erro_remocao = mensagem_erro(error, "excluir")
            self.convenio_remocao_id = ""
            return
        self.removendo_convenio = False
        self.convenio_remocao_id = ""
        self.carregando = True
        yield rx.toast.success("Convênio excluído.", position="top-center")
        evento = await self._buscar()
        if evento:
            yield evento


def convenios_table_header() -> rx.Component:
    return rx.hstack(
        cabecalho_coluna("Nome", "40%"),
        cabecalho_coluna("Código", "20%"),
        cabecalho_coluna("Desconto", "20%"),
        cabecalho_coluna("Ações", "20%"),
        width="100%",
        padding="0 0.5rem 0.75rem",
        display=rx.breakpoints(initial="none", md="flex"),
        border_bottom="1px solid #E6F2F7",
        box_sizing="border-box",
    )


def convenio_row(convenio: rx.Var[dict[str, str]]) -> rx.Component:
    return rx.hstack(
        celula_responsiva("Nome", rx.text(convenio["name"], color="#05589F", font_family="Inter", font_weight="600"), "40%"),
        celula_responsiva("Código", rx.text(convenio["codigo"], color="#6A9ECC", font_family="Inter", font_size="0.9rem"), "20%"),
        celula_responsiva("Desconto", rx.text(convenio["desconto"], color="#6A9ECC", font_family="Inter", font_size="0.9rem"), "20%"),
        celula_responsiva(
            "Ações",
            rx.hstack(
                rx.button("Editar", on_click=ConvenioState.editar(convenio["id"]), variant="outline", color="#05589F", border_radius="9999px", size="2", disabled=convenio["id"] == ""),
                rx.button("Excluir", on_click=ConvenioState.solicitar_remocao(convenio["id"]), variant="soft", color_scheme="red", border_radius="9999px", size="2", disabled=convenio["id"] == ""),
                spacing="2",
                flex_wrap="wrap",
            ),
            "20%",
        ),
        width="100%",
        padding="0.85rem 0.5rem",
        align="start",
        flex_wrap=rx.breakpoints(initial="wrap", md="nowrap"),
        spacing=rx.breakpoints(initial="2", md="0"),
        border_bottom="1px solid #EEF4F7",
        box_sizing="border-box",
    )


def novo_convenio_modal() -> rx.Component:
    return modal_cadastro(
        ConvenioState,
        rx.cond(ConvenioState.editando_id != "", "Editar Convênio", "Novo Convênio"),
        campo_input("Nome", ConvenioState.form_nome, ConvenioState.set_form_nome, obrigatorio=True, placeholder="Ex.: Unimed Nacional"),
        campo_input("Código", ConvenioState.form_codigo, ConvenioState.set_form_codigo, obrigatorio=True, placeholder="Código do convênio"),
        campo_input(
            "Desconto (%)",
            ConvenioState.form_desconto,
            ConvenioState.set_form_desconto,
            obrigatorio=True,
            placeholder="0 a 100",
            input_mode="decimal",
        ),
        texto_botao=rx.cond(ConvenioState.editando_id != "", "Atualizar convênio", "Salvar convênio"),
    )


def convenio() -> rx.Component:
    return rx.fragment(
        tela_cadastro(
            ConvenioState,
            ativo="Convênio",
            titulo="Convênio",
            busca="Buscar Convênio",
            botao="+ Novo Convênio",
            cabecalho=convenios_table_header(),
            linha=convenio_row,
            modal=novo_convenio_modal(),
        ),
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.dialog.title("Excluir convênio?", color="#05589F", font_family="Poppins"),
                    rx.dialog.description("A exclusão pode ser impedida se houver agendamentos vinculados.", color="#6A9ECC", font_family="Inter"),
                    rx.cond(
                        ConvenioState.erro_remocao != "",
                        rx.callout(ConvenioState.erro_remocao, icon="triangle_alert", color_scheme="red", width="100%"),
                    ),
                    rx.hstack(
                        rx.button("Cancelar", type="button", on_click=ConvenioState.cancelar_remocao, variant="outline", color="#05589F", border_radius="9999px"),
                        rx.button("Excluir", type="button", on_click=ConvenioState.remover, loading=ConvenioState.removendo_convenio, color_scheme="red", border_radius="9999px"),
                        justify="end",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                max_width="460px",
                border_radius="20px",
                padding="1.5rem",
            ),
            open=(ConvenioState.convenio_remocao_id != "") | (ConvenioState.erro_remocao != ""),
        ),
    )
