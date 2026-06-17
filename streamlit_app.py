"""EspetariaOS — Ponto de entrada do Streamlit.

Execução: `streamlit run streamlit_app.py`

Esta é a casca da Etapa 1: autenticação funcional + navegação. Cada item
do menu corresponde a um módulo que será implementado nas próximas etapas.
"""
from __future__ import annotations

import streamlit as st

from app.database.supabase_client import get_client
from app.pages.login import render_login
from app.services.auth_service import AuthService

st.set_page_config(
    page_title="EspetariaOS",
    page_icon="🍢",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_app(auth: AuthService) -> None:
    perfil = auth.perfil_atual()
    if not perfil:
        st.warning("Sua conta ainda não está vinculada a uma empresa.")
        if st.button("Sair"):
            auth.logout()
            st.rerun()
        return

    empresa = perfil.get("empresas") or {}
    eh_admin = perfil.get("perfil") == "administrador"

    with st.sidebar:
        st.markdown(f"### 🍢 {empresa.get('nome_fantasia', 'Minha Espetaria')}")
        st.caption(f"{perfil.get('nome')} · {perfil.get('perfil')}")
        st.divider()

        # Operador foca no PDV; admin vê tudo (controle de permissões — Módulo 2)
        itens = ["PDV", "Produção do dia"]
        if eh_admin:
            itens += ["Dashboard", "Produtos", "Estoque", "Relatórios", "Configurações"]
        escolha = st.radio("Navegação", itens, label_visibility="collapsed")

        st.divider()
        if st.button("Sair", use_container_width=True):
            auth.logout()
            st.rerun()

    st.header(escolha)
    st.info(
        f"O módulo **{escolha}** será implementado na próxima etapa. "
        "A fundação (banco multi-tenant, autenticação, arquitetura) já está pronta "
        "e validada."
    )


def main() -> None:
    auth = AuthService(get_client())
    if auth.usuario_logado():
        render_app(auth)
    else:
        render_login()


if __name__ == "__main__":
    main()
