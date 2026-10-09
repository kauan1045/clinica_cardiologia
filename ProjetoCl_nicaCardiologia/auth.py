import functools
import unicodedata
from typing import Any, Callable

import reflex as rx

from ProjetoCl_nicaCardiologia import api


NO_PERMISSION_MESSAGE = "Seu perfil não tem permissão para acessar o CardioVida. Contate o administrador."

ROTAS_ADMINISTRATIVAS = ("/dashboard", "/pacientes", "/agendamento", "/prescricoes", "/medicos", "/convenio", "/exames")

# Permissões por perfil: único lugar a alterar para mudar o acesso.
# - rotas: telas autenticadas que o perfil pode abrir (e que aparecem no menu);
# - inicial: tela aberta após o login ou ao tentar abrir uma rota não permitida;
# - acoes: permissões de ação, verificadas com `tem_permissao` / `AuthState.pode_gerenciar_agendamento`.
PERMISSOES: dict[str, dict[str, Any]] = {
    "administrador": {
        "rotas": ROTAS_ADMINISTRATIVAS,
        "inicial": "/dashboard",
        "acoes": ("agendamento:consultar", "agendamento:gerenciar", "paciente:gerenciar", "medico:gerenciar", "prescricao:visualizar", "prescricao:email"),
    },
    "secretaria": {
        "rotas": ("/pacientes", "/agendamento", "/prescricoes"),
        "inicial": "/agendamento",
        "acoes": ("agendamento:consultar", "agendamento:gerenciar", "paciente:gerenciar", "prescricao:visualizar", "prescricao:email"),
    },
    "medico": {
        "rotas": ("/agendamento", "/prescricoes"),
        "inicial": "/agendamento",
        "acoes": ("agendamento:consultar", "prescricao:emitir"),
    },
}


def normalizar_perfil(role: Any) -> str:
    """Compara perfis sem diferenciar maiúsculas/minúsculas nem acentos ("Médico" == "medico")."""
    texto = unicodedata.normalize("NFKD", str(role or "")).encode("ascii", "ignore").decode()
    return texto.strip().casefold()


def rotas_do_perfil(perfil: str) -> tuple[str, ...]:
    return tuple(PERMISSOES.get(perfil, {}).get("rotas", ()))


def rota_inicial(perfil: str) -> str:
    return str(PERMISSOES.get(perfil, {}).get("inicial", "/"))


def tem_permissao(perfil: str, acao: str) -> bool:
    return acao in PERMISSOES.get(perfil, {}).get("acoes", ())


def _medico_id(user: dict[str, Any]) -> str:
    """Id do médico vinculado: o Xano pode enviar o id ou o objeto do médico."""
    medico = user.get("medico")
    if isinstance(medico, dict):
        medico = medico.get("id")
    if medico is None or isinstance(medico, bool) or str(medico).strip() == "":
        return ""
    return str(medico).strip()


def _normalizar_rota(path: str) -> str:
    return "/" + path.strip("/") if path.strip("/") else "/"


