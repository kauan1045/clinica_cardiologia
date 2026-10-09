import reflex as rx

from rxconfig import config
from ProjetoCl_nicaCardiologia import api
from ProjetoCl_nicaCardiologia.auth import AuthState, require_auth
from ProjetoCl_nicaCardiologia.dashboard import dashboard
from ProjetoCl_nicaCardiologia.patients import patients
from ProjetoCl_nicaCardiologia.agendamento import agendamento
from ProjetoCl_nicaCardiologia.medicos import medicos
from ProjetoCl_nicaCardiologia.convenio import convenio
from ProjetoCl_nicaCardiologia.exames import exames
from ProjetoCl_nicaCardiologia.prescricoes import prescricoes


class State(rx.State):
    username: str = ""
    password: str = ""
    show_password: bool = False
    remember_me: str = rx.LocalStorage("false", name="cardiovida_remember_me")
    recuperacao_aberta: bool = False
    recuperacao_email: str = ""
    recuperacao_carregando: bool = False
    recuperacao_mensagem: str = ""
    recuperacao_erro: str = ""

    @rx.event
    def update_username(self, value: str):
        self.username = value

    @rx.event
    def update_password(self, value: str):
        self.password = value

    @rx.event
    def toggle_password(self):
        self.show_password = not self.show_password

    @rx.event
    def toggle_remember_me(self):
        self.remember_me = "false" if self.remember_me == "true" else "true"

    @rx.event
    def abrir_recuperacao(self):
        self.recuperacao_aberta = True
        self.recuperacao_email = self.username.strip()
        self.recuperacao_mensagem = ""
        self.recuperacao_erro = ""

    @rx.event
    def fechar_recuperacao(self):
        if not self.recuperacao_carregando:
            self.recuperacao_aberta = False
            self.recuperacao_erro = ""

    @rx.event
    def atualizar_email_recuperacao(self, valor: str):
        self.recuperacao_email = valor
        self.recuperacao_mensagem = ""
        self.recuperacao_erro = ""

    @rx.event
    async def solicitar_recuperacao(self):
        email = self.recuperacao_email.strip()
        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            self.recuperacao_erro = "Informe um e-mail válido para receber o link."
            self.recuperacao_mensagem = ""
            return

        self.recuperacao_carregando = True
        self.recuperacao_erro = ""
        self.recuperacao_mensagem = ""
        yield
        try:
            await api.request_password_reset(email)
        except api.ApiError as error:
            self.recuperacao_erro = error.message
        else:
            self.recuperacao_mensagem = "Se o e-mail estiver cadastrado, o Xano enviará um link de redefinição."
        self.recuperacao_carregando = False


