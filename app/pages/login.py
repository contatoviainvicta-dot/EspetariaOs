"""Tela de autenticação (Módulo 1): login, cadastro e recuperação."""
from __future__ import annotations

import streamlit as st

from app.database.supabase_client import get_client
from app.services.auth_service import AuthError, AuthService


def render_login() -> None:
    st.markdown(
        "<h1 style='text-align:center;margin-bottom:0'>🍢 EspetariaOS</h1>"
        "<p style='text-align:center;color:#888'>Gestão e PDV para espetarias</p>",
        unsafe_allow_html=True,
    )
    auth = AuthService(get_client())

    aba_login, aba_cadastro, aba_senha = st.tabs(
        ["Entrar", "Criar conta da empresa", "Esqueci a senha"]
    )

    with aba_login:
        email = st.text_input("E-mail", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar", type="primary", use_container_width=True):
            try:
                auth.login(email, senha)
                st.rerun()
            except AuthError as e:
                st.error(str(e))

    with aba_cadastro:
        st.caption("Crie a conta do dono (administrador) e cadastre o estabelecimento.")
        nome_fantasia = st.text_input("Nome da espetaria *")
        nome_admin = st.text_input("Seu nome *")
        col1, col2 = st.columns(2)
        email_c = col1.text_input("E-mail *", key="cad_email")
        senha_c = col2.text_input("Senha *", type="password", key="cad_senha")
        col3, col4 = st.columns(2)
        telefone = col3.text_input("Telefone")
        whatsapp = col4.text_input("WhatsApp")
        with st.expander("Dados fiscais (opcional)"):
            razao = st.text_input("Razão social")
            cnpj = st.text_input("CNPJ")
        if st.button("Criar conta", type="primary", use_container_width=True):
            if not (nome_fantasia and nome_admin and email_c and senha_c):
                st.error("Preencha os campos obrigatórios (*).")
            else:
                try:
                    auth.cadastrar_empresa(
                        email=email_c,
                        senha=senha_c,
                        nome_admin=nome_admin,
                        nome_fantasia=nome_fantasia,
                        razao_social=razao,
                        cnpj=cnpj,
                        telefone=telefone,
                        whatsapp=whatsapp,
                    )
                    st.success("Conta criada! Entrando...")
                    st.rerun()
                except AuthError as e:
                    st.error(str(e))

    with aba_senha:
        email_r = st.text_input("E-mail da conta", key="rec_email")
        if st.button("Enviar link de recuperação", use_container_width=True):
            try:
                auth.recuperar_senha(email_r)
                st.success("Se o e-mail existir, enviamos as instruções.")
            except AuthError as e:
                st.error(str(e))
