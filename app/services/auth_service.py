"""Service Layer — Autenticação e onboarding de empresa.

Concentra a regra de negócio do Módulo 1. A UI (páginas Streamlit) só
chama estes métodos, sem conhecer detalhes do Supabase.
"""
from __future__ import annotations

import streamlit as st
from supabase import Client

from app.database.supabase_client import SESSION_KEY


class AuthError(Exception):
    """Erro de autenticação tratável e exibível ao usuário."""


class AuthService:
    def __init__(self, client: Client) -> None:
        self.client = client

    # ---------------- Sessão ----------------
    def _salvar_sessao(self, session) -> None:
        st.session_state[SESSION_KEY] = {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        }

    def login(self, email: str, senha: str) -> None:
        try:
            resp = self.client.auth.sign_in_with_password(
                {"email": email.strip(), "password": senha}
            )
        except Exception as exc:  # supabase lança AuthApiError
            raise AuthError("E-mail ou senha inválidos.") from exc
        if not resp.session:
            raise AuthError("Não foi possível iniciar a sessão.")
        self._salvar_sessao(resp.session)

    def logout(self) -> None:
        try:
            self.client.auth.sign_out()
        except Exception:
            pass
        for chave in (SESSION_KEY, "perfil", "empresa"):
            st.session_state.pop(chave, None)

    def recuperar_senha(self, email: str) -> None:
        try:
            self.client.auth.reset_password_email(email.strip())
        except Exception as exc:
            raise AuthError("Não foi possível enviar o e-mail de recuperação.") from exc

    # ---------------- Onboarding ----------------
    def cadastrar_empresa(
        self,
        *,
        email: str,
        senha: str,
        nome_admin: str,
        nome_fantasia: str,
        razao_social: str = "",
        cnpj: str = "",
        telefone: str = "",
        whatsapp: str = "",
    ) -> None:
        """Cria o usuário no Auth, autentica e registra a empresa via RPC."""
        try:
            self.client.auth.sign_up({"email": email.strip(), "password": senha})
        except Exception as exc:
            raise AuthError("Não foi possível criar a conta (e-mail já usado?).") from exc

        # Em projetos sem confirmação de e-mail o login já funciona em seguida.
        self.login(email, senha)

        try:
            self.client.rpc(
                "registrar_empresa",
                {
                    "p_nome_fantasia": nome_fantasia,
                    "p_razao_social": razao_social or None,
                    "p_cnpj": cnpj or None,
                    "p_telefone": telefone or None,
                    "p_whatsapp": whatsapp or None,
                    "p_nome_admin": nome_admin,
                },
            ).execute()
        except Exception as exc:
            raise AuthError(f"Conta criada, mas falhou ao registrar a empresa: {exc}") from exc

    # ---------------- Contexto ----------------
    def usuario_logado(self) -> bool:
        return SESSION_KEY in st.session_state

    def perfil_atual(self) -> dict | None:
        """Retorna o registro de `usuarios` da pessoa logada (com empresa)."""
        if "perfil" in st.session_state:
            return st.session_state["perfil"]
        dados = (
            self.client.table("usuarios")
            .select("*, empresas(*)")
            .limit(1)
            .execute()
            .data
        )
        if dados:
            st.session_state["perfil"] = dados[0]
            return dados[0]
        return None