class AuthState(rx.State):
    token: str = rx.LocalStorage("", name="cardiovida_token")
    session_token: str = rx.SessionStorage("", name="cardiovida_session_token")
    # Perfil e médico vinculado ficam em cache para quando `/auth/me` não devolve `medico`;
    # nenhum deles autoriza chamadas sem um token ativo.
    perfil: str = rx.LocalStorage("", name="cardiovida_perfil")
    medico_id: str = rx.LocalStorage("", name="cardiovida_medico_id")
    user: dict[str, Any] = {}
    login_error: str = ""
    loading: bool = False
    session_ok: bool = False
    validated_route: str = ""

    @rx.var
    def user_display_name(self) -> str:
        return str(self.user.get("name") or self.user.get("email") or "Usuário")

    @rx.var
    def rotas_permitidas(self) -> list[str]:
        return list(rotas_do_perfil(self.perfil))

    @rx.var
    def has_active_token(self) -> bool:
        return bool(self.token or self.session_token)

    @rx.var
    def pode_gerenciar_agendamento(self) -> bool:
        """Criar, editar, alterar status ou excluir agendamentos (médico só consulta)."""
        return tem_permissao(self.perfil, "agendamento:gerenciar")

    def obter_token(self) -> str:
        """Retorna o token ativo, armazenado de acordo com a opção Lembrar-me."""
        return self.token or self.session_token

    @rx.event
    async def entrar(self, form_data: dict[str, Any]):
        email = str(form_data.get("username", "")).strip()
        password = str(form_data.get("password", ""))
        if not email or not password:
            self.login_error = "Preencha Usuário e senha para continuar."
            return

        self.loading = True
        self.login_error = ""
        yield
        try:
            token, user = await api.login(email, password)
            if user is None:
                # Sem o perfil não é possível decidir o acesso; a falha é exibida no Login.
                user = await api.get_me(token)
        except api.ApiError as error:
            self.loading = False
            self.login_error = error.message
            return

        perfil = normalizar_perfil(user.get("role"))
        if perfil not in PERMISSOES:
            self.loading = False
            self.login_error = NO_PERMISSION_MESSAGE
            return

        from ProjetoCl_nicaCardiologia.ProjetoCl_nicaCardiologia import State

        login_state = await self.get_state(State)
        lembrar = login_state.remember_me == "true"
        await self._limpar_formulario_login()
        self.token = token if lembrar else ""
        self.session_token = "" if lembrar else token
        self.user = user
        self.perfil = perfil
        self.medico_id = _medico_id(user)
        self.session_ok = True
        self.validated_route = ""
        self.loading = False
        yield rx.redirect(rota_inicial(perfil))

    @rx.event
    async def verificar_sessao(self):
        # A rota começa bloqueada. Só libera o conteúdo depois de confirmar o token
        # diretamente no Xano nesta navegação.
        self.session_ok = False
        self.validated_route = ""
        self.user = {}
        token = self.obter_token()
        if not token:
            self._limpar_sessao()
            return rx.redirect("/")
        try:
            user = await api.get_me(token)
        except api.SessionExpired:
            return self._expirar_sessao()
        except api.ApiError:
            # Falha ao confirmar o token nunca pode autorizar uma página protegida.
            return self._falha_validacao_sessao()

        self.user = user
        self.perfil = normalizar_perfil(user.get("role"))
        if "medico" in user:
            self.medico_id = _medico_id(user)

        if self.perfil not in PERMISSOES:
            return self._negar_acesso()
        rota = _normalizar_rota(self.router.url.path)
        if rota not in rotas_do_perfil(self.perfil):
            return rx.redirect(rota_inicial(self.perfil))
        self.session_ok = True
        self.validated_route = rota

    @rx.event
    async def verificar_login(self):
        """No Login: uma sessão só é reaproveitada depois de validada no Xano."""
        self.session_ok = False
        self.validated_route = ""
        token = self.obter_token()
        if not token:
            self._limpar_sessao()
            return
        try:
            user = await api.get_me(token)
        except api.SessionExpired:
            return self._expirar_sessao()
        except api.ApiError:
            return self._falha_validacao_sessao()
        self.user = user
        perfil = normalizar_perfil(user.get("role"))
        self.perfil = perfil
        if "medico" in user:
            self.medico_id = _medico_id(user)
        if perfil not in PERMISSOES:
            return self._negar_acesso()
        if perfil == "medico":
            return rx.redirect(rota_inicial("medico"))

    @rx.event
    def sessao_expirada(self):
        return self._expirar_sessao()

    @rx.event
    async def sair(self):
        await self._limpar_formulario_login()
        self._limpar_sessao()
        self.login_error = ""
        return rx.redirect("/")

    def _expirar_sessao(self):
        self._limpar_sessao()
        self.login_error = api.SESSION_EXPIRED_MESSAGE
        return rx.redirect("/")

    def _falha_validacao_sessao(self):
        self._limpar_sessao()
        self.login_error = "Não foi possível validar sua sessão. Entre novamente."
        return rx.redirect("/")

    def _negar_acesso(self):
        self._limpar_sessao()
        self.login_error = NO_PERMISSION_MESSAGE
        return rx.redirect("/")

    def _limpar_sessao(self):
        self.token = ""
        self.session_token = ""
        self.perfil = ""
        self.medico_id = ""
        self.user = {}
        self.session_ok = False
        self.validated_route = ""

    async def _limpar_formulario_login(self):
        # Importado aqui para evitar import circular (o app importa o Sidebar, que usa este estado).
        from ProjetoCl_nicaCardiologia.ProjetoCl_nicaCardiologia import State

        state = await self.get_state(State)
        state.username = ""
        state.password = ""
        state.show_password = False


def require_auth(page: Callable[[], rx.Component], rota: str) -> Callable[[], rx.Component]:
    """Só renderiza a tela com sessão verificada e rota permitida ao perfil (evita exibir a tela antes do redirecionamento)."""

    @functools.wraps(page)
    def protected() -> rx.Component:
        return rx.cond(
            AuthState.session_ok
            & AuthState.has_active_token
            & (AuthState.validated_route == rota)
            & AuthState.rotas_permitidas.contains(rota),
            page(),
            rx.box(min_height="100vh", width="100%", background="#F8FCFD"),
        )

    return protected