def index() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.vstack(
                    rx.image(
                        src="/bi_heart-pulse.svg",
                        alt="Ícone de coração com pulso CardioVida",
                        width="112px",
                        height="auto",
                    ),
                    rx.heading(
                        "CardioVida",
                        color="#05589F",
                        font_family="Poppins",
                        font_size={"initial": "3rem", "md": "3rem"},
                        font_weight="600",
                        line_height="1",
                    ),
                    rx.text(
                        "Clínica de Cardiologia",
                        color="#05589F",
                        font_family="Inter",
                        font_size={"initial": "1rem", "md": "1.125rem"},
                        font_weight="600",
                        text_align="center",
                    ),
                    rx.text(
                        "Cuidando do seu coração em todas as fases da sua vida.",
                        color="#05589F",
                        font_family="Inter",
                        font_size={"initial": "1rem", "md": "1.125rem"},
                        font_weight="600",
                        line_height="1.5",
                        text_align="center",
                        max_width="300px",
                        margin_top="1.5rem",
                    ),
                    spacing="2",
                    align="center",
                    justify="center",
                    position="relative",
                    z_index="1",
                    width="100%",
                    height="100%",
                    padding="2rem",
                ),
                position="relative",
                overflow="hidden",
                width=rx.breakpoints(initial="100%", md="40%"),
                box_sizing="border-box",
                flex_shrink="0",
                min_height=rx.breakpoints(initial="300px", md="calc(100vh - 2rem)"),
                background="#A7D8F0",
                background_image="url('/bottom-shapes.svg')",
                background_position="bottom",
                background_size="100% 300px",
                background_repeat="no-repeat",
                spacing="0",
                align="stretch",
            ),
            rx.vstack(
                rx.vstack(
                    rx.heading(
                        "Bem-Vindo(a)!",
                        color="#05589F",
                        font_family="Poppins",
                        font_size={"initial": "2rem", "md": "2rem"},
                        font_weight="600",
                        line_height="1.1",
                        text_align="center",
                    ),
                    rx.text(
                        "Acesse o sistema da CardioVida e gerencie todos os atendimentos da Clínica.",
                        color="#6A9ECC",
                        font_family="Inter",
                        font_size={"initial": "1rem", "md": "1.125rem"},
                        font_weight="600",
                        line_height="1.5",
                        text_align="center",
                        max_width="370px",
                    ),
                    spacing="3",
                    align="center",
                    width="100%",
                    max_width="480px",
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.button(
                        rx.color_mode_cond("Tema escuro", "Tema claro"),
                        on_click=rx.toggle_color_mode,
                        aria_label="Alternar tema claro ou escuro",
                        size="2",
                        variant="soft",
                        color_scheme="blue",
                        border_radius="9999px",
                    ),
                    width="100%",
                    max_width="480px",
                ),
                rx.form(
                    rx.vstack(
                        rx.vstack(
                            rx.hstack(
                                rx.image(
                                    src="/user.svg",
                                    alt="",
                                    width="24px",
                                    height="24px",
                                ),
                                rx.input(
                                    name="username",
                                    type="email",
                                    placeholder="E-mail",
                                    value=State.username,
                                    on_change=State.update_username,
                                    variant="soft",
                                    border="none",
                                    outline="none",
                                    padding="0",
                                    flex="1",
                                    color="#05589F",
                                    font_family="Inter",
                                    font_size="1.125rem",
                                    font_weight="600",
                                ),
                                width="100%",
                                align="center",
                                spacing="3",
                                padding="0.6rem 1rem",
                                border="1px solid #6A9ECC",
                                border_radius="9999px",
                                background="#FFFFFF",
                            ),
                            align="stretch",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.image(
                                    src="/lock.svg",
                                    alt="",
                                    width="24px",
                                    height="24px",
                                ),
                                rx.input(
                                    name="password",
                                    type=rx.cond(State.show_password, "text", "password"),
                                    placeholder="Senha",
                                    value=State.password,
                                    on_change=State.update_password,
                                    variant="soft",
                                    border="none",
                                    outline="none",
                                    padding="0",
                                    flex="1",
                                    color="#05589F",
                                    font_family="Inter",
                                    font_size="1.125rem",
                                    font_weight="600",
                                ),
                                rx.button(
                                    rx.image(
                                        src=rx.cond(State.show_password, "/eye-off.svg", "/eye.svg"),
                                        alt=rx.cond(State.show_password, "Ocultar senha", "Mostrar senha"),
                                        width="24px",
                                        height="24px",
                                    ),
                                    type="button",
                                    on_click=State.toggle_password,
                                    variant="ghost",
                                    padding="0",
                                    min_width="24px",
                                    height="24px",
                                ),
                                width="100%",
                                align="center",
                                spacing="3",
                                padding="0.6rem 1rem",
                                border="1px solid #6A9ECC",
                                border_radius="9999px",
                                background="#FFFFFF",
                            ),
                            align="stretch",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.checkbox(
                                checked=State.remember_me == "true",
                                on_click=State.toggle_remember_me,
                                color_scheme="green",
                            ),
                            rx.button(
                                "Lembrar-me",
                                type="button",
                                variant="ghost",
                                on_click=State.toggle_remember_me,
                                padding="0",
                                color="#6A9ECC",
                                font_family="Inter",
                                font_size="1rem",
                                font_weight="600",
                                cursor="pointer",
                            ),
                            width="fit-content",
                            align="center",
                        ),
                        rx.button(
                            "Entrar",
                            type="submit",
                            width="100%",
                            size="3",
                            background="#05589F",
                            color="#FFFFFF",
                            font_family="Inter",
                            font_size="1.125rem",
                            font_weight="600",
                            border_radius="9999px",
                            height="52px",
                            loading=AuthState.loading,
                            _hover={"background": "#4A7A69"},
                        ),
                        rx.button(
                            "Esqueceu sua senha?",
                            type="button",
                            on_click=State.abrir_recuperacao,
                            variant="ghost",
                            color="#6A9ECC",
                            font_family="Inter",
                            font_size="1rem",
                            font_weight="600",
                            text_decoration="underline",
                        ),
                        rx.cond(
                            State.recuperacao_aberta,
                            rx.vstack(
                                rx.heading("Recuperar acesso", size="4", color="#05589F"),
                                rx.text(
                                    "Informe o e-mail da sua conta para receber um link de redefinição.",
                                    color="#6A9ECC",
                                    font_family="Inter",
                                    font_size="0.9rem",
                                ),
                                rx.input(
                                    type="email",
                                    value=State.recuperacao_email,
                                    on_change=State.atualizar_email_recuperacao,
                                    placeholder="seu@email.com",
                                    aria_label="E-mail para recuperação de senha",
                                    width="100%",
                                    border="1px solid #A7D8F0",
                                    border_radius="12px",
                                    background="#FFFFFF",
                                    color="#05589F",
                                    padding="0.75rem 1rem",
                                ),
                                rx.cond(
                                    State.recuperacao_mensagem != "",
                                    rx.text(State.recuperacao_mensagem, color="#34785F", role="status"),
                                ),
                                rx.cond(
                                    State.recuperacao_erro != "",
                                    rx.text(State.recuperacao_erro, color="#ED6D6D", role="alert"),
                                ),
                                rx.hstack(
                                    rx.button(
                                        "Cancelar",
                                        type="button",
                                        on_click=State.fechar_recuperacao,
                                        variant="soft",
                                        color="#05589F",
                                    ),
                                    rx.button(
                                        rx.cond(State.recuperacao_carregando, "Enviando...", "Enviar link"),
                                        type="button",
                                        on_click=State.solicitar_recuperacao,
                                        loading=State.recuperacao_carregando,
                                        disabled=State.recuperacao_carregando,
                                        background="#05589F",
                                        color="#FFFFFF",
                                        border_radius="9999px",
                                    ),
                                    width="100%",
                                    justify="end",
                                    spacing="3",
                                ),
                                width="100%",
                                align="stretch",
                                spacing="3",
                                padding="1rem",
                                border="1px solid #D8EDF7",
                                border_radius="16px",
                                background="#F8FCFD",
                                id="recuperacao",
                            ),
                        ),
                        rx.cond(
                            AuthState.login_error != "",
                            rx.text(
                                AuthState.login_error,
                                color="#ED6D6D",
                                font_family="Inter",
                                font_size="1rem",
                                font_weight="600",
                                role="alert",
                            ),
                        ),
                        spacing="4",
                        align="stretch",
                        width="100%",
                    ),
                    on_submit=AuthState.entrar,
                    reset_on_submit=False,
                    width="100%",
                    max_width="480px",
                ),
                spacing="6",
                align="center",
                justify="center",
                width=rx.breakpoints(initial="100%", md="60%"),
                box_sizing="border-box",
                flex_shrink="0",
                min_height=rx.breakpoints(initial="auto", md="calc(100vh - 2rem)"),
                padding=rx.breakpoints(initial="2.5rem 1.25rem", md="3rem 2.25rem", lg="3rem 4rem"),
                background="#FFFFFF",
            ),
            width="100%",
            min_height=rx.breakpoints(initial="auto", md="calc(100vh - 2rem)"),
            spacing="0",
            align="stretch",
            flex_direction=rx.breakpoints(initial="column", md="row"),
            border_radius="26px",
            overflow="hidden",
            box_shadow="0 12px 36px rgba(5,88,159,0.10)",
        ),
        width="100%",
        min_height="100vh",
        padding=rx.breakpoints(initial="0.75rem", md="1rem"),
        box_sizing="border-box",
        background=rx.color_mode_cond("#F0F7FA", "#0B1220"),
        font_family="Inter",
    )


app = rx.App(stylesheets=config.stylesheets)
app.add_page(index, on_load=AuthState.verificar_login)
for page, route in (
    (dashboard, "/dashboard"),
    (patients, "/pacientes"),
    (agendamento, "/agendamento"),
    (prescricoes, "/prescricoes"),
    (medicos, "/medicos"),
    (convenio, "/convenio"),
    (exames, "/exames"),
):
    app.add_page(require_auth(page, route), route=route, on_load=AuthState.verificar_sessao)
